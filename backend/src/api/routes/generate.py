import re
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, Request

from src.api.auth import get_current_user_optional
from src.api.errors import ApiError
from src.models.schemas import GenerateAcceptedResponse, GenerateOptions, GenerateRequest, JobStatusResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["generate"])
GITHUB_URL_PATTERN = re.compile(r"^https://github\.com/[^/]+/[^/]+/?$")


@router.post("/generate", status_code=202)
async def generate_docs(
    payload: GenerateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    user: Optional[dict] = Depends(get_current_user_optional),
) -> GenerateAcceptedResponse:
    # Resolve the GitHub token from JWT (if signed in)
    github_token: Optional[str] = None
    if user:
        github_token = user["github_token"]

    # DEBUG
    print("\n========== /api/v1/generate called ==========")
    print(f"github_url: {payload.github_url}")
    print(f"github_token: {'present' if github_token else 'null'}")
    print("==============================================\n")

    if not GITHUB_URL_PATTERN.match(payload.github_url):
        raise ApiError(status_code=400, code="INVALID_URL", message="Invalid GitHub repository URL")

    github_tool = request.app.state.github_tool
    if github_token:
        github_tool = github_tool.with_token(github_token)

    is_accessible, status_code = await github_tool.check_repo_accessibility(payload.github_url)
    if not is_accessible and status_code == 404:
        raise ApiError(status_code=404, code="REPO_NOT_FOUND", message="Repository not found")
    if not is_accessible and status_code == 403:
        raise ApiError(
            status_code=403,
            code="REPO_PRIVATE",
            message="Repository is private. Sign in with GitHub to access.",
        )
    if not is_accessible:
        raise ApiError(status_code=400, code="REPO_UNREACHABLE", message="Repository is not accessible")

    options = GenerateOptions()
    job_id = str(uuid4())
    record = request.app.state.job_store.create_job(job_id, payload.github_url, options)

    logger.info(
        "job_created",
        job_id=job_id,
        repo=payload.github_url,
        authenticated=github_token is not None,
    )

    background_tasks.add_task(
        request.app.state.run_generation,
        job_id,
        payload.github_url,
        options,
        github_token,
    )

    return GenerateAcceptedResponse(job_id=record.job_id, status=record.status, created_at=record.created_at)


@router.get("/generate/{job_id}")
async def get_job_status(job_id: str, request: Request) -> JobStatusResponse:
    job = request.app.state.job_store.get_job(job_id)
    if not job:
        raise ApiError(status_code=404, code="JOB_NOT_FOUND", message="Job not found")
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        result=job.result,
        error=job.error,
        created_at=job.created_at,
    )
