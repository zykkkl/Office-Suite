"""样式引擎 — 色彩空间 / 渐变 / 排版 / 动画"""

from .color import hex_to_oklch, oklch_to_hex, OKLCH, OKLAB
from .color import adjust_lightness, adjust_chroma, rotate_hue, generate_palette
from .gradient import parse_gradient, evaluate_gradient, generate_css, generate_pptx_xml
from .typography import TypographySpec, TextMetrics, estimate_text_metrics, to_css

__all__ = [
    "hex_to_oklch", "oklch_to_hex", "OKLCH", "OKLAB",
    "adjust_lightness", "adjust_chroma", "rotate_hue", "generate_palette",
    "parse_gradient", "evaluate_gradient", "generate_css", "generate_pptx_xml",
    "TypographySpec", "TextMetrics", "estimate_text_metrics", "to_css",
]
