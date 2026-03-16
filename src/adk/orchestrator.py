import asyncio
from typing import Any, Dict

from src.adk.agents.researcher import build_research_report
from src.adk.agents.technical_writer import build_markdown
from src.adk.tools.github_tool import GithubTool
from src.models.schemas import GenerateOptions, JobResult


class DocumentationOrchestrator:
    def __init__(self, github_tool: GithubTool, timeout_seconds: int) -> None:
        self._github_tool = github_tool
        self._timeout_seconds = timeout_seconds

    async def run(self, github_url: str, options: GenerateOptions) -> tuple[Dict[str, Any], JobResult]:
        async def _run_pipeline() -> tuple[Dict[str, Any], JobResult]:
            tree = await self._github_tool.fetch_tree(
                repo_url=github_url,
                branch=options.branch,
                max_depth=options.max_depth,
            )
            research = build_research_report(github_url, tree)
            markdown = build_markdown(research)
            result = JobResult(
                markdown=markdown,
                metadata={
                    "tech_stack": research.get("tech_stack", []),
                    "file_count": research.get("file_count", 0),
                },
                json=research if options.output_format.value == "json" else None,
            )
            return research, result

        return await asyncio.wait_for(_run_pipeline(), timeout=self._timeout_seconds)
