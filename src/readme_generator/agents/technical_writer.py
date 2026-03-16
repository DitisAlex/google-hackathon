from google.adk.agents import LlmAgent

WRITER_PROMPT = """
You are a technical writer producing a professional README.md.

You will receive a JSON research report from the previous agent in the session state key "research_output".

Transform it into a well-structured Markdown document with these sections:
# <Project Name>
## Overview
## Tech Stack  (table: Component | Version/Status)
## Architecture
## Entry Points
## Directory Structure
## Getting Started  (inferred setup steps)
## Notes

Rules:
- Use standard GitHub Markdown.
- Do NOT invent information not present in the research report.
- If a section has no data, omit it.
- Output ONLY the Markdown — no preamble.
"""


def create_writer_agent(model: str = "gemini-2.0-flash") -> LlmAgent:
    return LlmAgent(
        name="technical_writer",
        model=model,
        instruction=WRITER_PROMPT,
        output_key="readme_markdown",
    )
