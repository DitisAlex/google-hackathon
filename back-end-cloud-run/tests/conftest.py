"""Shared test helpers for API endpoint tests."""

from fastapi.testclient import TestClient

from src.main import app


def get_client() -> TestClient:
    """Create a synchronous API test client bound to the application."""
    return TestClient(app)
