"""资源中枢 — 统一资源获取"""

from .registry import ResourceProvider, ResourceResult, ResourceRegistry
from .resolver import ResourceResolver
from .cache import ResourceCache

__all__ = [
    "ResourceProvider", "ResourceResult", "ResourceRegistry",
    "ResourceResolver", "ResourceCache",
]
