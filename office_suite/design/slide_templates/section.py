"""章节页模板"""
from __future__ import annotations

from typing import Any

from ._base import (
    SLIDE_W, SLIDE_H, _palette_colors,
    get_font_for_palette,
    business_clean, gradient_spotlight, frosted_glass,
    gradient_underline,
)


def section_slide(
    palette: str = "corporate",
    section_title: str = "",
    section_number: int = 1,
    style: str = "auto",
) -> dict[str, Any]:
    """章节页模板 — 分隔章节的过渡页

    Args:
        palette: 配色方案名
        section_title: 章节标题
        section_number: 章节编号
        style: 风格 (auto, minimal, gradient, split)
    """
    pal = _palette_colors(palette)
    font_title = get_font_for_palette(palette, "section_title")
    font_data = get_font_for_palette(palette, "data_large")

    # 自动选择风格
    if style == "auto":
        if palette in ("tech", "creative", "sunset", "ocean", "forest"):
            style = "gradient"
        else:
            style = "minimal"

    # 背景
    bg_map = {
        "minimal": lambda: business_clean(palette),
        "gradient": lambda: gradient_spotlight(palette),
        "split": lambda: frosted_glass(palette),
    }
    background_board = bg_map.get(style, lambda: business_clean(palette))()

    # 元素
    elements = []

    # 章节编号（大号数字）
    elements.append({
        "type": "text",
        "content": f"{section_number:02d}",
        "position": {"x": 30, "y": 28, "width": 60, "height": 48},
        "style": {
            "font": {
                "family": font_data.family,
                "size": 72,
                "weight": 700,
                "color": pal["accent"] + "30",
            },
        },
        "align": "left",
        "vertical_align": "middle",
    })

    # 章节标题
    if section_title:
        elements.append({
            "type": "text",
            "content": section_title,
            "position": {"x": 100, "y": 40, "width": 130, "height": 22},
            "style": {
                "font": {
                    "family": font_title.family,
                    "size": font_title.size,
                    "weight": font_title.weight,
                    "color": pal["text"],
                },
            },
            "align": "left",
            "vertical_align": "middle",
        })
        # 标题下划线（渐变）
        elements += gradient_underline(
            x=100, y=68, width=50, height=2.5,
            color_start=pal["primary"], color_end=pal["accent"],
        )

    return {
        "layout": "blank",
        "background_board": background_board,
        "elements": elements,
    }
