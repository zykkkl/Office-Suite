"""氛围类背景预设"""
from __future__ import annotations
from typing import Any
from ...constants import SLIDE_WIDTH_MM as SLIDE_W, SLIDE_HEIGHT_MM as SLIDE_H
from ..tokens import get_palette, get_gradient

def _palette_colors(name: str) -> dict[str, str]:
    return get_palette(name)

def card_layered(
    palette: str = "minimal",
    card_count: int = 3,
) -> dict[str, Any]:
    """层叠卡片 — 多层半透明卡片阴影叠加 + 圆角边框感

    适用：产品展示、功能介绍、卡片式内容页
    """
    pal = _palette_colors(palette)
    cards = []
    margin = 20.0
    gap = 4.0
    card_w = (SLIDE_W - margin * 2 - gap * (card_count - 1)) / card_count
    card_h = SLIDE_H - margin * 2
    for i in range(card_count):
        x = margin + i * (card_w + gap)
        cards.append({
            "type": "color",
            "color": pal.get("bg_alt", "#F8FAFC"),
            "position": {"x": x, "y": margin, "width": card_w, "height": card_h},
            "opacity": 0.8,
        })
    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#FFFFFF"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": cards,
        "scrim": [],
        "ornament": [],
    }
    return board

def morandi_soft(
    palette: str = "morandi",
) -> dict[str, Any]:
    """莫兰迪柔和 — 低饱和度渐变 + 圆角几何点缀

    适用：文艺汇报、设计提案、高端品牌
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "gradient",
            "gradient": {
                "type": "linear",
                "angle": 135,
                "stops": [pal.get("bg", "#F5F0EB"), pal.get("bg_alt", "#EDE7E0")],
            },
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            # 右上角圆形装饰
            {
                "type": "color",
                "color": pal.get("accent", "#C4B5A6"),
                "position": {"x": SLIDE_W - 60, "y": -20, "width": 80, "height": 80},
                "opacity": 0.15,
            },
            # 左下角圆形装饰
            {
                "type": "color",
                "color": pal.get("secondary", "#A69B8E"),
                "position": {"x": -30, "y": SLIDE_H - 50, "width": 60, "height": 60},
                "opacity": 0.1,
            },
        ],
        "scrim": [],
        "ornament": [
            # 顶部细线
            {
                "type": "color",
                "color": pal.get("border", "#D4CFC9"),
                "position": {"x": 30, "y": 10, "width": SLIDE_W - 60, "height": 0.5},
            },
            # 底部细线
            {
                "type": "color",
                "color": pal.get("border", "#D4CFC9"),
                "position": {"x": 30, "y": SLIDE_H - 10, "width": SLIDE_W - 60, "height": 0.5},
            },
        ],
    }
    return board


def minimal_lines(
    palette: str = "minimal_bw",
) -> dict[str, Any]:
    """极简线条 — 白底 + 细线几何装饰

    适用：极简主义、现代设计、正式报告
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#FFFFFF"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [],
        "scrim": [],
        "ornament": [
            # 顶部粗线
            {
                "type": "color",
                "color": pal.get("primary", "#000000"),
                "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": 1.5},
            },
            # 底部细线
            {
                "type": "color",
                "color": pal.get("border", "#E0E0E0"),
                "position": {"x": 30, "y": SLIDE_H - 8, "width": SLIDE_W - 60, "height": 0.3},
            },
            # 左侧竖线装饰
            {
                "type": "color",
                "color": pal.get("border", "#E0E0E0"),
                "position": {"x": 25, "y": 30, "width": 0.3, "height": SLIDE_H - 60},
            },
        ],
    }
    return board


def polygon_geometric(
    palette: str = "corporate",
    polygon_count: int = 5,
) -> dict[str, Any]:
    """多边形几何 — 不规则多边形装饰背景

    适用：科技公司、创意提案、现代设计
    """
    pal = _palette_colors(palette)
    polygons = []

    # 生成随机位置的多边形装饰
    positions = [
        {"x": 20, "y": 15, "w": 40, "h": 35},
        {"x": SLIDE_W - 70, "y": 20, "w": 50, "h": 45},
        {"x": 100, "y": SLIDE_H - 60, "w": 45, "h": 40},
        {"x": 180, "y": 80, "w": 35, "h": 30},
        {"x": 50, "y": 90, "w": 40, "h": 35},
    ]

    for i, pos in enumerate(positions[:polygon_count]):
        polygons.append({
            "type": "color",
            "color": pal.get("accent", "#60A5FA") if i % 2 == 0 else pal.get("primary", "#1E40AF"),
            "position": {"x": pos["x"], "y": pos["y"], "width": pos["w"], "height": pos["h"]},
            "opacity": 0.08 + (i * 0.02),
        })

    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#FFFFFF"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": polygons,
        "scrim": [],
        "ornament": [],
    }
    return board


def chinese_ink_wash(
    palette: str = "chinese_ink",
) -> dict[str, Any]:
    """中国风水墨 — 水墨山水意境背景

    适用：中国文化主题、古典风格、传统汇报
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#F8F6F0"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            # 右侧水墨晕染效果
            {
                "type": "radial_gradient",
                "color": pal.get("primary", "#2C3E50"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("primary", "#2C3E50") + "15", "#00000000"],
                },
                "position": {"x": "65%", "y": "30%", "width": "35%", "height": "40%"},
                "opacity": 0.2,
            },
            # 左下角淡墨效果
            {
                "type": "radial_gradient",
                "color": pal.get("secondary", "#34495E"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("secondary", "#34495E") + "10", "#00000000"],
                },
                "position": {"x": 0, "y": "70%", "width": "30%", "height": "30%"},
                "opacity": 0.15,
            },
        ],
        "scrim": [],
        "ornament": [
            # 顶部水墨线条
            {
                "type": "color",
                "color": pal.get("primary", "#2C3E50"),
                "position": {"x": 40, "y": 12, "width": 60, "height": 0.8},
                "opacity": 0.4,
            },
            # 底部水墨线条
            {
                "type": "color",
                "color": pal.get("primary", "#2C3E50"),
                "position": {"x": SLIDE_W - 100, "y": SLIDE_H - 12, "width": 60, "height": 0.8},
                "opacity": 0.4,
            },
        ],
    }
    return board


