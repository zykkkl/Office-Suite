"""程序化纹理生成器 — 纯代码几何图案，无外部依赖

提供可复用的背景纹理和装饰图案，通过 DSL 元素列表表达，
可在 YAML 中通过 Python 脚本引用，或直接在代码中生成。

用法：
    from office_suite.design.patterns import dot_grid, line_grid, hex_grid
    elements += dot_grid(density=0.3, color="#E2E8F0")
"""

from __future__ import annotations

import math
from typing import Any

from ..constants import SLIDE_WIDTH_MM, SLIDE_HEIGHT_MM


def dot_grid(
    density: float = 0.3,
    color: str = "#E2E8F0",
    opacity: float = 0.6,
    slide_w: float = SLIDE_WIDTH_MM,
    slide_h: float = SLIDE_HEIGHT_MM,
) -> list[dict[str, Any]]:
    """点阵背景 — 均匀分布的圆点

    Args:
        density: 点间距系数 (0.1-1.0)，越小点越密集
        color: 点的颜色
        opacity: 点的不透明度
        slide_w, slide_h: 幻灯片尺寸 (mm)
    """
    spacing = max(4.0, 20.0 * density)
    radius = max(0.3, spacing * 0.08)
    elements = []
    x = spacing
    while x < slide_w:
        y = spacing
        while y < slide_h:
            elements.append({
                "type": "shape",
                "shape_type": "circle",
                "position": {"x": x, "y": y, "width": radius * 2, "height": radius * 2},
                "style": {"fill": {"color": color}, "opacity": opacity},
            })
            y += spacing
        x += spacing
    return elements


def line_grid(
    spacing: float = 10.0,
    color: str = "#E2E8F0",
    opacity: float = 0.4,
    angle: float = 0,
    slide_w: float = SLIDE_WIDTH_MM,
    slide_h: float = SLIDE_HEIGHT_MM,
) -> list[dict[str, Any]]:
    """斜线网格 / 横竖网格背景

    Args:
        spacing: 线间距 (mm)
        color: 线颜色
        opacity: 线不透明度
        angle: 线角度 (0=横竖, 45=斜线)
        slide_w, slide_h: 幻灯片尺寸
    """
    elements = []
    if angle == 0:
        # 横竖网格
        for x in range(int(spacing), int(slide_w), int(spacing)):
            elements.append({
                "type": "shape",
                "shape_type": "line",
                "position": {"x": x, "y": 0, "width": 0, "height": slide_h},
                "style": {"border": {"color": color, "width": 0.3}, "opacity": opacity},
            })
        for y in range(int(spacing), int(slide_h), int(spacing)):
            elements.append({
                "type": "shape",
                "shape_type": "line",
                "position": {"x": 0, "y": y, "width": slide_w, "height": 0},
                "style": {"border": {"color": color, "width": 0.3}, "opacity": opacity},
            })
    else:
        # 斜线网格
        rad = math.radians(angle)
        dx = math.cos(rad) * spacing
        dy = math.sin(rad) * spacing
        # 从左上角开始画斜线
        for i in range(-int(slide_h / spacing) - 5, int(slide_w / spacing) + 5):
            start_x = i * dx
            start_y = 0
            end_x = start_x + slide_h / math.tan(rad) if math.tan(rad) != 0 else start_x
            end_y = slide_h
            # 裁剪到幻灯片边界
            if start_x < 0:
                start_y = -start_x * math.tan(rad)
                start_x = 0
            if end_x > slide_w:
                end_y = slide_h - (end_x - slide_w) * math.tan(rad)
                end_x = slide_w
            elements.append({
                "type": "shape",
                "shape_type": "line",
                "position": {"x": start_x, "y": start_y, "width": end_x - start_x, "height": end_y - start_y},
                "style": {"border": {"color": color, "width": 0.3}, "opacity": opacity},
            })
    return elements


def hex_grid(
    size: float = 6.0,
    color: str = "#CBD5E1",
    opacity: float = 0.25,
    slide_w: float = SLIDE_WIDTH_MM,
    slide_h: float = SLIDE_HEIGHT_MM,
) -> list[dict[str, Any]]:
    """六边形蜂窝网格背景

    Args:
        size: 六边形边长 (mm)
        color: 六边形边框颜色
        opacity: 不透明度
    """
    elements = []
    w = size * math.sqrt(3)
    h = size * 2
    row = 0
    y = 0
    while y < slide_h + h:
        x_offset = (w / 2) if (row % 2) else 0
        x = x_offset - w
        while x < slide_w + w:
            elements.append({
                "type": "shape",
                "shape_type": "hexagon",
                "position": {"x": x, "y": y, "width": w, "height": size * 1.5},
                "style": {"fill": {"color": "#00000000"}, "border": {"color": color, "width": 0.4}, "opacity": opacity},
            })
            x += w
        y += size * 1.5
        row += 1
    return elements


def wave_bottom(
    color: str = "#E2E8F0",
    opacity: float = 0.5,
    amplitude: float = 6.0,
    wavelength: float = 40.0,
    y_base: float = 120.0,
    slide_w: float = SLIDE_WIDTH_MM,
) -> list[dict[str, Any]]:
    """底部波浪装饰 — 用多个小线段近似正弦波

    Args:
        color: 波浪线颜色
        opacity: 不透明度
        amplitude: 波峰高度 (mm)
        wavelength: 波长 (mm)
        y_base: 波浪基线 Y 坐标
    """
    elements = []
    segments = int(slide_w / 2)
    for i in range(segments):
        x1 = i * 2
        x2 = (i + 1) * 2
        y1 = y_base + amplitude * math.sin(2 * math.pi * x1 / wavelength)
        y2 = y_base + amplitude * math.sin(2 * math.pi * x2 / wavelength)
        elements.append({
            "type": "shape",
            "shape_type": "line",
            "position": {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1},
            "style": {"border": {"color": color, "width": 0.8}, "opacity": opacity},
        })
    return elements


def concentric_circles(
    center_x: float = SLIDE_WIDTH_MM / 2,
    center_y: float = SLIDE_HEIGHT_MM / 2,
    max_radius: float = 100.0,
    step: float = 12.0,
    color: str = "#CBD5E1",
    opacity: float = 0.2,
    line_width: float = 0.4,
) -> list[dict[str, Any]]:
    """同心圆扩散装饰

    Args:
        center_x, center_y: 圆心坐标
        max_radius: 最大半径
        step: 圆环间距
        color: 圆环颜色
        opacity: 不透明度
        line_width: 线宽
    """
    elements = []
    r = step
    while r <= max_radius:
        elements.append({
            "type": "shape",
            "shape_type": "circle",
            "position": {"x": center_x - r, "y": center_y - r, "width": r * 2, "height": r * 2},
            "style": {"fill": {"color": "#00000000"}, "border": {"color": color, "width": line_width}, "opacity": opacity},
        })
        r += step
    return elements


def diagonal_stripes(
    color: str = "#F1F5F9",
    opacity: float = 0.6,
    spacing: float = 8.0,
    stripe_width: float = 2.0,
    angle: float = 45,
    slide_w: float = SLIDE_WIDTH_MM,
    slide_h: float = SLIDE_HEIGHT_MM,
) -> list[dict[str, Any]]:
    """斜条纹背景 — 用平行四边形条带模拟

    Args:
        color: 条纹颜色
        opacity: 不透明度
        spacing: 条纹中心间距
        stripe_width: 条纹宽度
        angle: 倾斜角度 (度)
        slide_w, slide_h: 幻灯片尺寸
    """
    elements = []
    rad = math.radians(angle)
    # 对角线长度
    diag = math.sqrt(slide_w ** 2 + slide_h ** 2)
    count = int(diag / spacing) + 5
    offset = -diag / 2

    for i in range(count):
        base = offset + i * spacing
        # 条纹的四个角（简化为矩形旋转，用 shape 的 rotation 属性）
        # 实际上 pptx 形状可以直接旋转，但 DSL 中没有 rotation
        # 改用细长的矩形 + 从一端画到另一端
        elements.append({
            "type": "shape",
            "shape_type": "rectangle",
            "position": {"x": 0, "y": base, "width": slide_w, "height": stripe_width},
            "style": {"fill": {"color": color}, "opacity": opacity},
        })
    return elements


def corner_dots(
    color: str = "#94A3B8",
    opacity: float = 0.3,
    size: float = 1.5,
    spacing: float = 5.0,
    count: int = 5,
    corner: str = "top-left",
) -> list[dict[str, Any]]:
    """角落点阵装饰 — 从角落向外扩散的小圆点

    Args:
        color: 点颜色
        opacity: 不透明度
        size: 点直径 (mm)
        spacing: 点间距
        count: 每行/列点数
        corner: 角落位置 (top-left, top-right, bottom-left, bottom-right)
    """
    elements = []
    base_x = 0 if "left" in corner else SLIDE_WIDTH_MM - size
    base_y = 0 if "top" in corner else SLIDE_HEIGHT_MM - size
    sign_x = 1 if "left" in corner else -1
    sign_y = 1 if "top" in corner else -1

    for i in range(count):
        for j in range(count - i):
            x = base_x + sign_x * i * spacing
            y = base_y + sign_y * j * spacing
            elements.append({
                "type": "shape",
                "shape_type": "circle",
                "position": {"x": x, "y": y, "width": size, "height": size},
                "style": {"fill": {"color": color}, "opacity": opacity},
            })
    return elements
