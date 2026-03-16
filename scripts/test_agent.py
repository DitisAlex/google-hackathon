"""Quick CLI test for the doc_pipeline agent.

Usage:
    GEMINI_API_KEY=your_key .venv/bin/python scripts/test_agent.py https://github.com/owner/repo
"""
import asyncio
import sys
from pathlib import Path

# Ensure the project root is on sys.path so `src` is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from src.agent import root_agent


async def main(github_url: str) -> None:
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test", user_id="dev")
    runner = Runner(agent=root_agent, app_name="test", session_service=session_service)

    message = Content(parts=[Part(text=github_url)])
    print(f"Running agent for: {github_url}\n{'─' * 60}\n")

    async for event in runner.run_async(user_id="dev", session_id=session.id, new_message=message):
        if event.is_final_response() and event.content:
            print(event.content.parts[0].text)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/google/adk-python"
    asyncio.run(main(url))
