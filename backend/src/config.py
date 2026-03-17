from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "repo-doc-generator"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    request_rate_limit: str = "10/minute"
    max_job_timeout_seconds: int = 120
    max_request_body_bytes: int = 10_240
    max_file_size_bytes: int = 102_400

    github_api_timeout_seconds: int = 10
    github_retry_attempts: int = 3
    github_token: str | None = None
    github_client_id: str = ""
    github_client_secret: str = ""
    github_mcp_image: str = "ghcr.io/github/github-mcp-server"

    jwt_secret_key: str = "change-me-in-production"
    jwt_expire_minutes: int = 480

    gemini_primary_model: str = "gemini-3"
    gemini_fallback_model: str = "gemini-2.0-flash"

    gcp_project_id: str | None = None
    gcp_location: str = "us-central1"
    enable_cloud_trace: bool = False
    cors_allow_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_allow_origins:
            return ["*"]
        return [part.strip() for part in self.cors_allow_origins.split(",") if part.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
