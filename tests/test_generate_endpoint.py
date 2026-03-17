from unittest.mock import AsyncMock, patch

from src.main import app
from src.models.schemas import JobStatus
from tests.conftest import get_client


def test_generate_validates_url() -> None:
    client = get_client()
    response = client.post("/api/v1/generate", json={"github_url": "http://invalid"})
    assert response.status_code == 400


def test_generate_accepted_with_mocked_repo_check() -> None:
    client = get_client()
    app.state.run_generation = AsyncMock(return_value=None)

    with patch(
        "src.adk.tools.github_tool.GithubTool.check_repo_accessibility",
        new=AsyncMock(return_value=(True, 200)),
    ):
        response = client.post("/api/v1/generate", json={"github_url": "https://github.com/org/repo"})

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] in {JobStatus.queued.value, JobStatus.processing.value, JobStatus.completed.value}
    assert "job_id" in payload
