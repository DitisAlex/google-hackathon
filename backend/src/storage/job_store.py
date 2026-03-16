import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from src.models.schemas import ErrorBody, GenerateOptions, JobRecord, JobResult, JobStatus


class JobStore:
    def __init__(self, snapshot_path: str = ".jobs_snapshot.json") -> None:
        self._snapshot_path = Path(snapshot_path)
        self._jobs: Dict[str, JobRecord] = {}
        self._load_snapshot()

    def create_job(self, job_id: str, github_url: str, options: GenerateOptions) -> JobRecord:
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
        return record

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        return self._jobs.get(job_id)

    def set_processing(self, job_id: str) -> None:
        record = self._jobs[job_id]
        record.status = JobStatus.processing
        record.updated_at = datetime.now(timezone.utc)
        self._save_snapshot()

    def set_researcher_output(self, job_id: str, output: dict) -> None:
        record = self._jobs[job_id]
        record.researcher_output = output
        record.updated_at = datetime.now(timezone.utc)
        self._save_snapshot()

    def set_completed(self, job_id: str, result: JobResult) -> None:
        record = self._jobs[job_id]
        record.status = JobStatus.completed
        record.result = result
        record.updated_at = datetime.now(timezone.utc)
        self._save_snapshot()

    def set_failed(self, job_id: str, code: str, message: str, details: Optional[dict] = None) -> None:
        record = self._jobs[job_id]
        record.status = JobStatus.failed
        record.error = ErrorBody(code=code, message=message, details=details or {})
        record.updated_at = datetime.now(timezone.utc)
        self._save_snapshot()

    def _save_snapshot(self) -> None:
        payload = {job_id: record.model_dump(mode="json") for job_id, record in self._jobs.items()}
        self._snapshot_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load_snapshot(self) -> None:
        if not self._snapshot_path.exists():
            return
        try:
            raw = self._snapshot_path.read_text(encoding="utf-8")
            if not raw.strip():
                return
            data = json.loads(raw)
            self._jobs = {job_id: JobRecord.model_validate(value) for job_id, value in data.items()}
        except (json.JSONDecodeError, OSError):
            self._jobs = {}
