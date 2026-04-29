"""IR 样式子模块 — re-export 样式规格

从 ir/style_spec.py 统一导出，保持 import 路径简洁：
    from office_suite.ir.style import StyleSpec, cascade_styles
"""

from ..style_spec import (
    BorderSpec,
    FillSpec,
    FontSpec,
    GradientSpec,
    GradientStop,
    ShadowSpec,
    StyleSpec,
    cascade_styles,
    contrast_ratio,
    hex_to_rgb,
    hex_to_rgba,
    luminance,
)

__all__ = [
    "BorderSpec",
    "FillSpec",
    "FontSpec",
    "GradientSpec",
    "GradientStop",
    "ShadowSpec",
    "StyleSpec",
    "cascade_styles",
    "contrast_ratio",
    "hex_to_rgb",
    "hex_to_rgba",
    "luminance",
]
