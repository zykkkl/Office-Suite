"""文本引擎 — 塑形 / WordArt / 路径文字 / 富文本"""

from .shaping import (
    PPTX_TEXT_WARP_MAP, TextTransform, apply_text_transform,
    get_supported_transforms, AVAILABLE_TRANSFORMS,
)
from .path_text import (
    PathTextConfig, PathPoint, CharPlacement,
    generate_arc_points, generate_wave_points, layout_chars_on_path,
    to_html_svg, to_pptx_placements,
)
from .rich_text import (
    RichDocument, RichParagraph, TextRun,
    parse_rich_text, to_html, to_pptx_runs,
)

__all__ = [
    "PPTX_TEXT_WARP_MAP", "TextTransform", "apply_text_transform",
    "get_supported_transforms", "AVAILABLE_TRANSFORMS",
    "PathTextConfig", "PathPoint", "CharPlacement",
    "generate_arc_points", "generate_wave_points", "layout_chars_on_path",
    "to_html_svg", "to_pptx_placements",
    "RichDocument", "RichParagraph", "TextRun",
    "parse_rich_text", "to_html", "to_pptx_runs",
]
