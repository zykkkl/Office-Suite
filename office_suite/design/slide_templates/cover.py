"""封面页模板"""
from __future__ import annotations

from typing import Any

from ._base import (
    SLIDE_W, SLIDE_H, _palette_colors,
    get_font_for_palette,
    business_clean, gradient_spotlight, dark_elegant, neon_glow, gradient_mesh,
    gradient_underline, side_accent_bar, circle_frame,
)


def cover_slide(
    palette: str = "corporate",
    title: str = "",
    subtitle: str = "",
    layout: str = "center",
    style: str = "auto",
) -> dict[str, Any]:
    """封面页模板 — 完整的幻灯片设计方案

    Args:
        palette: 配色方案名
        title: 主标题
        subtitle: 副标题
        layout: 布局方式 (center, left, split)
        style: 风格 (auto, gradient, dark, elegant, neon)
            auto: 根据 palette 自动选择最佳风格
    """
    pal = _palette_colors(palette)
    font_title = get_font_for_palette(palette, "cover_title")
    font_sub = get_font_for_palette(palette, "cover_subtitle")

    # 自动选择风格
    if style == "auto":
        if palette in ("tech", "creative", "sunset", "ocean", "forest"):
            style = "gradient"
        elif palette == "chinese":
            style = "dark"
        else:
            style = "elegant"

    # 背景
    bg_map = {
        "gradient": lambda: gradient_spotlight(palette),
        "dark": lambda: dark_elegant(palette),
        "elegant": lambda: business_clean(palette),
        "neon": lambda: neon_glow(palette),
        "mesh": lambda: gradient_mesh(palette),
    }
    background_board = bg_map.get(style, lambda: business_clean(palette))()

    # 元素
    elements = []

    if layout == "center":
        # 居中布局
        if title:
            elements.append({
                "type": "text",
                "content": title,
                "position": {"x": 30, "y": 40, "width": SLIDE_W - 60, "height": 25},
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
        if subtitle:
            elements.append({
                "type": "text",
                "content": subtitle,
                "position": {"x": 50, "y": 76, "width": SLIDE_W - 100, "height": 12},
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
        # 标题下划线装饰（渐变）
        elements += gradient_underline(
            x=SLIDE_W / 2 - 25, y=70, width=50, height=2.5,
            color_start=pal["primary"], color_end=pal["accent"],
            rounded=True,
        )

    elif layout == "left":
        # 左对齐布局
        if title:
            elements.append({
                "type": "text",
                "content": title,
                "position": {"x": 40, "y": 38, "width": 160, "height": 22},
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
        if subtitle:
            elements.append({
                "type": "text",
                "content": subtitle,
                "position": {"x": 40, "y": 66, "width": 160, "height": 10},
                "style": {
                    "font": {
                        "family": font_sub.family,
                        "size": font_sub.size,
                        "weight": font_sub.weight,
                        "color": pal["text_secondary"],
                    },
                },
                "align": "left",
                "vertical_align": "middle",
            })
        # 左侧强调条
        elements += side_accent_bar(color=pal["primary"], position="left", width=3, margin=30)

    elif layout == "split":
        # 分栏布局（左侧标题，右侧装饰）
        if title:
            elements.append({
                "type": "text",
                "content": title,
                "position": {"x": 30, "y": 46, "width": 130, "height": 22},
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
        if subtitle:
            elements.append({
                "type": "text",
                "content": subtitle,
                "position": {"x": 30, "y": 74, "width": 130, "height": 10},
                "style": {
                    "font": {
                        "family": font_sub.family,
                        "size": font_sub.size,
                        "weight": font_sub.weight,
                        "color": pal["text_secondary"],
                    },
                },
                "align": "left",
                "vertical_align": "middle",
            })
        # 右侧装饰圆
        elements += circle_frame(x=210, y=70, radius=20, color=pal["accent"], opacity=0.3, filled=True, fill_color=pal["accent"] + "10")
        elements += circle_frame(x=220, y=80, radius=12, color=pal["primary"], opacity=0.4)

    return {
        "layout": "blank",
        "background_board": background_board,
        "elements": elements,
    }
