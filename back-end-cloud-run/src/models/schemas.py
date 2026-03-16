"""Pydantic schema definitions shared by API, orchestration, and storage.

Data flow:
    Incoming request JSON is validated into request models, transformed into
    job records during processing, and serialized back into response models
    when clients poll job status.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    """Supported response serialization formats for completed jobs."""

    markdown = "markdown"
    json = "json"


class GenerateOptions(BaseModel):
    """Optional knobs that control repository analysis depth and output."""

    branch: Optional[str] = None
    max_depth: int = Field(default=5, ge=1, le=12)
    include_tests: bool = False
    output_format: OutputFormat = OutputFormat.markdown


class GenerateRequest(BaseModel):
    """Payload accepted by ``POST /api/v1/generate``."""

    github_url: str
    options: GenerateOptions = Field(default_factory=GenerateOptions)


class JobStatus(str, Enum):
    """Lifecycle states for asynchronous documentation jobs."""

    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class JobResult(BaseModel):
    """Successful job output artifacts.

    Data flow:
        The ADK endpoint returns the generated ``README.md`` content and the
        backend stores that text for polling clients.
    """

    markdown: Optional[str] = None


class ErrorBody(BaseModel):
    """Canonical API error content."""

    code: str
    message: str
    details: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Envelope returned for failed API requests."""

    error: ErrorBody


class JobRecord(BaseModel):
    """Internal persisted representation of a generation job.

    Data flow:
        Created when a job is accepted, updated through processing phases,
        then returned by polling endpoints as a reduced status view.
    """

    job_id: str
    status: JobStatus
    github_url: str
    options: GenerateOptions
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    result: Optional[JobResult] = None
    error: Optional[ErrorBody] = None


class GenerateAcceptedResponse(BaseModel):
    """Response returned immediately after job submission."""

    job_id: str
    status: JobStatus
    created_at: datetime


class JobStatusResponse(BaseModel):
    """Polling response that reports the latest known job state."""

    job_id: str
    status: JobStatus
    result: Optional[JobResult] = None
    error: Optional[ErrorBody] = None
    created_at: datetime
