"""资源缓存 — 避免重复获取同一资源

缓存策略：
  - 内存缓存（LRU）
  - 基于资源 URI 的键
  - 支持 TTL 过期
  - 缓存命中/未命中统计
"""

from collections import OrderedDict
from dataclasses import dataclass, field
from time import monotonic
from typing import Any


@dataclass
class CacheEntry:
    key: str
    data: Any
    mime_type: str = ""
    created_at: float = 0.0
    ttl: float = 300.0    # 秒

    @property
    def expired(self) -> bool:
        return monotonic() - self.created_at > self.ttl


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0

    @property
    def total(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        return self.hits / self.total if self.total > 0 else 0.0


class ResourceCache:
    """LRU 资源缓存"""

    def __init__(self, max_size: int = 128, default_ttl: float = 300.0):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._stats = CacheStats()

    @property
    def stats(self) -> CacheStats:
        return self._stats

    def get(self, key: str) -> Any | None:
        """获取缓存，返回 None 表示未命中"""
        entry = self._cache.get(key)
        if entry is None:
            self._stats.misses += 1
            return None
        if entry.expired:
            self._cache.pop(key, None)
            self._stats.misses += 1
            return None
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        self._stats.hits += 1
        return entry.data

    def put(self, key: str, data: Any, mime_type: str = "", ttl: float | None = None):
        """存入缓存"""
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key].data = data
            self._cache[key].mime_type = mime_type
            return
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)
            self._stats.evictions += 1
        self._cache[key] = CacheEntry(
            key=key,
            data=data,
            mime_type=mime_type,
            created_at=monotonic(),
            ttl=ttl if ttl is not None else self._default_ttl,
        )

    def invalidate(self, key: str):
        """删除指定缓存"""
        self._cache.pop(key, None)

    def clear(self):
        """清空缓存"""
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        entry = self._cache.get(key)
        if entry and not entry.expired:
            return True
        return False
