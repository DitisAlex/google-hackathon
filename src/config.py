"""Application configuration models and loader.

Data flow:
    Environment variables are parsed into :class:`Settings`. The FastAPI app
    calls :func:`get_settings` once at startup and reuses the cached instance
    to configure logging, tracing, middleware limits, and orchestrator timeout.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime configuration for the service.

    Attributes mirror environment variables and safe defaults so the app can
    start locally without additional setup.
    """

    app_name: str = "repo-doc-generator"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    request_rate_limit: str = "10/minute"
    max_job_timeout_seconds: int = 120
    max_request_body_bytes: int = 10_240
    max_file_size_bytes: int = 102_400

    gemini_primary_model: str = "gemini-3"
    gemini_fallback_model: str = "gemini-2.0-flash"

    gcp_project_id: str | None = None
    gcp_location: str = "us-central1"
    enable_cloud_trace: bool = False
    cors_allow_origins: List[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | List[str]) -> List[str]:
        """Normalize CORS origins from either CSV string or list input.

        Args:
            value: Raw setting value from environment or already-parsed list.

        Returns:
            A cleaned list of origin strings, defaulting to ``["*"]``.
        """
        if isinstance(value, list):
            return value
        if not value:
            return ["*"]
        return [part.strip() for part in value.split(",") if part.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings object.

    Returns:
        Singleton-like :class:`Settings` instance for process lifetime.

    Data flow:
        First call parses environment and `.env`; subsequent calls reuse the
        same object to keep configuration consistent across modules.
    """
    return Settings()
