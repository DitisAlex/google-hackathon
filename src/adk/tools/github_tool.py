import asyncio
import base64
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx
from google.adk.tools import FunctionTool


@dataclass
class RepoRef:
    owner: str
    repo: str


class GithubTool:
    def __init__(
        self,
        token: str | None,
        timeout_seconds: int = 10,
        retry_attempts: int = 3,
        max_file_size_bytes: int = 102_400,
    ) -> None:
        self._token = token
        self._timeout = timeout_seconds
        self._retry_attempts = retry_attempts
        self._max_file_size_bytes = max_file_size_bytes

    @staticmethod
    def parse_repo_url(repo_url: str) -> RepoRef:
        parsed = urlparse(repo_url)
        if parsed.scheme != "https" or parsed.netloc != "github.com":
            raise ValueError("Repository URL must be https://github.com/{owner}/{repo}")
        parts = [part for part in parsed.path.strip("/").split("/") if part]
        if len(parts) < 2:
            raise ValueError("Repository URL must include owner and repo")
        return RepoRef(owner=parts[0], repo=parts[1].removesuffix(".git"))

    async def check_repo_accessibility(self, repo_url: str) -> tuple[bool, int]:
        ref = self.parse_repo_url(repo_url)
        headers = self._headers()
        url = f"https://api.github.com/repos/{ref.owner}/{ref.repo}"
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                is_private = bool(response.json().get("private", False))
                if is_private:
                    return False, 403
                return True, 200
            return False, response.status_code

    async def fetch_tree(self, repo_url: str, branch: str | None = None, max_depth: int = 5) -> list[dict[str, Any]]:
        ref = self.parse_repo_url(repo_url)
        default_branch = branch or await self._get_default_branch(ref)
        sha = await self._get_branch_sha(ref, default_branch)
        url = f"https://api.github.com/repos/{ref.owner}/{ref.repo}/git/trees/{sha}?recursive=1"
        data = await self._request_json(url)
        tree: list[dict[str, Any]] = []
        for node in data.get("tree", []):
            path = node.get("path", "")
            if path.count("/") > max_depth:
                continue
            tree.append(
                {
                    "path": path,
                    "type": node.get("type", "unknown"),
                    "size": node.get("size", 0),
                }
            )
        return tree

    async def read_file(self, repo_url: str, file_path: str, branch: str | None = None) -> str | None:
        ref = self.parse_repo_url(repo_url)
        branch_ref = branch or await self._get_default_branch(ref)
        url = f"https://api.github.com/repos/{ref.owner}/{ref.repo}/contents/{file_path}?ref={branch_ref}"
        data = await self._request_json(url)
        if isinstance(data, list):
            return None
        size = int(data.get("size", 0))
        if size > self._max_file_size_bytes:
            return None
        content = data.get("content")
        encoding = data.get("encoding", "utf-8")
        if not content:
            return None
        if encoding == "base64":
            decoded = base64.b64decode(content)
            try:
                return decoded.decode("utf-8")
            except UnicodeDecodeError:
                return None
        return str(content)

    async def _get_default_branch(self, ref: RepoRef) -> str:
        url = f"https://api.github.com/repos/{ref.owner}/{ref.repo}"
        data = await self._request_json(url)
        return data.get("default_branch", "main")

    async def _get_branch_sha(self, ref: RepoRef, branch: str) -> str:
        url = f"https://api.github.com/repos/{ref.owner}/{ref.repo}/branches/{branch}"
        data = await self._request_json(url)
        return data.get("commit", {}).get("sha")

    async def _request_json(self, url: str) -> dict[str, Any]:
        headers = self._headers()
        for attempt in range(self._retry_attempts):
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            if response.status_code in {403, 429, 500, 502, 503, 504} and attempt < self._retry_attempts - 1:
                await asyncio.sleep(2**attempt)
                continue
            response.raise_for_status()
        raise RuntimeError("Unreachable retry path")

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers


def create_github_tools(github_tool: GithubTool) -> list:
    async def fetch_tree(repo_url: str, branch: str | None = None, max_depth: int = 5):
        """Fetch the file tree of a GitHub repository. Returns a list of {path, type, size} dicts."""
        return await github_tool.fetch_tree(repo_url, branch, max_depth)

    async def read_file(repo_url: str, file_path: str, branch: str | None = None):
        """Read the text content of a single file in a GitHub repository. Returns None if too large or binary."""
        return await github_tool.read_file(repo_url, file_path, branch)

    return [FunctionTool(fetch_tree), FunctionTool(read_file)]
