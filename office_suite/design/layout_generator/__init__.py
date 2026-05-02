"""参数化布局生成器 — 生成 1000+ 布局配置

通过 Grid / Split / Special 三类参数化组合，批量生成覆盖常见排版场景的布局预设。
每个布局可被 `layout: <name>` 在 DSL 中直接引用。

用法：
    from office_suite.design.layout_generator import get_all_layouts, get_layout
    layouts = get_all_layouts()
    config = get_layout("g3x2g4d")
"""

from ._api import get_all_layouts, get_layout, search_layouts, layout_count

__all__ = [
    "get_all_layouts",
    "get_layout",
    "search_layouts",
    "layout_count",
]
