"""渐变类背景预设"""
from __future__ import annotations
from typing import Any
from ..tokens import get_palette, get_gradient

SLIDE_W = 254.0
SLIDE_H = 142.875

def _palette_colors(name: str) -> dict[str, str]:
    return get_palette(name)

def gradient_spotlight(
    palette: str = "tech",
    spotlight_x: float = 0.5,
    spotlight_y: float = 0.4,
) -> dict[str, Any]:
    """渐变聚光灯 — 深色径向渐变 + 中心高光 + 底部 scrim

    适用：科技产品发布、创意提案、封面页
    """
    pal = _palette_colors(palette)
    grad = get_gradient(palette) if palette in ["tech", "creative", "sunset", "ocean", "forest"] else get_gradient("tech")
    board: dict[str, Any] = {
        "background": {
            "type": "gradient",
            "gradient": {
                "type": "radial",
                "stops": [
                    pal.get("bg_alt", "#111827"),
                    pal.get("bg", "#0B0F19"),
                ],
            },
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            {
                "type": "radial_gradient",
                "color": pal.get("accent", "#06B6D4"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("accent", "#06B6D4") + "40", "#00000000"],
                },
                "position": {
                    "x": f"{(spotlight_x - 0.3) * 100}%",
                    "y": f"{(spotlight_y - 0.3) * 100}%",
                    "width": "60%",
                    "height": "60%",
                },
                "opacity": 0.3,
            },
        ],
        "scrim": [
            {
                "type": "linear_gradient",
                "gradient": {
                    "type": "linear",
                    "angle": 180,
                    "stops": ["#00000000", pal.get("bg", "#0B0F19") + "CC"],
                },
                "position": {"x": 0, "y": "70%", "width": SLIDE_W, "height": "30%"},
            },
        ],
        "ornament": [
            {
                "type": "color",
                "color": pal.get("accent", "#06B6D4"),
                "position": {"x": 0, "y": SLIDE_H - 1.5, "width": SLIDE_W, "height": 1.5},
            },
        ],
    }
    return board

def frosted_glass(
    palette: str = "minimal",
) -> dict[str, Any]:
    """毛玻璃质感 — 背景模糊 + 半透明卡片层

    适用：现代 UI 风格、仪表盘、信息卡片页
    """
    pal = _palette_colors(palette)
    # 毛玻璃效果通过多层半透明叠加模拟
    board: dict[str, Any] = {
        "background": {
            "type": "gradient",
            "gradient": {
                "type": "linear",
                "angle": 135,
                "stops": [pal.get("bg_alt", "#F8FAFC"), pal.get("bg", "#FFFFFF")],
            },
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            # 右上角模糊色块
            {
                "type": "color",
                "color": pal.get("accent", "#60A5FA") + "20",
                "position": {"x": "60%", "y": 0, "width": "40%", "height": "50%"},
                "opacity": 0.4,
            },
            # 左下角模糊色块
            {
                "type": "color",
                "color": pal.get("secondary", "#3B82F6") + "15",
                "position": {"x": 0, "y": "60%", "width": "50%", "height": "40%"},
                "opacity": 0.3,
            },
        ],
        "scrim": [],
        "ornament": [
            # 顶部细线
            {
                "type": "color",
                "color": pal.get("border", "#E2E8F0"),
                "position": {"x": 20, "y": 0, "width": SLIDE_W - 40, "height": 0.5},
            },
        ],
    }
    return board

def dark_elegant(
    palette: str = "creative",
) -> dict[str, Any]:
    """暗色优雅 — 深色背景 + 金色/银色点缀 + 边角光效

    适用：高端产品发布、奢华品牌、颁奖典礼
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": pal.get("bg", "#18181B"),
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            # 左上角光晕
            {
                "type": "radial_gradient",
                "color": pal.get("accent", "#FB7185"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("accent", "#FB7185") + "30", "#00000000"],
                },
                "position": {"x": -20, "y": -20, "width": "50%", "height": "50%"},
                "opacity": 0.2,
            },
            # 右下角光晕
            {
                "type": "radial_gradient",
                "color": pal.get("secondary", "#F43F5E"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("secondary", "#F43F5E") + "20", "#00000000"],
                },
                "position": {"x": "60%", "y": "60%", "width": "40%", "height": "40%"},
                "opacity": 0.15,
            },
        ],
        "scrim": [],
        "ornament": [
            # 顶部金色细线
            {
                "type": "color",
                "color": "#D4AF37",
                "position": {"x": 30, "y": 10, "width": SLIDE_W - 60, "height": 0.5},
                "opacity": 0.6,
            },
            # 底部金色细线
            {
                "type": "color",
                "color": "#D4AF37",
                "position": {"x": 30, "y": SLIDE_H - 10, "width": SLIDE_W - 60, "height": 0.5},
                "opacity": 0.6,
            },
        ],
    }
    return board

def gradient_mesh(
    palette: str = "ocean",
) -> dict[str, Any]:
    """渐变网格 — 多色渐变叠加 + 网格线纹理

    适用：创意设计、艺术展示、多彩主题
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "gradient",
            "gradient": {
                "type": "linear",
                "angle": 135,
                "stops": [
                    pal.get("bg", "#0B0F19"),
                    pal.get("bg_alt", "#111827"),
                ],
            },
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            # 多色渐变叠加
            {
                "type": "radial_gradient",
                "color": pal.get("primary", "#0EA5E9"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("primary", "#0EA5E9") + "40", "#00000000"],
                },
                "position": {"x": 0, "y": 0, "width": "50%", "height": "50%"},
                "opacity": 0.25,
            },
            {
                "type": "radial_gradient",
                "color": pal.get("accent", "#8B5CF6"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("accent", "#8B5CF6") + "30", "#00000000"],
                },
                "position": {"x": "50%", "y": "50%", "width": "50%", "height": "50%"},
                "opacity": 0.2,
            },
        ],
        "scrim": [],
        "ornament": [
            # 网格线纹理（水平）
            *[{
                "type": "color",
                "color": "#FFFFFF",
                "position": {"x": 0, "y": y, "width": SLIDE_W, "height": 0.2},
                "opacity": 0.05,
            } for y in range(0, int(SLIDE_H), 10)],
            # 网格线纹理（垂直）
            *[{
                "type": "color",
                "color": "#FFFFFF",
                "position": {"x": x, "y": 0, "width": 0.2, "height": SLIDE_H},
                "opacity": 0.05,
            } for x in range(0, int(SLIDE_W), 10)],
        ],
    }
    return board

def neon_glow(
    palette: str = "tech",
) -> dict[str, Any]:
    """霓虹发光 — 深色背景 + 强烈发光效果

    适用：科技发布会、游戏主题、赛博朋克风格
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "color",
            "color": "#0B0F19",
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            # 中心发光
            {
                "type": "radial_gradient",
                "color": pal.get("primary", "#8B5CF6"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("primary", "#8B5CF6") + "50", "#00000000"],
                },
                "position": {"x": "30%", "y": "30%", "width": "40%", "height": "40%"},
                "opacity": 0.4,
            },
        ],
        "scrim": [],
        "ornament": [
            # 霓虹灯条（顶部）
            {
                "type": "color",
                "color": pal.get("accent", "#06B6D4"),
                "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": 2},
                "opacity": 0.8,
            },
            # 霓虹灯条（底部）
            {
                "type": "color",
                "color": pal.get("primary", "#8B5CF6"),
                "position": {"x": 0, "y": SLIDE_H - 2, "width": SLIDE_W, "height": 2},
                "opacity": 0.8,
            },
        ],
    }
    return board

def gradient_abstract(
    palette: str = "ocean",
) -> dict[str, Any]:
    """抽象渐变 — 多色渐变叠加 + 抽象形状

    适用：艺术展示、创意设计、多彩主题
    """
    pal = _palette_colors(palette)
    board: dict[str, Any] = {
        "background": {
            "type": "gradient",
            "gradient": {
                "type": "linear",
                "angle": 135,
                "stops": [
                    pal.get("bg", "#0B0F19"),
                    pal.get("bg_alt", "#111827"),
                ],
            },
            "position": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H},
        },
        "illustration": [
            # 左上角渐变
            {
                "type": "radial_gradient",
                "color": pal.get("primary", "#0EA5E9"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("primary", "#0EA5E9") + "40", "#00000000"],
                },
                "position": {"x": 0, "y": 0, "width": "50%", "height": "50%"},
                "opacity": 0.3,
            },
            # 右下角渐变
            {
                "type": "radial_gradient",
                "color": pal.get("accent", "#8B5CF6"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("accent", "#8B5CF6") + "30", "#00000000"],
                },
                "position": {"x": "50%", "y": "50%", "width": "50%", "height": "50%"},
                "opacity": 0.25,
            },
            # 中心点缀
            {
                "type": "radial_gradient",
                "color": pal.get("secondary", "#38BDF8"),
                "gradient": {
                    "type": "radial",
                    "stops": [pal.get("secondary", "#38BDF8") + "20", "#00000000"],
                },
                "position": {"x": "35%", "y": "35%", "width": "30%", "height": "30%"},
                "opacity": 0.2,
            },
        ],
        "scrim": [],
        "ornament": [],
    }
    return board


