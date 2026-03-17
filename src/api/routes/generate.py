import re
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Request

from src.adk.tools.github_tool import GithubTool
from src.api.auth import get_current_user_optional
from src.api.errors import ApiError
from src.models.schemas import GenerateAcceptedResponse, GenerateRequest, JobStatusResponse

router = APIRouter(prefix="/api/v1", tags=["generate"])
GITHUB_URL_PATTERN = re.compile(r"^https://github\.com/[^/]+/[^/]+/?$")


@router.post("/generate", status_code=202)
async def generate_docs(
    payload: GenerateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
) -> GenerateAcceptedResponse:
    if not GITHUB_URL_PATTERN.match(payload.github_url):
        raise ApiError(status_code=400, code="INVALID_URL", message="Invalid GitHub repository URL")

    user = await get_current_user_optional(request)
    github_token = user["github_token"] if user else None

    settings = request.app.state.settings
    github_tool = GithubTool(
        token=github_token,
        timeout_seconds=settings.github_api_timeout_seconds,
        retry_attempts=settings.github_retry_attempts,
        max_file_size_bytes=settings.max_file_size_bytes,
    )

    is_accessible, status_code = await github_tool.check_repo_accessibility(payload.github_url)
    if not is_accessible and status_code == 404:
        raise ApiError(status_code=404, code="REPO_NOT_FOUND", message="Repository not found")
    if not is_accessible and status_code == 403:
        raise ApiError(status_code=403, code="REPO_PRIVATE", message="Repository is private")
    if not is_accessible:
        raise ApiError(status_code=400, code="REPO_UNREACHABLE", message="Repository is not accessible")

    job_id = str(uuid4())
    record = request.app.state.job_store.create_job(job_id, payload.github_url, payload.options)

    background_tasks.add_task(
        request.app.state.run_generation,
        job_id,
        payload.github_url,
        payload.options,
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
