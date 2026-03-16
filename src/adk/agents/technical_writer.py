from typing import Any, Dict


def build_markdown(research: Dict[str, Any]) -> str:
    stack = research.get("tech_stack", [])
    entry_points = research.get("entry_points", [])
    summary = research.get("directory_summary", {})

    table_rows = "\n".join(f"| {item} | detected |" for item in stack)
    if not table_rows:
        table_rows = "| Unknown | detected |"

    tree_lines = "\n".join(f"- {name}: {count} files" for name, count in summary.items()) or "- No files found"
    entries = "\n".join(f"- {item}" for item in entry_points) or "- None identified"

    return (
        "# Generated Repository Documentation\n\n"
        f"Source: {research.get('repo_url', 'unknown')}\n\n"
        "## Tech Stack\n\n"
        "| Component | Status |\n"
        "| --- | --- |\n"
        f"{table_rows}\n\n"
        "## Entry Points\n\n"
        f"{entries}\n\n"
        "## Directory Summary\n\n"
        f"{tree_lines}\n\n"
        "## Notes\n\n"
        f"{research.get('project_purpose_guess', '')}\n"
    )
