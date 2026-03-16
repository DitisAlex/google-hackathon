from google.adk.agents import LlmAgent

RESEARCHER_PROMPT = """
You are a senior software architect analysing a GitHub repository.

Steps:
1. Call fetch_tree(repo_url) to get the full file listing.
2. Identify the tech stack from config files (pyproject.toml, package.json, go.mod, Cargo.toml, pom.xml, Gemfile, etc.).
3. Read the most informative files: README.md, main entry points (main.py, app.py, index.ts, cmd/main.go, etc.), and any top-level config files.
4. Synthesise your findings into a JSON object with keys:
   - repo_url, tech_stack (list), entry_points (list), project_purpose (string),
     architecture_notes (string), directory_summary (object: dir→file count).

Language support: Python, TypeScript/JavaScript, Go, Rust, Java, Ruby. Infer from file extensions if config files are absent.
Output ONLY valid JSON — no prose, no markdown fences.
"""


def create_researcher_agent(tools: list, model: str = "gemini-2.0-flash") -> LlmAgent:
    return LlmAgent(
        name="researcher",
        model=model,
        instruction=RESEARCHER_PROMPT,
        tools=tools,
        output_key="research_output",
    )
