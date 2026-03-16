import asyncio
import json
import uuid

from google.adk.agents import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from src.adk.agents.researcher import create_researcher_agent
from src.adk.agents.technical_writer import create_writer_agent
from src.adk.tools.github_tool import GithubTool, create_github_tools
from src.models.schemas import GenerateOptions, JobResult


class DocumentationOrchestrator:
    def __init__(self, github_tool: GithubTool, timeout_seconds: int) -> None:
        self._github_tool = github_tool
        self._timeout_seconds = timeout_seconds

    async def run(self, github_url: str, options: GenerateOptions) -> tuple[dict, JobResult]:
        tools = create_github_tools(self._github_tool)
        model = options.model if hasattr(options, "model") else "gemini-2.0-flash"
        pipeline = SequentialAgent(
            name="readme_pipeline",
            sub_agents=[
                create_researcher_agent(tools, model=model),
                create_writer_agent(),
            ],
        )

        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name="readme_generator",
            user_id="system",
            session_id=str(uuid.uuid4()),
            state={"repo_url": github_url},
        )

        runner = Runner(agent=pipeline, app_name="readme_generator", session_service=session_service)

        async def _run():
            from google.adk.types import Content, Part
            initial_message = Content(parts=[Part(text=github_url)], role="user")
            async for _ in runner.run_async(
                user_id="system",
                session_id=session.id,
                new_message=initial_message,
            ):
                pass  # consume the event stream
            final_session = await session_service.get_session(
                app_name="readme_generator", user_id="system", session_id=session.id
            )
            return final_session.state

        state = await asyncio.wait_for(_run(), timeout=self._timeout_seconds)

        markdown = state.get("readme_markdown", "")
        research = state.get("research_output", {})
        if isinstance(research, str):
            try:
                research = json.loads(research)
            except json.JSONDecodeError:
                research = {}

        result = JobResult(
            markdown=markdown,
            metadata={
                "tech_stack": research.get("tech_stack", []),
                "file_count": len(research.get("directory_summary", {})),
            },
            json=research if options.output_format.value == "json" else None,
        )
        return research, result
