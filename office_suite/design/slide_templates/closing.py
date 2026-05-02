"""收尾页模板"""
from __future__ import annotations

from typing import Any

from ._base import (
    SLIDE_W, SLIDE_H, _palette_colors,
    get_font_for_palette,
    business_clean, gradient_spotlight, dark_elegant,
    circle_frame,
)


def closing_slide(
    palette: str = "corporate",
    message: str = "谢谢",
    subtitle: str = "",
    style: str = "auto",
) -> dict[str, Any]:
    """收尾页模板 — 感谢/结束页

    Args:
        palette: 配色方案名
        message: 结束语
        subtitle: 副标题
        style: 风格 (auto, minimal, gradient, elegant)
    """
    pal = _palette_colors(palette)
    font_title = get_font_for_palette(palette, "cover_title")
    font_sub = get_font_for_palette(palette, "cover_subtitle")

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
        "elegant": lambda: dark_elegant(palette),
    }
    background_board = bg_map.get(style, lambda: business_clean(palette))()

    # 元素
    elements = []

    # 结束语（大号居中）
    if message:
        elements.append({
            "type": "text",
            "content": message,
            "position": {"x": 30, "y": 46, "width": SLIDE_W - 60, "height": 22},
            "style": {
                "font": {
                    "family": font_title.family,
                    "size": font_title.size,
                    "weight": font_title.weight,
                    "color": pal["text"],
                },
            },
            "align": "center",
            "vertical_align": "middle",
        })

    # 副标题
    if subtitle:
        elements.append({
            "type": "text",
            "content": subtitle,
            "position": {"x": 50, "y": 74, "width": SLIDE_W - 100, "height": 10},
            "style": {
                "font": {
                    "family": font_sub.family,
                    "size": font_sub.size,
                    "weight": font_sub.weight,
                    "color": pal["text_secondary"],
                },
            },
            "align": "center",
            "vertical_align": "middle",
        })

    # 装饰圆环
    elements += circle_frame(x=SLIDE_W / 2, y=42, radius=25, color=pal["accent"], opacity=0.15, filled=False)
    elements += circle_frame(x=SLIDE_W / 2, y=42, radius=18, color=pal["primary"], opacity=0.1, filled=True, fill_color=pal["primary"] + "05")

    return {
        "layout": "blank",
        "background_board": background_board,
        "elements": elements,
    }
