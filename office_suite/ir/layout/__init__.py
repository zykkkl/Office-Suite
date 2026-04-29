"""IR 布局子模块 — re-export 布局规格

从 ir/layout_spec.py 统一导出，保持 import 路径简洁：
    from office_suite.ir.layout import LayoutSpec, LayoutMode
"""

from ..layout_spec import (
    AbsolutePosition,
    FlexAlign,
    FlexDirection,
    FlexJustify,
    FlexPosition,
    FlexWrap,
    GridAlign,
    GridPosition,
    LayoutMode,
    LayoutSpec,
    RelativePosition,
    mm_to_emu,
    mm_to_pt,
    mm_to_px,
    mm_to_twips,
)

__all__ = [
    "AbsolutePosition",
    "FlexAlign",
    "FlexDirection",
    "FlexJustify",
    "FlexPosition",
    "FlexWrap",
    "GridAlign",
    "GridPosition",
    "LayoutMode",
    "LayoutSpec",
    "RelativePosition",
    "mm_to_emu",
    "mm_to_pt",
    "mm_to_px",
    "mm_to_twips",
]
