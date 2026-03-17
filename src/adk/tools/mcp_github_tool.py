import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RepoRef:
    owner: str
    repo: str


class MCPGithubTool:
    def __init__(
        self,
        token: str | None = None,
        mcp_image: str = "ghcr.io/github/github-mcp-server",
        max_file_size_bytes: int = 102_400,
    ) -> None:
        self._token = token
        self._mcp_image = mcp_image
        self._max_file_size_bytes = max_file_size_bytes

    def with_token(self, token: str) -> "MCPGithubTool":
        return MCPGithubTool(
            token=token,
            mcp_image=self._mcp_image,
            max_file_size_bytes=self._max_file_size_bytes,
        )

    @staticmethod
    def parse_repo_url(repo_url: str) -> RepoRef:
        parsed = urlparse(repo_url)
        if parsed.scheme != "https" or parsed.netloc != "github.com":
            raise ValueError("Repository URL must be https://github.com/{owner}/{repo}")
        parts = [part for part in parsed.path.strip("/").split("/") if part]
        if len(parts) < 2:
            raise ValueError("Repository URL must include owner and repo")
        return RepoRef(owner=parts[0], repo=parts[1].removesuffix(".git"))

    def _server_params(self) -> StdioServerParameters:
        env = {}
        if self._token:
            env["GITHUB_PERSONAL_ACCESS_TOKEN"] = self._token
        return StdioServerParameters(
            command="docker",
            args=[
                "run", "-i", "--rm",
                "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                "--toolsets", "repos",
                self._mcp_image,
            ],
            env=env if env else None,
        )

    async def _call_tool(self, tool_name: str, arguments: dict) -> Any:
        server_params = self._server_params()
        async with stdio_client(server_params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                logger.info("mcp_tool_call", tool=tool_name, arguments=arguments)
                if result.isError:
                    logger.warning("mcp_tool_error", tool=tool_name, content=result.content)
                    return None
                return result.content

    async def check_repo_accessibility(self, repo_url: str) -> tuple[bool, int]:
        ref = self.parse_repo_url(repo_url)
        try:
            result = await self._call_tool("get_file_contents", {
                "owner": ref.owner,
                "repo": ref.repo,
                "path": "",
            })
            if result is not None:
                return True, 200
            return False, 403
        except Exception:
            logger.exception("mcp_accessibility_check_failed", repo_url=repo_url)
            return False, 500

    async def fetch_tree(
        self,
        repo_url: str,
        branch: str | None = None,
        max_depth: int = 5,
    ) -> list[dict[str, Any]]:
        ref = self.parse_repo_url(repo_url)
        arguments: dict[str, Any] = {
            "owner": ref.owner,
            "repo": ref.repo,
            "recursive": True,
        }
        if branch:
            arguments["tree_sha"] = branch

        result = await self._call_tool("get_repository_tree", arguments)
        if result is None:
            return []

        tree: list[dict[str, Any]] = []
        for content_block in result:
            text = content_block.text if hasattr(content_block, "text") else str(content_block)
            try:
                data = json.loads(text)
            except (json.JSONDecodeError, TypeError):
                continue

            nodes = data.get("tree", []) if isinstance(data, dict) else []
            for node in nodes:
                path = node.get("path", "")
                if path.count("/") > max_depth:
                    continue
                tree.append({
                    "path": path,
                    "type": node.get("type", "unknown"),
                    "size": node.get("size", 0),
                })

        return tree

    async def read_file(
        self,
        repo_url: str,
        file_path: str,
        branch: str | None = None,
    ) -> str | None:
        ref = self.parse_repo_url(repo_url)
        arguments: dict[str, Any] = {
            "owner": ref.owner,
            "repo": ref.repo,
            "path": file_path,
        }
        if branch:
            arguments["ref"] = branch

        result = await self._call_tool("get_file_contents", arguments)
        if result is None:
            return None

        text_parts = []
        for content_block in result:
            text = content_block.text if hasattr(content_block, "text") else str(content_block)
            text_parts.append(text)

        content = "".join(text_parts)
        if len(content.encode("utf-8")) > self._max_file_size_bytes:
            return None

        return content
