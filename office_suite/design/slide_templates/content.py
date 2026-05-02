"""内容页模板"""
from __future__ import annotations

from typing import Any

from ._base import (
    SLIDE_W, SLIDE_H, _palette_colors,
    get_font_for_palette,
    business_clean, subtle_texture, frosted_glass,
    gradient_underline, divider_line,
)


def content_slide(
    palette: str = "corporate",
    title: str = "",
    layout: str = "full",
    style: str = "auto",
) -> dict[str, Any]:
    """内容页模板 — 通用的内容展示页

    Args:
        palette: 配色方案名
        title: 页面标题
        layout: 布局方式 (full, two_column, three_column, left_text_right_image)
        style: 风格 (auto, clean, textured, frosted)
    """
    pal = _palette_colors(palette)
    font_heading = get_font_for_palette(palette, "heading")
    font_sub = get_font_for_palette(palette, "subheading")

    # 自动选择风格
    if style == "auto":
        if palette in ("minimal", "editorial", "flat"):
            style = "clean"
        elif palette == "tech":
            style = "frosted"
        else:
            style = "clean"

    # 背景
    bg_map = {
        "clean": lambda: business_clean(palette, accent_bar=False),
        "textured": lambda: subtle_texture(palette, texture_type="dot"),
        "frosted": lambda: frosted_glass(palette),
    }
    background_board = bg_map.get(style, lambda: business_clean(palette, accent_bar=False))()

    # 元素
    elements = []

    # 顶部标题区域
    if title:
        elements.append({
            "type": "text",
            "content": title,
            "position": {"x": 25, "y": 14, "width": SLIDE_W - 50, "height": 14},
            "style": {
                "font": {
                    "family": font_heading.family,
                    "size": font_heading.size,
                    "weight": font_heading.weight,
                    "color": pal["text"],
                },
            },
            "align": "left",
            "vertical_align": "middle",
        })
        # 标题下划线（渐变）
        elements += gradient_underline(
            x=25, y=31, width=40, height=2,
            color_start=pal["primary"], color_end=pal["accent"],
        )

    # 内容区域占位符
    content_y = 38 if title else 20
    content_h = SLIDE_H - content_y - 12

    if layout == "full":
        # 全宽布局
        elements.append({
            "type": "shape",
            "shape_type": "rounded_rectangle",
            "position": {"x": 25, "y": content_y, "width": SLIDE_W - 50, "height": content_h},
            "style": {
                "fill": {"color": pal["bg_alt"]},
                "border": {"color": pal["border"], "width": 0.5},
            },
        })
    elif layout == "two_column":
        # 双栏布局
        col_w = (SLIDE_W - 66) / 2
        for i in range(2):
            x = 25 + i * (col_w + 16)
            elements.append({
                "type": "shape",
                "shape_type": "rounded_rectangle",
                "position": {"x": x, "y": content_y, "width": col_w, "height": content_h},
                "style": {
                    "fill": {"color": pal["bg_alt"]},
                    "border": {"color": pal["border"], "width": 0.5},
                    "padding": 8,
                },
            })
    elif layout == "three_column":
        # 三栏布局
        col_w = (SLIDE_W - 80) / 3
        for i in range(3):
            x = 25 + i * (col_w + 15)
            elements.append({
                "type": "shape",
                "shape_type": "rounded_rectangle",
                "position": {"x": x, "y": content_y, "width": col_w, "height": content_h},
                "style": {
                    "fill": {"color": pal["bg_alt"]},
                    "border": {"color": pal["border"], "width": 0.5},
                    "padding": 8,
                },
            })
    elif layout == "left_text_right_image":
        # 左文右图布局
        left_w = (SLIDE_W - 66) * 0.55
        right_w = (SLIDE_W - 66) - left_w
        elements.append({
            "type": "shape",
            "shape_type": "rounded_rectangle",
            "position": {"x": 25, "y": content_y, "width": left_w, "height": content_h},
            "style": {
                "fill": {"color": pal["bg_alt"]},
                "border": {"color": pal["border"], "width": 0.5},
            },
        })
        elements.append({
            "type": "shape",
            "shape_type": "rounded_rectangle",
            "position": {"x": 25 + left_w + 16, "y": content_y, "width": right_w, "height": content_h},
            "style": {
                "fill": {"color": pal["bg_alt"]},
                "border": {"color": pal["border"], "width": 0.5},
            },
        })

    # 底部装饰线
    elements += divider_line(x=25, y=SLIDE_H - 8, width=30, color=pal["border"])

    return {
        "layout": "blank",
        "background_board": background_board,
        "elements": elements,
    }
