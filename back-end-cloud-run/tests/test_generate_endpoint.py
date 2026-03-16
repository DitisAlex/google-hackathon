"""Tests for documentation generation endpoints.

Data flow:
    These tests issue HTTP calls against the FastAPI app, mock background task
    behavior, and assert response status/payload contracts.
"""

from unittest.mock import AsyncMock

from src.main import app
from src.models.schemas import JobStatus
from tests.conftest import get_client


def test_generate_validates_url() -> None:
    """Ensure malformed repository URLs are rejected with HTTP 400."""
    client = get_client()
    response = client.post("/api/v1/generate", json={"github_url": "http://invalid"})
    assert response.status_code == 400


def test_generate_accepted_for_valid_url() -> None:
    """Ensure valid requests are accepted and queued for background work."""
    client = get_client()
    app.state.run_generation = AsyncMock(return_value=None)

    response = client.post("/api/v1/generate", json={"github_url": "https://github.com/org/repo"})
    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] in {JobStatus.queued.value, JobStatus.processing.value, JobStatus.completed.value}
    assert "job_id" in payload
