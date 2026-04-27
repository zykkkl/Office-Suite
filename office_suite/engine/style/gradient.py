"""渐变系统 — 线性/径向/锥形渐变

设计方案第七章：样式引擎。

渐变在渲染器中的实现方式：
  - PPTX: XML 渐变填充 <a:gradFill>
  - HTML: CSS linear-gradient / radial-gradient
  - PDF: reportlab 渐变
  - DOCX: 有限支持（降级为纯色）

本模块提供渐变解析、插值和渲染器适配。
"""

import math
from dataclasses import dataclass, field
from typing import Any

from ...ir.style_spec import GradientSpec, GradientStop, hex_to_rgb


@dataclass
class ColorStop:
    """渐变色标（内部表示）"""
    r: int
    g: int
    b: int
    position: float  # 0.0 - 1.0
    alpha: float = 1.0


def parse_gradient(raw: dict) -> GradientSpec:
    """从 DSL 字典解析渐变规格

    Args:
        raw: DSL 渐变字典

    Returns:
        GradientSpec 实例
    """
    stops = []
    for stop in raw.get("stops", []):
        if isinstance(stop, str):
            # 简写：只传颜色，自动均匀分布
            stops.append(GradientStop(color=stop))
        elif isinstance(stop, dict):
            stops.append(GradientStop(
                color=stop.get("color", "#000000"),
                position=stop.get("position", 0.0),
            ))

    # 自动分配位置
    if stops and all(s.position == 0.0 for s in stops):
        for i, s in enumerate(stops):
            stops[i] = GradientStop(color=s.color, position=i / max(1, len(stops) - 1))

    return GradientSpec(
        type=raw.get("type", "linear"),
        angle=raw.get("angle", 0.0),
        stops=stops,
    )


def interpolate_color(color1: tuple[int, int, int], color2: tuple[int, int, int],
                       t: float) -> tuple[int, int, int]:
    """线性插值两个颜色

    Args:
        color1: 起始颜色 (r, g, b)
        color2: 结束颜色 (r, g, b)
        t: 插值因子 (0.0 - 1.0)

    Returns:
        插值后的颜色 (r, g, b)
    """
    return (
        round(color1[0] + (color2[0] - color1[0]) * t),
        round(color1[1] + (color2[1] - color1[1]) * t),
        round(color1[2] + (color2[2] - color1[2]) * t),
    )


def evaluate_gradient(gradient: GradientSpec, t: float) -> tuple[int, int, int]:
    """在渐变上的指定位置取色

    Args:
        gradient: 渐变规格
        t: 位置 (0.0 - 1.0)

    Returns:
        颜色 (r, g, b)
    """
    if not gradient.stops:
        return (0, 0, 0)

    if len(gradient.stops) == 1:
        return hex_to_rgb(gradient.stops[0].color)

    t = max(0.0, min(1.0, t))

    # 找到 t 所在的区间
    for i in range(len(gradient.stops) - 1):
        s1 = gradient.stops[i]
        s2 = gradient.stops[i + 1]
        if s1.position <= t <= s2.position:
            # 归一化 t 到区间内
            if s2.position == s1.position:
                local_t = 0.0
            else:
                local_t = (t - s1.position) / (s2.position - s1.position)
            return interpolate_color(hex_to_rgb(s1.color), hex_to_rgb(s2.color), local_t)

    # 超出范围，返回最近的色标
    if t <= gradient.stops[0].position:
        return hex_to_rgb(gradient.stops[0].color)
    return hex_to_rgb(gradient.stops[-1].color)


def generate_css(gradient: GradientSpec) -> str:
    """生成 CSS 渐变字符串

    Args:
        gradient: 渐变规格

    Returns:
        CSS 渐变字符串，如 "linear-gradient(135deg, #FF0000 0%, #00FF00 100%)"
    """
    if not gradient.stops:
        return "none"

    stops_css = []
    for s in gradient.stops:
        pos = f"{s.position * 100:.0f}%"
        stops_css.append(f"{s.color} {pos}")

    if gradient.type == "radial":
        return f"radial-gradient(circle, {', '.join(stops_css)})"
    else:
        # CSS 角度与 DSL 角度不同：DSL 用度数，CSS 用 from-top 顺时针
        css_angle = (90 - gradient.angle) % 360
        return f"linear-gradient({css_angle}deg, {', '.join(stops_css)})"


def generate_pptx_xml(gradient: GradientSpec) -> str:
    """生成 PPTX 渐变 XML

    Args:
        gradient: 渐变规格

    Returns:
        <a:gradFill> XML 片段
    """
    if not gradient.stops:
        return ""

    # PPTX 角度：60000ths of a degree, 0 = 左→右
    pptx_angle = int(gradient.angle * 60000)

    stops_xml = []
    for s in gradient.stops:
        r, g, b = hex_to_rgb(s.color)
        pos_pct = int(s.position * 100000)
        stops_xml.append(
            f'<a:gs pos="{pos_pct}">'
            f'<a:srgbClr val="{r:02X}{g:02X}{b:02X}"/>'
            f'</a:gs>'
        )

    if gradient.type == "radial":
        return (
            '<a:gradFill tileRect="l" flip="none" rotWithShape="1">'
            f'<a:gsLst>{"".join(stops_xml)}</a:gsLst>'
            '<a:path path="circle">'
            '<a:fillToRect l="50000" t="50000" r="50000" b="50000"/>'
            '</a:path>'
            '</a:gradFill>'
        )
    else:
        return (
            '<a:gradFill tileRect="l" flip="none" rotWithShape="1">'
            f'<a:gsLst>{"".join(stops_xml)}</a:gsLst>'
            f'<a:lin ang="{pptx_angle}" scaled="1"/>'
            '</a:gradFill>'
        )


def gradient_to_color_list(gradient: GradientSpec, steps: int = 10) -> list[tuple[int, int, int]]:
    """将渐变离散为颜色列表（用于不支持渐变的渲染器）

    Args:
        gradient: 渐变规格
        steps: 离散步数

    Returns:
        颜色列表
    """
    colors = []
    for i in range(steps):
        t = i / max(1, steps - 1)
        colors.append(evaluate_gradient(gradient, t))
    return colors
