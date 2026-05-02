"""引言页模板"""
from __future__ import annotations

from typing import Any

from ._base import (
    SLIDE_W, SLIDE_H, _palette_colors,
    get_font_for_palette,
    business_clean, dark_elegant, frosted_glass,
)


def quote_slide(
    palette: str = "corporate",
    quote: str = "",
    author: str = "",
    style: str = "auto",
) -> dict[str, Any]:
    """引言页模板 — 突出显示引言/金句

    Args:
        palette: 配色方案名
        quote: 引言内容
        author: 作者/来源
        style: 风格 (auto, minimal, elegant, dark)
    """
    pal = _palette_colors(palette)
    font_body = get_font_for_palette(palette, "body")
    font_caption = get_font_for_palette(palette, "caption")

    # 自动选择风格
    if style == "auto":
        if palette == "chinese":
            style = "dark"
        else:
            style = "elegant"

    # 背景
    bg_map = {
        "minimal": lambda: business_clean(palette, accent_bar=False),
        "elegant": lambda: frosted_glass(palette),
        "dark": lambda: dark_elegant(palette),
    }
    background_board = bg_map.get(style, lambda: frosted_glass(palette))()

    # 元素
    elements = []

    # 引号装饰
    elements.append({
        "type": "text",
        "content": "“",
        "position": {"x": 50, "y": 28, "width": 30, "height": 25},
        "style": {
            "font": {
                "size": 72,
                "weight": 700,
                "color": pal["accent"] + "40",
            },
        },
        "align": "left",
        "vertical_align": "top",
    })

    # 引言内容
    if quote:
        elements.append({
            "type": "text",
            "content": quote,
            "position": {"x": 60, "y": 52, "width": SLIDE_W - 120, "height": 42},
            "style": {
                "font": {
                    "family": font_body.family,
                    "size": font_body.size,
                    "weight": 400,
                    "color": pal["text"],
                },
            },
            "align": "center",
            "vertical_align": "middle",
        })

    # 作者
    if author:
        elements.append({
            "type": "text",
            "content": f"— {author}",
            "position": {"x": 80, "y": 100, "width": SLIDE_W - 160, "height": 10},
            "style": {
                "font": {
                    "family": font_caption.family,
                    "size": font_caption.size,
                    "weight": 400,
                    "color": pal["text_secondary"],
                },
            },
            "align": "center",
            "vertical_align": "middle",
        })

    return {
        "layout": "blank",
        "background_board": background_board,
        "elements": elements,
    }
