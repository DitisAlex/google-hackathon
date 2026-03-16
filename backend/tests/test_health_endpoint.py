from tests.conftest import get_client


def test_health_endpoint() -> None:
    client = get_client()
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body
