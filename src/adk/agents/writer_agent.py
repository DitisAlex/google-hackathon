from google.adk.agents import LlmAgent

from src.adk.agents.skills.skill_builder import build_skill_toolset
from src.config import get_settings


def get_writer_agent() -> LlmAgent:
    """Factory function to create and return the writer agent instance."""
    return LlmAgent(
        name="technical_writer",
        model=get_settings().gemini_primary_model,
        description=(
            "Receives a GitHub repository research report and produces a structured "
            "onboarding README document using the write-md-doc skill."
        ),
        instruction=(
            "You are a technical writer. You will receive a JSON research report about "
            "a GitHub repository. Use your write-md-doc skill to transform it into a "
            "well-structured onboarding README document. Return raw Markdown only."
        ),
        tools=[build_skill_toolset()],
    )
