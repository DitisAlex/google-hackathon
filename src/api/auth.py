import secrets
from datetime import UTC, datetime, timedelta

import httpx
import jwt
from fastapi import Request

from src.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"


async def exchange_code_for_token(code: str) -> str:
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_TOKEN_URL,
            json={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
        logger.info("github_token_response", data={k: v for k, v in data.items() if k != "access_token"})
        if "error" in data:
            raise ValueError(f"GitHub OAuth error: {data.get('error')}: {data.get('error_description', '')}")
        return data["access_token"]


async def fetch_github_user(token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GITHUB_USER_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        response.raise_for_status()
        data = response.json()
        return {
            "login": data["login"],
            "avatar_url": data.get("avatar_url", ""),
            "name": data.get("name", data["login"]),
        }


def create_jwt(github_token: str, user_info: dict) -> str:
    settings = get_settings()
    payload = {
        "github_token": github_token,
        "login": user_info["login"],
        "avatar_url": user_info["avatar_url"],
        "name": user_info["name"],
        "exp": datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])


def generate_state() -> str:
    return secrets.token_urlsafe(32)


async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        from src.api.errors import ApiError
        raise ApiError(status_code=401, code="UNAUTHORIZED", message="Missing or invalid authorization header")
    token = auth_header.removeprefix("Bearer ")
    try:
        return decode_jwt(token)
    except jwt.ExpiredSignatureError as exc:
        from src.api.errors import ApiError
        raise ApiError(status_code=401, code="TOKEN_EXPIRED", message="Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        from src.api.errors import ApiError
        raise ApiError(status_code=401, code="INVALID_TOKEN", message="Invalid token") from exc


async def get_current_user_optional(request: Request) -> dict | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.removeprefix("Bearer ")
    try:
        return decode_jwt(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
