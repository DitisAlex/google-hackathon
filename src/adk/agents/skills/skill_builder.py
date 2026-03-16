import pathlib
from typing import Any

import yaml
from google.adk.skills import models
from google.adk.tools.skill_toolset import SkillToolset

_SKILLS_DIR = pathlib.Path(__file__).parent


def _load_skill_from_md(filename: str) -> models.Skill:
    """Parse a SKILL.md file and return a models.Skill instance.

    The file must have YAML frontmatter (between --- delimiters) containing
    at least a `name` key. The body after the frontmatter becomes the skill
    instructions.
    """
    raw = (_SKILLS_DIR / filename).read_text(encoding="utf-8")

    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise ValueError(
            f"Skill file '{filename}' is missing YAML frontmatter. "
            "Expected content between --- delimiters."
        )

    frontmatter_data: dict[str, Any] = yaml.safe_load(parts[1]) or {}
    instructions = parts[2].strip()

    return models.Skill(
        frontmatter=models.Frontmatter(
            name=frontmatter_data["name"],
            description=frontmatter_data.get("description", ""),
        ),
        instructions=instructions,
    )


# Pre-built skill instances — import directly or compose via build_skill_toolset()
writing_readme_skill = _load_skill_from_md("writing_onboarding_readme.md")
analyzing_repo_skill = _load_skill_from_md("analyzing_repo.md")


def build_skill_toolset() -> SkillToolset:
    """Return a SkillToolset containing all agent skills in this package."""
    return SkillToolset(skills=[analyzing_repo_skill, writing_readme_skill])
