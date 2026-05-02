"""公开 API"""
from __future__ import annotations

from typing import Any

from ._constants import _SPECIAL_LAYOUTS
from ._grid import _generate_grid_layouts
from ._split import _generate_split_layouts
from ._special import _init_special_layouts

_LAYOUT_CACHE: dict[str, dict[str, Any]] | None = None


def get_all_layouts() -> dict[str, dict[str, Any]]:
    """获取所有布局配置（1000+），结果缓存"""
    global _LAYOUT_CACHE
    if _LAYOUT_CACHE is not None:
        return _LAYOUT_CACHE

    _init_special_layouts()

    layouts: dict[str, dict[str, Any]] = {}
    layouts.update(_generate_grid_layouts())
    layouts.update(_generate_split_layouts())
    layouts.update(_SPECIAL_LAYOUTS)

    _LAYOUT_CACHE = layouts
    return layouts


def get_layout(name: str) -> dict[str, Any] | None:
    """按名称获取单个布局配置"""
    return get_all_layouts().get(name)


def search_layouts(
    mode: str | None = None,
    min_columns: int | None = None,
    max_columns: int | None = None,
    has_rows: int | None = None,
    category: str | None = None,
) -> list[str]:
    """搜索布局名称

    Args:
        mode: 布局模式 ("grid" / "flex" / "absolute")
        min_columns: 最小列数
        max_columns: 最大列数
        has_rows: 精确行数
        category: 类别前缀 ("g" / "f" / "stats" / "feature" / ...)

    Returns:
        匹配的布局名称列表
    """
    all_layouts = get_all_layouts()
    results = []

    for name, config in all_layouts.items():
        if mode and config.get("mode") != mode:
            continue
        if category and not name.startswith(category):
            continue
        if min_columns is not None:
            cols = config.get("grid", {}).get("columns", 0)
            if cols < min_columns:
                continue
        if max_columns is not None:
            cols = config.get("grid", {}).get("columns", 999)
            if cols > max_columns:
                continue
        if has_rows is not None:
            if "x" in name:
                try:
                    rows_part = name.split("x")[1].split("g")[0]
                    if int(rows_part) != has_rows:
                        continue
                except (ValueError, IndexError):
                    continue
        results.append(name)

    return sorted(results)


def layout_count() -> int:
    """返回总布局数量"""
    return len(get_all_layouts())
