"""设计系统模块

Office Suite 自有的文档/PPT 设计令牌系统。
不引用 Material / Fluent / Ant Design 等 UI 设计语言。

用法：
    from office_suite.design import PALETTE, TYPOGRAPHY, SPACING, GRID
    from office_suite.design import get_palette, get_font, get_layout
"""

from .tokens import (
    PALETTE,
    TYPOGRAPHY,
    SPACING,
    GRID,
    LAYOUTS,
    SHADOWS,
    RADII,
    GRADIENTS,
    get_palette,
    get_font,
    get_layout,
    get_shadow,
    get_gradient,
    palette_to_style,
)

__all__ = [
    "PALETTE",
    "TYPOGRAPHY",
    "SPACING",
    "GRID",
    "LAYOUTS",
    "SHADOWS",
    "RADII",
    "GRADIENTS",
    "get_palette",
    "get_font",
    "get_layout",
    "get_shadow",
    "get_gradient",
    "palette_to_style",
]
