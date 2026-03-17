"""Pipeline orchestration that invokes an internal repository agent function."""

import asyncio
from uuid import uuid4
from typing import Any

from src.models.schemas import GenerateOptions, JobResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentationOrchestrator:
    """Coordinate internal agent invocation and normalize output for storage/API."""

    def __init__(self, timeout_seconds: int) -> None:
        """Initialize orchestrator runtime settings.

        Args:
            timeout_seconds: End-to-end timeout applied to each generation run.
        """
        self._timeout_seconds = timeout_seconds

    async def run(self, github_url: str, options: GenerateOptions) -> JobResult:
        """Generate README content through the internal agent function.

        Args:
            github_url: Repository URL received from the API request.
            options: Generation options forwarded to ADK.

        Returns:
            A job result containing generated markdown.
        """

        async def _run_pipeline() -> JobResult:
            """Execute internal agent call and convert response to ``JobResult``."""
            logger.info("orchestrator_run_started", github_url=github_url)
            agent_output = await self._invoke_agent(
                github_url=github_url,
                options=options,
            )
            readme = agent_output.get("readme.md")
            if not isinstance(readme, str) or not readme.strip():
                raise ValueError("Agent output missing 'readme.md'")
            logger.info("orchestrator_run_completed", readme_chars=len(readme))
            return JobResult(markdown=readme)

        return await asyncio.wait_for(_run_pipeline(), timeout=self._timeout_seconds)

    async def _invoke_agent(self, github_url: str, options: GenerateOptions) -> dict:
        """Invoke the in-repo writer agent and return normalized JSON output."""
        from google.adk.runners import InMemorySessionService, Runner
        from google.genai import types

        from src.adk.agents.skills.writer_agent import get_writer_agent

        agent = get_writer_agent()
        prompt = self._build_writer_prompt(github_url, options)
        runner = Runner(
            app_name="repo-doc-generator",
            agent=agent,
            session_service=InMemorySessionService(),
            auto_create_session=True,
        )
        logger.info("writer_agent_invocation_started")

        message = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        events = runner.run_async(
            user_id="api-user",
            session_id=str(uuid4()),
            new_message=message,
        )

        last_text = ""
        event_count = 0
        async for event in events:
            event_count += 1
            text = self._extract_text_from_event(event)
            if text:
                last_text = text

        if not last_text:
            logger.warning("writer_agent_invocation_empty_output", events=event_count)
            raise ValueError("Writer agent output could not be normalized to 'readme.md'")
        logger.info("writer_agent_invocation_completed", events=event_count, output_chars=len(last_text))
        return {"readme.md": last_text}

    def _build_writer_prompt(self, github_url: str, options: GenerateOptions) -> str:
        """Build the writer-agent prompt from API inputs."""
        options_payload = options.model_dump(mode="json")
        return (
            "Generate a structured onboarding README in raw markdown for this repository.\n"
            f"Repository URL: {github_url}\n"
            f"Options: {options_payload}\n"
            "Return only markdown content."
        )

    def _normalize_agent_output(self, raw_output: Any) -> dict:
        """Normalize agent output into ``{'readme.md': '<markdown>'}`` shape."""
        if isinstance(raw_output, str):
            return {"readme.md": raw_output}

        if isinstance(raw_output, dict):
            if isinstance(raw_output.get("readme.md"), str):
                return {"readme.md": raw_output["readme.md"]}
            if isinstance(raw_output.get("readme_markdown"), str):
                return {"readme.md": raw_output["readme_markdown"]}

        for attr in ("text", "content", "output"):
            value = getattr(raw_output, attr, None)
            if isinstance(value, str):
                return {"readme.md": value}

        raise ValueError("Writer agent output could not be normalized to 'readme.md'")

    def _extract_text_from_event(self, event: Any) -> str:
        """Extract plain text content from a single ADK event object."""
        content = getattr(event, "content", None)
        if content is None:
            return ""

        parts = getattr(content, "parts", None)
        if not parts:
            return ""

        chunks: list[str] = []
        for part in parts:
            text = getattr(part, "text", None)
            if isinstance(text, str) and text.strip():
                chunks.append(text)
        return "\n".join(chunks).strip()
