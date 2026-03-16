from google.adk.agents import SequentialAgent

from src.adk.agents.researcher import create_researcher_agent
from src.adk.agents.technical_writer import create_writer_agent
from src.adk.tools.github_tool import GithubTool, create_github_tools
import os

_github_tool = GithubTool(token=os.environ.get("GITHUB_TOKEN"))
_tools = create_github_tools(_github_tool)

root_agent = SequentialAgent(
    name="readme_pipeline",
    sub_agents=[
        create_researcher_agent(_tools),
        create_writer_agent(),
    ],
)
