from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    markdown = "markdown"
    json = "json"


class GenerateOptions(BaseModel):
    branch: Optional[str] = None
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
    markdown: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    json: Optional[Dict[str, Any]] = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody


class JobRecord(BaseModel):
    job_id: str
    status: JobStatus
    github_url: str
    options: GenerateOptions
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    result: Optional[JobResult] = None
    error: Optional[ErrorBody] = None
    researcher_output: Optional[Dict[str, Any]] = None


class GenerateAcceptedResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[JobResult] = None
    error: Optional[ErrorBody] = None
    created_at: datetime
