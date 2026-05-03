"""形状装饰工具箱 — 轻量级几何装饰元素

提供可复用的装饰形状函数，解决"元素过于单一、缺少细节"的问题。
所有装饰均为纯几何形状（无外部图片依赖），通过 DSL 元素列表表达。

用法：
    from office_suite.design.ornaments import corner_ribbon, bottom_wave, side_accent_bar
    elements += corner_ribbon(color="#F97316", position="top-right", text="NEW")
"""

from __future__ import annotations

from typing import Any

from ..constants import SLIDE_WIDTH_MM as SLIDE_W, SLIDE_HEIGHT_MM as SLIDE_H


def corner_ribbon(
    color: str = "#F97316",
    text: str = "",
    position: str = "top-right",
    width: float = 35.0,
    height: float = 6.0,
) -> list[dict[str, Any]]:
    """角标丝带 — 幻灯片角落的斜向色条

    Args:
        color: 丝带颜色
        text: 丝带上文字（可选）
        position: 位置 (top-left, top-right, bottom-left, bottom-right)
        width: 丝带长度
        height: 丝带宽度
    """
    elements = []
    # 使用旋转的矩形模拟丝带
    if "top" in position:
        y = 0 if "top" in position else SLIDE_H - height
    else:
        y = SLIDE_H - height

    if "right" in position:
        x = SLIDE_W - width
    else:
        x = 0

    # 旋转角度：右上角和左下角为正 45 度，其他为负 45 度
    rotation = 45 if ("right" in position and "top" in position) or ("left" in position and "bottom" in position) else -45

    elements.append({
        "type": "shape",
        "shape_type": "rectangle",
        "position": {"x": x, "y": y, "width": width, "height": height},
        "style": {"fill": {"color": color}},
    })

    if text:
        # 文字居中在丝带上
        elements.append({
            "type": "text",
            "content": text,
            "position": {"x": x + 2, "y": y + 0.5, "width": width - 4, "height": height - 1},
            "style": {"font": {"size": 10, "weight": 700, "color": "#FFFFFF"}},
            "align": "center",
            "vertical_align": "middle",
        })

    return elements


def bottom_wave(
    color: str = "#E2E8F0",
    opacity: float = 0.5,
    amplitude: float = 4.0,
    wavelength: float = 30.0,
    y_offset: float = 138.0,
    slide_w: float = SLIDE_W,
) -> list[dict[str, Any]]:
    """底部波浪装饰线 — 比 patterns.wave_bottom 更简洁，仅一条线

    Args:
        color: 波浪颜色
        opacity: 不透明度
        amplitude: 波峰高度
        wavelength: 波长
        y_offset: 基线 Y 坐标
    """
    import math
    elements = []
    segments = int(slide_w)
    for i in range(segments):
        x1 = i
        x2 = i + 1
        y1 = y_offset + amplitude * math.sin(2 * math.pi * x1 / wavelength)
        y2 = y_offset + amplitude * math.sin(2 * math.pi * x2 / wavelength)
        elements.append({
            "type": "shape",
            "shape_type": "line",
            "position": {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1},
            "style": {"border": {"color": color, "width": 0.6}, "opacity": opacity},
        })
    return elements


def side_accent_bar(
    color: str = "#2563EB",
    position: str = "left",
    width: float = 2.0,
    margin: float = 20.0,
    slide_h: float = SLIDE_H,
) -> list[dict[str, Any]]:
    """侧边强调条 — 细长的竖向色条

    Args:
        color: 色条颜色
        position: 位置 (left, right)
        width: 色条宽度
        margin: 距离边缘的边距
        slide_h: 幻灯片高度
    """
    x = margin if position == "left" else SLIDE_W - margin - width
    return [{
        "type": "shape",
        "shape_type": "rectangle",
        "position": {"x": x, "y": margin, "width": width, "height": slide_h - margin * 2},
        "style": {"fill": {"color": color}},
    }]


def circle_frame(
    x: float,
    y: float,
    radius: float = 15.0,
    color: str = "#CBD5E1",
    line_width: float = 0.8,
    opacity: float = 0.4,
    filled: bool = False,
    fill_color: str = "#F1F5F9",
) -> list[dict[str, Any]]:
    """圆环装饰框 — 空心或实心圆环

    Args:
        x, y: 圆心坐标
        radius: 半径
        color: 边框颜色
        line_width: 边框宽度
        opacity: 不透明度
        filled: 是否填充
        fill_color: 填充颜色
    """
    style: dict[str, Any] = {"border": {"color": color, "width": line_width}, "opacity": opacity}
    if filled:
        style["fill"] = {"color": fill_color}
    return [{
        "type": "shape",
        "shape_type": "circle",
        "position": {"x": x - radius, "y": y - radius, "width": radius * 2, "height": radius * 2},
        "style": style,
    }]


def underline_accent(
    x: float,
    y: float,
    width: float = 40.0,
    height: float = 2.5,
    color: str = "#2563EB",
    rounded: bool = True,
) -> list[dict[str, Any]]:
    """下划线强调 — 粗短的下划线装饰

    Args:
        x, y: 起始位置
        width: 线宽度
        height: 线粗细
        color: 颜色
        rounded: 是否使用圆角矩形（更柔和）
    """
    shape_type = "rounded_rectangle" if rounded else "rectangle"
    return [{
        "type": "shape",
        "shape_type": shape_type,
        "position": {"x": x, "y": y, "width": width, "height": height},
        "style": {"fill": {"color": color}},
    }]


def gradient_underline(
    x: float,
    y: float,
    width: float = 40.0,
    height: float = 2.5,
    color_start: str = "#1E40AF",
    color_end: str = "#60A5FA",
    angle: int = 0,
    rounded: bool = True,
) -> list[dict[str, Any]]:
    """渐变下划线 — 从 color_start 渐变到 color_end 的强调线

    Args:
        x, y: 起始位置
        width: 线宽度
        height: 线粗细
        color_start: 渐变起始色
        color_end: 渐变结束色
        angle: 渐变角度 (0=从左到右)
        rounded: 是否使用圆角矩形
    """
    shape_type = "rounded_rectangle" if rounded else "rectangle"
    return [{
        "type": "shape",
        "shape_type": shape_type,
        "position": {"x": x, "y": y, "width": width, "height": height},
        "style": {
            "fill_gradient": {
                "type": "linear",
                "angle": angle,
                "stops": [color_start, color_end],
            },
        },
    }]


def gradient_bar(
    x: float,
    y: float,
    width: float,
    height: float,
    color_start: str,
    color_end: str,
    angle: int = 135,
    opacity: float = 1.0,
) -> list[dict[str, Any]]:
    """渐变色块 — 大面积渐变填充的矩形/圆角矩形

    Args:
        x, y: 起始位置
        width, height: 尺寸
        color_start: 渐变起始色
        color_end: 渐变结束色
        angle: 渐变角度
        opacity: 整体不透明度
    """
    return [{
        "type": "shape",
        "shape_type": "rounded_rectangle",
        "position": {"x": x, "y": y, "width": width, "height": height},
        "style": {
            "fill_gradient": {
                "type": "linear",
                "angle": angle,
                "stops": [color_start, color_end],
            },
            "opacity": opacity,
        },
    }]


def divider_line(
    x: float,
    y: float,
    width: float = 194.0,
    color: str = "#E2E8F0",
    thickness: float = 0.5,
    style: str = "solid",
) -> list[dict[str, Any]]:
    """分割线 — 带装饰点的水平分隔线

    Args:
        x, y: 起始位置
        width: 线长度
        color: 颜色
        thickness: 线粗细
        style: 样式 (solid, dotted)
    """
    elements = [{
        "type": "shape",
        "shape_type": "line",
        "position": {"x": x, "y": y, "width": width, "height": 0},
        "style": {"border": {"color": color, "width": thickness}},
    }]
    # 中间装饰点
    if style == "dotted":
        elements.append({
            "type": "shape",
            "shape_type": "circle",
            "position": {"x": x + width / 2 - 1.5, "y": y - 1.5, "width": 3, "height": 3},
            "style": {"fill": {"color": color}},
        })
    return elements


def badge(
    x: float,
    y: float,
    text: str,
    bg_color: str = "#2563EB",
    text_color: str = "#FFFFFF",
    font_size: int = 10,
    padding_x: float = 6.0,
    padding_y: float = 2.5,
) -> list[dict[str, Any]]:
    """徽章标签 — 圆角矩形背景 + 文字

    Args:
        x, y: 位置
        text: 标签文字
        bg_color: 背景色
        text_color: 文字色
        font_size: 字号
        padding_x, padding_y: 内边距
    """
    # 估算文字宽度：每个字符约 0.5 * font_size mm
    text_w = len(str(text)) * font_size * 0.55
    w = text_w + padding_x * 2
    h = font_size * 0.5 + padding_y * 2
    return [
        {
            "type": "shape",
            "shape_type": "rounded_rectangle",
            "position": {"x": x, "y": y, "width": w, "height": h},
            "style": {"fill": {"color": bg_color}},
        },
        {
            "type": "text",
            "content": text,
            "position": {"x": x + padding_x, "y": y + padding_y * 0.5, "width": text_w, "height": h - padding_y},
            "style": {"font": {"size": font_size, "weight": 600, "color": text_color}},
            "align": "center",
            "vertical_align": "middle",
        },
    ]


def arrow_connector(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str = "#94A3B8",
    width: float = 1.0,
) -> list[dict[str, Any]]:
    """箭头连接线 — 带箭头的直线

    Args:
        x1, y1: 起点
        x2, y2: 终点
        color: 颜色
        width: 线宽
    """
    elements = [{
        "type": "shape",
        "shape_type": "line",
        "position": {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1},
        "style": {"border": {"color": color, "width": width}},
    }]
    # 箭头头部（小三角形）
    angle = 0  # 简化：不计算角度，用简单箭头
    arrow_size = 3.0
    elements.append({
        "type": "shape",
        "shape_type": "triangle",
        "position": {"x": x2 - arrow_size, "y": y2 - arrow_size / 2, "width": arrow_size, "height": arrow_size},
        "style": {"fill": {"color": color}},
    })
    return elements
