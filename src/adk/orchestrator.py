import asyncio
import json
import os
import uuid

from google.adk.agents import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from src.adk.agents.diagrammer import create_diagrammer_agent
from src.adk.agents.researcher import create_researcher_agent
from src.adk.agents.technical_writer import create_writer_agent
from src.adk.agents.skills.skill_builder import build_analyzing_skill_toolset, build_writing_skill_toolset
from src.adk.tools.github_tool import GithubTool, create_github_tools
from src.models.schemas import GenerateOptions, JobResult


class DocumentationOrchestrator:
    def __init__(self, github_tool: GithubTool, timeout_seconds: int, model: str = "gemini-2.0-flash", api_key: str | None = None) -> None:
        self._github_tool = github_tool
        self._timeout_seconds = timeout_seconds
        self._model = model
        if api_key:
            os.environ.setdefault("GOOGLE_API_KEY", api_key)

    async def run(self, github_url: str, options: GenerateOptions) -> tuple[dict, JobResult]:
        github_tools = create_github_tools(self._github_tool)
        pipeline = SequentialAgent(
            name="readme_pipeline",
            sub_agents=[
<<<<<<< feature/analyzing-writing-skills
                create_researcher_agent(
                    [*github_tools, build_analyzing_skill_toolset()], model=self._model),
                create_writer_agent(
                    [build_writing_skill_toolset()],
                    model=self._model),
=======
                create_researcher_agent(tools, model=self._model),
                create_diagrammer_agent(model=self._model),
                create_writer_agent(model=self._model),
>>>>>>> feature/google-adk-migration
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
        mermaid_diagram = state.get("mermaid_diagram", "")
        research = state.get("research_output", {})
        if isinstance(research, str):
            try:
                research = json.loads(research)
            except json.JSONDecodeError:
                research = {}

        result = JobResult(
            markdown=markdown,
            mermaid_diagram=mermaid_diagram if mermaid_diagram else None,
            metadata={
                "tech_stack": research.get("tech_stack", []),
                "file_count": len(research.get("directory_summary", {})),
            },
            json_output=research if options.output_format.value == "json" else None,
        )
        return research, result
