from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    markdown = "markdown"
    json = "json"


class GenerateOptions(BaseModel):
    branch: str | None = None
    max_depth: int = Field(default=5, ge=1, le=12)
    include_tests: bool = False
    output_format: OutputFormat = OutputFormat.markdown


class GenerateRequest(BaseModel):
    github_url: str
    options: GenerateOptions = Field(default_factory=GenerateOptions)


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class JobResult(BaseModel):
    markdown: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    json_output: dict[str, Any] | None = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody


class JobRecord(BaseModel):
    job_id: str
    status: JobStatus
    github_url: str
    options: GenerateOptions
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    result: JobResult | None = None
    error: ErrorBody | None = None
    researcher_output: dict[str, Any] | None = None


class GenerateAcceptedResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: JobResult | None = None
    error: ErrorBody | None = None
    created_at: datetime
