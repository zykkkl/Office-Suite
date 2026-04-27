"""资源解析器 — 将 IR 节点中的资源引用解析为实际资源

架构位置：
  IR 节点 (source="mcp__unsplash?query=nature")
    → [本文件] ResourceResolver.resolve()
    → ResourceResult (bytes/Path/None)
    → 渲染器使用
"""

from pathlib import Path
from typing import Any

from .registry import ResourceRegistry, ResourceResult
from .providers.local_provider import LocalFileProvider
from .providers.inline_provider import InlineDataProvider


def create_default_registry() -> ResourceRegistry:
    """创建默认的资源注册表（内置 Provider）"""
    registry = ResourceRegistry()
    registry.register(LocalFileProvider())
    registry.register(InlineDataProvider())
    return registry


class ResourceResolver:
    """资源解析器 — 在渲染前解析 IR 节点中的资源引用

    使用方式：
        resolver = ResourceResolver()
        result = resolver.resolve("file://logo.png")
        result = resolver.resolve({"mcp__unsplash": {"query": "nature"}})
    """

    def __init__(self, registry: ResourceRegistry | None = None):
        self.registry = registry or create_default_registry()

    def resolve(self, source: str | dict, **kwargs) -> ResourceResult:
        """解析资源引用

        降级链：
        1. 尝试 Provider 获取
        2. 失败时返回占位符结果
        """
        if source is None:
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason="source 为 None",
            )

        result = self.registry.resolve(source, **kwargs)

        if not result.success:
            # 降级：返回占位符标记
            result.fallback_used = True
            if not result.fallback_reason:
                result.fallback_reason = "资源获取失败"

        return result

    def resolve_for_image(self, source: str | dict, base_dir: Path | None = None) -> ResourceResult:
        """专门解析图片资源"""
        return self.resolve(source, base_dir=base_dir or Path.cwd())
