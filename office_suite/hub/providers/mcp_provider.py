"""MCP 资源提供者 — 通过 MCP 协议获取外部资源

设计方案第五章：资源中枢。

MCP (Model Context Protocol) 提供者通过 MCP 服务器获取：
  - 图片：Unsplash, Pexels, DALL-E
  - 视频：Pexels
  - 数据：API / DB
  - 图表：ECharts

source 格式：
  mcp__unsplash — Unsplash 图片搜索
  mcp__pexels   — Pexels 图片/视频
  mcp__minimax  — MiniMax AI 生成

注意：实际 MCP 调用需要运行中的 MCP 服务器。
本模块提供协议适配层，MCP 连接由外部环境管理。
"""

from dataclasses import dataclass
from typing import Any, Callable

from ..registry import ResourceProvider, ResourceResult


# MCP 服务器配置模板
MCP_SERVER_DEFAULTS: dict[str, dict[str, Any]] = {
    "unsplash": {
        "description": "Unsplash 图片搜索",
        "capabilities": ["image_search"],
        "params": {"query": "", "orientation": "landscape", "size": "regular"},
    },
    "pexels": {
        "description": "Pexels 图片/视频",
        "capabilities": ["image_search", "video_search"],
        "params": {"query": "", "type": "photo", "per_page": 1},
    },
    "minimax": {
        "description": "MiniMax AI 生成",
        "capabilities": ["image_generate", "text_generate"],
        "params": {"prompt": "", "model": "image-01"},
    },
    "dalle": {
        "description": "DALL-E 图片生成",
        "capabilities": ["image_generate"],
        "params": {"prompt": "", "size": "1024x1024", "quality": "standard"},
    },
}


@dataclass
class MCPConfig:
    """MCP 服务器配置"""
    server_name: str
    endpoint: str = ""
    api_key: str = ""
    params: dict[str, Any] | None = None


class MCPProvider:
    """MCP 资源提供者

    通过 MCP 协议获取外部资源。

    使用方式：
        provider = MCPProvider()
        provider.set_caller("unsplash", my_unsplash_caller)
        result = provider.fetch({"mcp": "unsplash", "query": "nature"})
    """

    name = "mcp"
    prefixes = ["mcp__", "mcp:"]

    def __init__(self):
        self._callers: dict[str, Callable] = {}
        self._configs: dict[str, MCPConfig] = {}

    def set_caller(self, server_name: str, caller: Callable) -> None:
        """设置 MCP 服务器调用函数

        Args:
            server_name: 服务器名称（unsplash, pexels 等）
            caller: 调用函数，签名 (params: dict) -> ResourceResult
        """
        self._callers[server_name] = caller

    def set_config(self, config: MCPConfig) -> None:
        """设置 MCP 服务器配置"""
        self._configs[config.server_name] = config

    def can_handle(self, source: str | dict) -> bool:
        if isinstance(source, dict):
            return "mcp" in source or "mcp_server" in source
        if isinstance(source, str):
            return source.startswith("mcp__") or source.startswith("mcp:")
        return False

    def fetch(self, source: str | dict, **kwargs) -> ResourceResult:
        """获取 MCP 资源

        Args:
            source: 资源引用
                - "mcp__unsplash" 或 {"mcp": "unsplash", "query": "..."}
                - "mcp:pexels" 或 {"mcp_server": "pexels", "query": "..."}

        Returns:
            ResourceResult
        """
        # 解析服务器名和参数
        server_name, params = self._parse_source(source, kwargs)

        if not server_name:
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason="无法解析 MCP 服务器名",
                error=f"Invalid MCP source: {source}",
            )

        # 检查是否有对应的 caller
        caller = self._callers.get(server_name)
        if not caller:
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason=f"MCP 服务器 {server_name} 未配置 caller",
                error=f"No caller registered for MCP server: {server_name}",
            )

        # 调用 MCP
        try:
            result = caller(params)
            if isinstance(result, ResourceResult):
                return result
            # 如果 caller 返回的是原始数据，包装为 ResourceResult
            return ResourceResult(
                success=True,
                data=result,
                source_used=f"mcp__{server_name}",
            )
        except Exception as e:
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason=f"MCP 调用异常: {e}",
                error=str(e),
            )

    def _parse_source(self, source: str | dict, kwargs: dict) -> tuple[str, dict]:
        """解析 source 为服务器名和参数"""
        if isinstance(source, dict):
            server = source.get("mcp", source.get("mcp_server", ""))
            params = {k: v for k, v in source.items() if k not in ("mcp", "mcp_server")}
            params.update(kwargs)
            return server, params

        if isinstance(source, str):
            if source.startswith("mcp__"):
                server = source[5:]
            elif source.startswith("mcp:"):
                server = source[4:]
            else:
                return "", {}
            return server, dict(kwargs)

        return "", {}

    def list_servers(self) -> list[str]:
        """列出已配置的 MCP 服务器"""
        return list(self._callers.keys())
