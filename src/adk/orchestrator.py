import asyncio
import json
from typing import Any, Dict

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from src.adk.agents.doc_pipeline_agent import get_doc_pipeline_agent
from src.adk.tools.github_tool import GithubTool
from src.models.schemas import GenerateOptions, JobResult


class DocumentationOrchestrator:
    def __init__(self, github_tool: GithubTool, timeout_seconds: int) -> None:
        self._github_tool = github_tool
        self._timeout_seconds = timeout_seconds
        self._agent = get_doc_pipeline_agent(github_tool)
        self._session_service = InMemorySessionService()

    async def run(self, github_url: str, options: GenerateOptions) -> tuple[Dict[str, Any], JobResult]:
        async def _run_pipeline() -> tuple[Dict[str, Any], JobResult]:
            session = await self._session_service.create_session(
                app_name="doc-generator", user_id="system"
            )
            runner = Runner(
                agent=self._agent,
                app_name="doc-generator",
                session_service=self._session_service,
            )
            message = Content(parts=[Part(text=github_url)])
            markdown = ""
            async for event in runner.run_async(
                user_id="system",
                session_id=session.id,
                new_message=message,
            ):
                if event.is_final_response() and event.content:
                    markdown = event.content.parts[0].text

            result = JobResult(
                markdown=markdown,
                metadata={"source": github_url},
                json={"github_url": github_url, "output": markdown} if options.output_format.value == "json" else None,
            )
            return {"github_url": github_url}, result

        return await asyncio.wait_for(_run_pipeline(), timeout=self._timeout_seconds)
