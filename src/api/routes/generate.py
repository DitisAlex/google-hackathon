"""Documentation generation endpoints.

Data flow:
    ``POST /generate`` validates input, creates a job record, and schedules
    asynchronous ADK processing. ``GET /generate/{id}`` exposes persisted job
    state and outputs from ``JobStore``.
"""

import re
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Request

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
    """Validate a generation request and enqueue background processing.

    Args:
        payload: Validated request body with repository URL and options.
        request: FastAPI request containing shared app state dependencies.
        background_tasks: Task manager used to schedule async job execution.

    Returns:
        Acceptance response with job ID and initial status.

    Raises:
        ApiError: If URL format is invalid.

    Data flow:
        Performs lightweight validation, stores a queued job, and delegates
        generation to the background ``run_generation`` worker.
    """
    if not GITHUB_URL_PATTERN.match(payload.github_url):
        raise ApiError(status_code=400, code="INVALID_URL", message="Invalid GitHub repository URL")

    job_id = str(uuid4())
    record = request.app.state.job_store.create_job(job_id, payload.github_url, payload.options)

    background_tasks.add_task(
        request.app.state.run_generation,
        job_id,
        payload.github_url,
        payload.options,
    )

    return GenerateAcceptedResponse(job_id=record.job_id, status=record.status, created_at=record.created_at)


@router.get("/generate/{job_id}")
async def get_job_status(job_id: str, request: Request) -> JobStatusResponse:
    """Return the latest state for a previously submitted generation job.

    Args:
        job_id: Unique job identifier.
        request: FastAPI request containing application state.

    Returns:
        Polling response with status and optional result/error payload.

    Raises:
        ApiError: If the requested job ID does not exist.
    """
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
