from collections import Counter
from typing import Any, Dict, List


LANGUAGE_HINTS = {
    "Python": ["pyproject.toml", "requirements.txt", "setup.py"],
    "TypeScript/JavaScript": ["package.json", "tsconfig.json", "pnpm-lock.yaml", "yarn.lock"],
    "Go": ["go.mod"],
    "Rust": ["Cargo.toml"],
    "Java": ["pom.xml", "build.gradle"],
    "Ruby": ["Gemfile"],
}


def _detect_stack(paths: List[str]) -> List[str]:
    detected: List[str] = []
    lowered = {path.lower() for path in paths}
    for stack_name, markers in LANGUAGE_HINTS.items():
        if any(marker.lower() in lowered for marker in markers):
            detected.append(stack_name)
    return detected or ["Unknown"]


def _guess_entry_points(paths: List[str]) -> List[str]:
    preferred = [
        "README.md",
        "main.py",
        "app.py",
        "src/main.py",
        "package.json",
        "pyproject.toml",
    ]
    path_set = set(paths)
    return [candidate for candidate in preferred if candidate in path_set]


def _directory_summary(paths: List[str]) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for path in paths:
        top = path.split("/", 1)[0]
        counter[top] += 1
    return dict(counter)


def build_research_report(repo_url: str, tree: List[Dict[str, Any]]) -> Dict[str, Any]:
    paths = [node["path"] for node in tree if node.get("path")]
    return {
        "repo_url": repo_url,
        "file_count": len(paths),
        "tech_stack": _detect_stack(paths),
        "entry_points": _guess_entry_points(paths),
        "project_purpose_guess": "Repository documentation generation candidate.",
        "directory_summary": _directory_summary(paths),
    }
