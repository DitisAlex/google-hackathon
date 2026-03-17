"""Contracts and validators for the diagrammer agent."""

from __future__ import annotations

import json
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class FrameworkInfo(BaseModel):
    """A detected framework or major technology."""

    model_config = ConfigDict(extra="ignore")

    name: str
    layer: Literal["frontend", "backend", "build", "ai", "infra", "other"]
    evidence: list[str] = Field(default_factory=list)

    @field_validator("layer", mode="before")
    @classmethod
    def _normalize_layer(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        normalized = value.strip().lower()
        alias_map = {
            "client": "frontend",
            "ui": "frontend",
            "web": "frontend",
            "server": "backend",
            "api": "backend",
            "service": "backend",
            "worker": "backend",
            "deployment": "infra",
            "devops": "infra",
            "ops": "infra",
            "infrastructure": "infra",
            "ml": "ai",
            "llm": "ai",
            "tooling": "build",
            "ci": "build",
            "cd": "build",
        }
        return alias_map.get(normalized, normalized)


class FlowEdge(BaseModel):
    """A directed relationship between two architecture nodes."""

    model_config = ConfigDict(extra="ignore")

    source: str
    target: str
    reason: str


class ArchitectureMap(BaseModel):
    """Normalized payload produced by the researcher agent."""

    model_config = ConfigDict(extra="ignore")

    repo_url: str
    repo_name: str
    default_branch: str | None = None
    summary: str = ""
    frameworks: list[FrameworkInfo] = Field(default_factory=list)
    entrypoints: list[str] = Field(default_factory=list)
    directories: list[str] = Field(default_factory=list)
    edges: list[FlowEdge] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


def architecture_map_schema_example() -> str:
    """Returns a compact JSON example for prompt grounding."""
    frontend_entrypoint = "frontend/src/main.jsx"
    payload = {
        "repo_url": "https://github.com/owner/repo",
        "repo_name": "repo",
        "default_branch": "main",
        "summary": "One or two sentences grounded in repo evidence.",
        "frameworks": [
            {
                "name": "React",
                "layer": "frontend",
                "evidence": ["frontend/package.json", frontend_entrypoint],
            }
        ],
        "entrypoints": [frontend_entrypoint],
        "directories": ["frontend/src/components", "frontend/src/pages"],
        "edges": [
            {
                "source": frontend_entrypoint,
                "target": "frontend/src/App.jsx",
                "reason": "main.jsx renders App",
            }
        ],
        "unknowns": ["No backend directory found in inspected tree."],
        "evidence": ["frontend/package.json", "README.md"],
    }
    return json.dumps(payload, indent=2)


def parse_architecture_map(raw_text: str) -> ArchitectureMap:
    """Parses the researcher output into a validated architecture map."""
    candidate = _extract_json_payload(raw_text)
    try:
        return ArchitectureMap.model_validate_json(candidate)
    except ValidationError as exc:
        raise ValueError(f"Researcher output is not valid ArchitectureMap JSON: {exc}") from exc


def validate_mermaid_output(raw_text: str) -> str:
    """Ensures the writer output contains a Mermaid graph block. Returns the fenced block."""
    text = raw_text.strip()

    # Try to extract a fenced mermaid block
    match = re.search(r"```mermaid\s+(.*?)\s+```", text, flags=re.DOTALL)
    if not match:
        raise ValueError("Writer output must contain a fenced mermaid block.")

    graph = _sanitize_mermaid_graph(match.group(1).strip())
    if not graph.startswith("graph TD"):
        raise ValueError("Writer output must start with 'graph TD'.")
    if "-->" not in graph:
        raise ValueError("Writer output must contain at least one edge.")
    return f"```mermaid\n{graph}\n```"


def _sanitize_mermaid_graph(graph: str) -> str:
    lines = graph.splitlines()
    sanitized_lines: list[str] = []
    for line in lines:
        sanitized = _sanitize_mermaid_edge_label(line)
        sanitized = _sanitize_mermaid_node_label(sanitized)
        sanitized_lines.append(sanitized)
    return "\n".join(sanitized_lines).strip()


def _sanitize_mermaid_edge_label(line: str) -> str:
    match = re.match(r"^(\s*\S+)\s+-->\s+(\S+)\s*:\s*(.+?)\s*$", line)
    if not match:
        return line
    source, target, label = match.groups()
    return f"{source} -->|{label.strip()}| {target}"


def _sanitize_mermaid_node_label(line: str) -> str:
    if "-->" in line:
        return line
    match = re.match(r"^(\s*\w+)\[(.*)\]\s*$", line)
    if not match:
        return line
    node_id, label = match.groups()
    label = label.strip()
    if label.startswith('"') and label.endswith('"'):
        return line
    escaped_label = label.replace('"', "&quot;")
    return f'{node_id}["{escaped_label}"]'


def _extract_json_payload(raw_text: str) -> str:
    text = raw_text.strip()
    fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in researcher output.")
    return text[start : end + 1]
