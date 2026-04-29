"""样式级联 — Re-export

核心实现在 engine/style/cascade.py。
本模块仅保留 re-export，保持 ir 层的数据结构职责。

所有 import 统一使用 engine.style.cascade：
    from office_suite.engine.style.cascade import cascade_style, cascade_style_by_name
"""

from ..engine.style.cascade import (
    cascade_style,
    cascade_style_by_name,
    DEFAULT_THEME_STYLES,
    _merge_field,
)

__all__ = [
    "cascade_style",
    "cascade_style_by_name",
    "DEFAULT_THEME_STYLES",
]
