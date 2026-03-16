from fastapi.testclient import TestClient

from src.main import app


def get_client() -> TestClient:
    return TestClient(app)
