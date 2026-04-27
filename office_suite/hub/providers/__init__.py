"""资源提供者 — 本地 / 内联 / MCP / Skill / AI"""

from .local_provider import LocalFileProvider
from .inline_provider import InlineDataProvider
from .mcp_provider import MCPProvider
from .skill_provider import SkillProvider
from .ai_provider import AIProvider

__all__ = [
    "LocalFileProvider", "InlineDataProvider",
    "MCPProvider", "SkillProvider", "AIProvider",
]
