import httpx
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.api.auth import (
    create_jwt,
    exchange_code_for_token,
    fetch_github_user,
    generate_state,
    get_current_user,
)
from src.api.errors import ApiError
from src.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"


class GitHubLoginResponse(BaseModel):
    authorize_url: str
    state: str


class GitHubCallbackRequest(BaseModel):
    code: str
    state: str


class GitHubCallbackResponse(BaseModel):
    token: str
    user: dict


class MeResponse(BaseModel):
    login: str
    avatar_url: str
    name: str


class RepoItem(BaseModel):
    full_name: str
    html_url: str
    description: str | None = None
    private: bool = False
    language: str | None = None
    updated_at: str


@router.get("/github/login")
async def github_login() -> GitHubLoginResponse:
    settings = get_settings()
    if not settings.github_client_id:
        raise ApiError(
            status_code=500,
            code="OAUTH_NOT_CONFIGURED",
            message="GitHub OAuth is not configured",
        )
    state = generate_state()
    authorize_url = (
        f"{GITHUB_AUTHORIZE_URL}"
        f"?client_id={settings.github_client_id}"
        f"&scope=repo"
        f"&state={state}"
    )
    return GitHubLoginResponse(authorize_url=authorize_url, state=state)


@router.post("/github/callback")
async def github_callback(payload: GitHubCallbackRequest) -> GitHubCallbackResponse:
    try:
        github_token = await exchange_code_for_token(payload.code)
    except Exception as exc:
        logger.exception("github_token_exchange_failed")
        raise ApiError(
            status_code=400,
            code="TOKEN_EXCHANGE_FAILED",
            message=f"Failed to exchange code for token: {exc}",
        ) from exc

    try:
        user_info = await fetch_github_user(github_token)
    except Exception as exc:
        logger.exception("github_user_fetch_failed")
        raise ApiError(
            status_code=400,
            code="USER_FETCH_FAILED",
            message="Failed to fetch GitHub user info",
        ) from exc

    token = create_jwt(github_token, user_info)
    logger.info("user_authenticated", login=user_info["login"])
    return GitHubCallbackResponse(token=token, user=user_info)


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)) -> MeResponse:  # noqa: B008
    return MeResponse(
        login=user["login"],
        avatar_url=user["avatar_url"],
        name=user["name"],
    )


@router.get("/repos")
async def list_user_repos(
    user: dict = Depends(get_current_user),  # noqa: B008
    page: int = Query(default=1, ge=1),  # noqa: B008
    per_page: int = Query(default=30, ge=1, le=100),
) -> list[RepoItem]:
    github_token = user["github_token"]
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
            },
            params={
                "sort": "updated",
                "direction": "desc",
                "per_page": per_page,
                "page": page,
                "type": "all",
            },
        )
        response.raise_for_status()
        repos = response.json()

    return [
        RepoItem(
            full_name=r["full_name"],
            html_url=r["html_url"],
            description=r.get("description"),
            private=r.get("private", False),
            language=r.get("language"),
            updated_at=r.get("updated_at", ""),
        )
        for r in repos
    ]
