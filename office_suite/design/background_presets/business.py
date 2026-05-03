"""商务类背景预设"""
from __future__ import annotations
from typing import Any
from ...constants import SLIDE_WIDTH_MM as SLIDE_W, SLIDE_HEIGHT_MM as SLIDE_H
from ..tokens import get_palette, get_gradient

def _palette_colors(name: str) -> dict[str, str]:
    return get_palette(name)

def business_clean(
    palette: str = "corporate",
    accent_bar: bool = True,
) -> dict[str, Any]:
    """商务简洁 — 白底 + 细微点阵 + 顶部色条

    适用：商务汇报、数据分析、正式提案
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal["bg"],
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [],
        "scrim": [],
        "ornament": [],
    }
    if accent_bar:
        board["ornament"] = [
            {
                "type": "color",
                "color": pal["primary"],
                "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": 2.5},
            },
            {
                "type": "color",
                "color": pal["accent"],
                "position": {"x": 0, "y": 2.5, "width": SLIDE_W, "height": 0.8},
            },
        ]
    return board

def subtle_texture(
    palette: str = "editorial",
    texture_type: str = "dot",
) -> dict[str, Any]:
    """细微纹理 — 低透明度几何图案填充

    适用：长文阅读、报告内页、需要质感但不过度设计的场景
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
        "ornament": [],
    }

    if texture_type == "dot":
        # 点阵纹理 — 右上角稀疏点阵
        dots = []
        for i in range(8):
            for j in range(8 - i):
                dots.append({
                    "type": "color",
                    "color": pal.get("border", "#CBD5E1"),
                    "position": {
                        "x": SLIDE_W - 60 + i * 5,
                        "y": 10 + j * 5,
                        "width": 1.2,
                        "height": 1.2,
                    },
                    "opacity": 0.25,
                })
        board["illustration"] = dots
    elif texture_type == "line":
        # 左侧竖线装饰
        lines = []
        for i in range(5):
            lines.append({
                "type": "color",
                "color": pal.get("border", "#CBD5E1"),
                "position": {"x": 15 + i * 3, "y": 30, "width": 0.4, "height": SLIDE_H - 60},
                "opacity": 0.2,
            })
        board["illustration"] = lines
    elif texture_type == "grid":
        # 背景细网格
        grid_items = []
        for x in range(20, int(SLIDE_W), 20):
            grid_items.append({
                "type": "color",
                "color": pal.get("border", "#CBD5E1"),
                "position": {"x": x, "y": 0, "width": 0.3, "height": SLIDE_H},
                "opacity": 0.1,
            })
        for y in range(20, int(SLIDE_H), 20):
            grid_items.append({
                "type": "color",
                "color": pal.get("border", "#CBD5E1"),
                "position": {"x": 0, "y": y, "width": SLIDE_W, "height": 0.3},
                "opacity": 0.1,
            })
        board["illustration"] = grid_items

    # 底部细线 ornament
    board["ornament"] = [
        {
            "type": "color",
            "color": pal.get("primary", "#0F172A"),
            "position": {"x": 25, "y": SLIDE_H - 4, "width": 30, "height": 0.8},
        },
    ]
    return board
def split_accent(
    palette: str = "corporate",
    split_ratio: float = 0.35,
    side: str = "left",
) -> dict[str, Any]:
    """分栏强调 — 一侧大面积色块 + 另一侧留白

    适用：对比展示、引言页、Hero 区域
    """
    pal = _palette_colors(palette)
    accent_w = SLIDE_W * split_ratio
    if side == "right":
        accent_x = SLIDE_W - accent_w
    else:
        accent_x = 0.0

    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#FFFFFF"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            {
                "type": "color",
                "color": pal.get("primary", "#1E40AF"),
                "position": {"x": accent_x, "y": 0, "width": accent_w, "height": SLIDE_H},
            },
        ],
        "scrim": [],
        "ornament": [
            {
                "type": "color",
                "color": pal.get("accent", "#60A5FA"),
                "position": {"x": accent_x + (accent_w if side == "left" else 0) - 1.5, "y": 20, "width": 1.5, "height": SLIDE_H - 40},
            },
        ],
    }
    return board
