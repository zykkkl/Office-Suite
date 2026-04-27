"""资源解析器 — 将 IR 节点中的资源引用解析为实际资源

架构位置：
  IR 节点 (source="mcp__unsplash?query=nature")
    → [本文件] ResourceResolver.resolve()
    → ResourceResult (bytes/Path/None)
    → 渲染器使用

降级链（4 级）：
  1. 缓存命中 → 直接返回
  2. Provider 获取 → 成功则写入缓存
  3. 占位符标记 → fallback_used=True
  4. 空结果 + warning 日志
"""

import logging
from pathlib import Path
from typing import Any

from .registry import ResourceRegistry, ResourceResult
from .cache import ResourceCache
from .providers.local_provider import LocalFileProvider
from .providers.inline_provider import InlineDataProvider

logger = logging.getLogger(__name__)


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

    def __init__(
        self,
        registry: ResourceRegistry | None = None,
        cache: ResourceCache | None = None,
    ):
        self.registry = registry or create_default_registry()
        self.cache = cache or ResourceCache()

    def resolve(self, source: str | dict, **kwargs) -> ResourceResult:
        """解析资源引用

        降级链：
        1. 缓存命中 → 直接返回（cache_hit=True）
        2. Provider 获取成功 → 写入缓存，返回结果
        3. Provider 获取失败 → 返回占位符（fallback_used=True）
        4. source 为 None → 立即返回失败结果 + warning 日志
        """
        if source is None:
            logger.warning("[ResourceResolver] source 为 None，跳过解析")
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason="source 为 None",
            )

        # 生成缓存键
        cache_key = str(source)

        # 1. 缓存命中
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug("[ResourceResolver] 缓存命中: %s", cache_key)
            return cached

        # 2. Provider 获取
        result = self.registry.resolve(source, **kwargs)

        if result.success:
            # 写入缓存
            self.cache.put(cache_key, result)
            logger.debug("[ResourceResolver] 资源已获取并缓存: %s", cache_key)
        else:
            # 3. 降级：占位符
            result.fallback_used = True
            if not result.fallback_reason:
                result.fallback_reason = "资源获取失败"
            # 4. warning 日志
            logger.warning(
                "[ResourceResolver] 资源获取失败，使用占位符: %s — %s",
                cache_key,
                result.fallback_reason,
            )

        return result

    def resolve_for_image(self, source: str | dict, base_dir: Path | None = None) -> ResourceResult:
        """专门解析图片资源"""
        return self.resolve(source, base_dir=base_dir or Path.cwd())

    @property
    def cache_stats(self):
        """返回缓存统计信息"""
        return self.cache.stats
