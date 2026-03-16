from google.adk.agents import LlmAgent

from src.adk.agents.skills.skill_builder import build_skill_toolset
from src.adk.agents.tools.github_functions import make_github_tools
from src.adk.tools.github_tool import GithubTool
from src.config import get_settings


def get_doc_pipeline_agent(github_tool: GithubTool) -> LlmAgent:
    """Factory that builds the single documentation pipeline agent.

    The agent has three capabilities:
    - fetch_repo_tree / read_repo_file  — GitHub FunctionTools
    - analyze-repo skill                — inspects the tree, returns research JSON
    - write-md-doc skill                — turns research JSON into a README
    """
    return LlmAgent(
        name="doc_pipeline",
        model=get_settings().gemini_primary_model,
        description=(
            "Fetches a GitHub repository's file tree, analyzes its structure, "
            "and produces a well-formatted onboarding README document."
        ),
        instruction=(
            "You are a documentation pipeline agent. Given a GitHub repository URL, "
            "follow these steps in order:\n\n"
            "1. Call `fetch_repo_tree` with the provided URL to retrieve the file tree.\n"
            "2. Use your `analyze-repo` skill on the file tree to produce a structured "
            "JSON research report.\n"
            "3. Use your `write-md-doc` skill on the research report to produce a "
            "complete onboarding README.\n\n"
            "Return raw Markdown only — no preamble, no explanation."
        ),
        tools=[*make_github_tools(github_tool), build_skill_toolset()],
    )
