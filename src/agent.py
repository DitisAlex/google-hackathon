from src.adk.agents.doc_pipeline_agent import get_doc_pipeline_agent
from src.adk.tools.github_tool import GithubTool
from src.config import get_settings

_settings = get_settings()

root_agent = get_doc_pipeline_agent(
    github_tool=GithubTool(
        token=_settings.github_token,
        timeout_seconds=_settings.github_api_timeout_seconds,
        retry_attempts=_settings.github_retry_attempts,
        max_file_size_bytes=_settings.max_file_size_bytes,
    )
)
