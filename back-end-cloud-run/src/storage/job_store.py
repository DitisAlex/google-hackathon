"""Persistence layer for asynchronous documentation jobs.

Data flow:
    API routes create queued jobs here, background workers update status as
    processing advances, and polling endpoints read the latest job record.
    State is mirrored to a JSON snapshot file for simple restart recovery.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from src.models.schemas import ErrorBody, GenerateOptions, JobRecord, JobResult, JobStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JobStore:
    """In-memory job registry with JSON snapshot persistence."""

    def __init__(self, snapshot_path: str = ".jobs_snapshot.json") -> None:
        """Initialize store state and attempt snapshot restore.

        Args:
            snapshot_path: Filesystem path used to read/write serialized jobs.
        """
        self._snapshot_path = Path(snapshot_path)
        self._jobs: Dict[str, JobRecord] = {}
        self._load_snapshot()

    def create_job(self, job_id: str, github_url: str, options: GenerateOptions) -> JobRecord:
        """Create and persist a new queued job.

        Args:
            job_id: Unique generated identifier.
            github_url: Repository URL being analyzed.
            options: Generation options selected by the caller.

        Returns:
            Newly created :class:`JobRecord`.
        """
        now = datetime.now(timezone.utc)
        record = JobRecord(
            job_id=job_id,
            status=JobStatus.queued,
            github_url=github_url,
            options=options,
            created_at=now,
            updated_at=now,
        )
        self._jobs[job_id] = record
        self._save_snapshot()
        logger.info("job_created", job_id=job_id, github_url=github_url)
        return record

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        """Return a job by ID if it exists."""
        logger.debug("job_lookup", job_id=job_id, found=job_id in self._jobs)
        return self._jobs.get(job_id)

    def set_processing(self, job_id: str) -> None:
        """Mark an existing job as actively processing."""
        record = self._jobs[job_id]
        record.status = JobStatus.processing
        record.updated_at = datetime.now(timezone.utc)
        self._save_snapshot()
        logger.info("job_marked_processing", job_id=job_id)

    def set_completed(self, job_id: str, result: JobResult) -> None:
        """Store successful result and mark the job as completed."""
        record = self._jobs[job_id]
        record.status = JobStatus.completed
        record.result = result
        record.updated_at = datetime.now(timezone.utc)
        self._save_snapshot()
        logger.info("job_marked_completed", job_id=job_id)

    def set_failed(self, job_id: str, code: str, message: str, details: Optional[dict] = None) -> None:
        """Store failure details and mark the job as failed.

        Args:
            job_id: Target job identifier.
            code: Machine-readable failure code.
            message: Human-readable failure message.
            details: Optional error metadata.
        """
        record = self._jobs[job_id]
        record.status = JobStatus.failed
        record.error = ErrorBody(code=code, message=message, details=details or {})
        record.updated_at = datetime.now(timezone.utc)
        self._save_snapshot()
        logger.warning("job_marked_failed", job_id=job_id, code=code)

    def _save_snapshot(self) -> None:
        """Write all current jobs to disk as JSON."""
        payload = {job_id: record.model_dump(mode="json") for job_id, record in self._jobs.items()}
        self._snapshot_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.debug("job_snapshot_saved", path=str(self._snapshot_path), jobs=len(self._jobs))

    def _load_snapshot(self) -> None:
        """Restore jobs from snapshot if available and valid.

        Data flow:
            Reads snapshot file text, parses JSON, validates each job through
            Pydantic, and repopulates in-memory state. Any parse/IO failure
            falls back to an empty store to keep startup resilient.
        """
        if not self._snapshot_path.exists():
            return
        try:
            raw = self._snapshot_path.read_text(encoding="utf-8")
            if not raw.strip():
                return
            data = json.loads(raw)
            self._jobs = {job_id: JobRecord.model_validate(value) for job_id, value in data.items()}
            logger.info("job_snapshot_loaded", path=str(self._snapshot_path), jobs=len(self._jobs))
        except (json.JSONDecodeError, OSError):
            self._jobs = {}
            logger.warning("job_snapshot_load_failed", path=str(self._snapshot_path))
