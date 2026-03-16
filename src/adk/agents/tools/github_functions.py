from typing import Any, Dict, List, Optional

from src.adk.tools.github_tool import GithubTool


def make_github_tools(github_tool: GithubTool) -> List[Any]:
    """Return ADK-compatible async functions wrapping GithubTool.

    ADK automatically converts plain async functions into FunctionTools
    when passed to an LlmAgent's tools list.
    """

    async def fetch_repo_tree(
        repo_url: str,
        branch: Optional[str] = None,
        max_depth: int = 5,
    ) -> List[Dict[str, Any]]:
        """Fetch the full file/directory tree of a GitHub repository.

        Args:
            repo_url: Full HTTPS GitHub URL, e.g. https://github.com/owner/repo
            branch: Target branch name. Defaults to the repository's default branch.
            max_depth: Maximum directory depth to traverse (1-12). Defaults to 5.

        Returns:
            List of file nodes, each with 'path', 'type', and 'size' fields.
        """
        return await github_tool.fetch_tree(
            repo_url=repo_url,
            branch=branch,
            max_depth=max_depth,
        )

    async def read_repo_file(
        repo_url: str,
        file_path: str,
        branch: Optional[str] = None,
    ) -> Optional[str]:
        """Read the raw text content of a single file from a GitHub repository.

        Args:
            repo_url: Full HTTPS GitHub URL, e.g. https://github.com/owner/repo
            file_path: Path to the file relative to the repo root, e.g. 'src/main.py'
            branch: Target branch name. Defaults to the repository's default branch.

        Returns:
            File content as a UTF-8 string, or None if the file is binary or too large.
        """
        return await github_tool.read_file(
            repo_url=repo_url,
            file_path=file_path,
            branch=branch,
        )

    return [fetch_repo_tree, read_repo_file]
