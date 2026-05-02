"""纹理类背景预设"""
from __future__ import annotations
from typing import Any
from ..tokens import get_palette, get_gradient

SLIDE_W = 254.0
SLIDE_H = 142.875

def _palette_colors(name: str) -> dict[str, str]:
    return get_palette(name)

def paper_texture(
    palette: str = "warm",
) -> dict[str, Any]:
    """纸质纹理 — 暖色调背景 + 模拟纸张质感

    适用：手写笔记、复古风格、温馨故事
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#FFFBEB"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            # 左上角淡色块（模拟折痕）
            {
                "type": "color",
                "color": pal.get("bg_alt", "#FEF3C7"),
                "position": {"x": 0, "y": 0, "width": "15%", "height": "15%"},
                "opacity": 0.5,
            },
        ],
        "scrim": [],
        "ornament": [
            # 顶部装饰线
            {
                "type": "color",
                "color": pal.get("border", "#FDE68A"),
                "position": {"x": 20, "y": 8, "width": SLIDE_W - 40, "height": 1.5},
            },
            # 底部装饰线
            {
                "type": "color",
                "color": pal.get("border", "#FDE68A"),
                "position": {"x": 20, "y": SLIDE_H - 8, "width": SLIDE_W - 40, "height": 1.5},
            },
        ],
    }
    return board

def geometric_blocks(
    palette: str = "minimal",
) -> dict[str, Any]:
    """几何色块 — 不规则几何色块拼接背景

    适用：设计提案、建筑展示、现代艺术
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#FFFFFF"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            # 大块色块
            {
                "type": "color",
                "color": pal.get("primary", "#2563EB") + "10",
                "position": {"x": 0, "y": 0, "width": "40%", "height": "60%"},
            },
            {
                "type": "color",
                "color": pal.get("accent", "#60A5FA") + "08",
                "position": {"x": "60%", "y": "40%", "width": "40%", "height": "60%"},
            },
            # 小色块点缀
            {
                "type": "color",
                "color": pal.get("secondary", "#3B82F6") + "15",
                "position": {"x": "45%", "y": "10%", "width": "10%", "height": "10%"},
            },
        ],
        "scrim": [],
        "ornament": [
            # 几何线条
            {
                "type": "color",
                "color": pal.get("border", "#E2E8F0"),
                "position": {"x": 0, "y": "60%", "width": "40%", "height": 0.5},
            },
            {
                "type": "color",
                "color": pal.get("border", "#E2E8F0"),
                "position": {"x": "60%", "y": "40%", "width": "40%", "height": 0.5},
            },
        ],
    }
    return board


def diagonal_split(
    palette: str = "corporate",
    angle: str = "forward",
) -> dict[str, Any]:
    """对角分割 — 沿对角线分割的双色背景

    适用：对比展示、前后对比、变化展示
    """
    pal = _palette_colors(palette)
    if angle == "forward":
        # 左上到右下
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
                    "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": "50%"},
                },
                {
                    "type": "color",
                    "color": pal.get("secondary", "#3B82F6"),
                    "position": {"x": 0, "y": "50%", "width": SLIDE_W, "height": "50%"},
                },
            ],
            "scrim": [],
            "ornament": [
                {
                    "type": "color",
                    "color": pal.get("accent", "#60A5FA"),
                    "position": {"x": 0, "y": "49%", "width": SLIDE_W, "height": 2},
                },
            ],
        }
    else:
        # 反向分割
        board = {
            "background": {
                "type": "color",
                "color": pal.get("bg", "#FFFFFF"),
                "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
            },
            "illustration": [
                {
                    "type": "color",
                    "color": pal.get("secondary", "#3B82F6"),
                    "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": "50%"},
                },
                {
                    "type": "color",
                    "color": pal.get("primary", "#1E40AF"),
                    "position": {"x": 0, "y": "50%", "width": SLIDE_W, "height": "50%"},
                },
            ],
            "scrim": [],
            "ornament": [
                {
                    "type": "color",
                    "color": pal.get("accent", "#60A5FA"),
                    "position": {"x": 0, "y": "49%", "width": SLIDE_W, "height": 2},
                },
            ],
        }
    return board


def watermark_bg(
    palette: str = "editorial",
) -> dict[str, Any]:
    """水印背景 — 大号半透明文字/图形水印

    适用：机密文档、草稿、演示文稿内页
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#FFFFFF"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            # 大号半透明色块作为水印
            {
                "type": "color",
                "color": pal.get("primary", "#0F172A"),
                "position": {"x": "20%", "y": "20%", "width": "60%", "height": "60%"},
                "opacity": 0.03,
            },
        ],
        "scrim": [],
        "ornament": [
            # 顶部细线
            {
                "type": "color",
                "color": pal.get("border", "#CBD5E1"),
                "position": {"x": 20, "y": 5, "width": SLIDE_W - 40, "height": 0.3},
            },
            # 底部细线
            {
                "type": "color",
                "color": pal.get("border", "#CBD5E1"),
                "position": {"x": 20, "y": SLIDE_H - 5, "width": SLIDE_W - 40, "height": 0.3},
            },
        ],
    }
    return board


def dotted_grid_bg(
    palette: str = "editorial",
    dot_spacing: float = 8.0,
) -> dict[str, Any]:
    """点阵网格 — 规则点阵背景

    适用：技术文档、数据展示、现代简约
    """
    pal = _palette_colors(palette)
    dots = []

    # 生成点阵
    x = dot_spacing
    while x < SLIDE_W:
        y = dot_spacing
        while y < SLIDE_H:
            dots.append({
                "type": "color",
                "color": pal.get("border", "#CBD5E1"),
                "position": {"x": x, "y": y, "width": 1.2, "height": 1.2},
                "opacity": 0.3,
            })
            y += dot_spacing
        x += dot_spacing

    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#FFFFFF"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": dots[:200],  # 限制数量避免过多
        "scrim": [],
        "ornament": [],
    }
    return board


def striped_bg(
    palette: str = "minimal_bw",
    stripe_width: float = 2.0,
    stripe_spacing: float = 6.0,
) -> dict[str, Any]:
    """条纹背景 — 水平细条纹装饰

    适用：简约设计、数据报告、正式场合
    """
    pal = _palette_colors(palette)
    stripes = []

    # 生成水平条纹
    y = stripe_spacing
    while y < SLIDE_H:
        stripes.append({
            "type": "color",
            "color": pal.get("border", "#E0E0E0"),
            "position": {"x": 0, "y": y, "width": SLIDE_W, "height": stripe_width},
            "opacity": 0.15,
        })
        y += stripe_spacing + stripe_width

    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#FFFFFF"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": stripes,
        "scrim": [],
        "ornament": [],
    }
    return board
