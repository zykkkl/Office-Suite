"""SVG 处理引擎 — 解析、转码、嵌入

设计方案第七章：媒体处理。

SVG 处理能力：
  - SVG 解析（提取 viewBox、尺寸、元素）
  - SVG → PNG 转码（用于不支持 SVG 的渲染器）
  - SVG 内联嵌入（HTML）
  - SVG → EMF 转换（PPTX 嵌入）

注意：SVG → PNG 需要 cairosvg 或类似库。
本模块优先提供解析和参数提取，转码作为可选增强。
"""

from dataclasses import dataclass
from typing import Any
import re
import xml.etree.ElementTree as ET


@dataclass
class SVGInfo:
    """SVG 文件信息"""
    width: float = 0.0        # 原始宽度
    height: float = 0.0       # 原始高度
    viewBox: str = ""         # viewBox 属性
    view_width: float = 0.0   # viewBox 宽度
    view_height: float = 0.0  # viewBox 高度
    has_text: bool = False    # 是否包含文本
    element_count: int = 0    # 元素数量
    valid: bool = False       # 是否有效 SVG


def parse_svg(svg_content: str | bytes) -> SVGInfo:
    """解析 SVG 内容，提取基本信息

    Args:
        svg_content: SVG 文件内容（字符串或字节）

    Returns:
        SVGInfo 实例
    """
    info = SVGInfo()

    try:
        if isinstance(svg_content, bytes):
            svg_content = svg_content.decode("utf-8")

        # 提取根元素属性（不依赖完整 XML 解析，处理常见的格式变体）
        # 先尝试 XML 解析
        try:
            root = ET.fromstring(svg_content)
        except ET.ParseError:
            # 尝试清理常见问题
            svg_content = re.sub(r'<\?xml[^?]*\?>', '', svg_content)
            root = ET.fromstring(svg_content.strip())

        # 命名空间处理
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"

        if root.tag != f"{ns}svg" and root.tag != "svg":
            return info

        info.valid = True

        # 提取 width / height
        width_str = root.get("width", "")
        height_str = root.get("height", "")
        info.width = _parse_svg_length(width_str)
        info.height = _parse_svg_length(height_str)

        # 提取 viewBox
        viewbox = root.get("viewBox", root.get("viewbox", ""))
        info.viewBox = viewbox
        if viewbox:
            parts = viewbox.replace(",", " ").split()
            if len(parts) == 4:
                try:
                    info.view_width = float(parts[2])
                    info.view_height = float(parts[3])
                except ValueError:
                    pass

        # 如果没有 width/height，使用 viewBox
        if info.width <= 0 and info.view_width > 0:
            info.width = info.view_width
        if info.height <= 0 and info.view_height > 0:
            info.height = info.view_height

        # 检查是否包含文本
        info.has_text = bool(root.iter(f"{ns}text")) or bool(root.iter("text"))

        # 统计元素数量
        info.element_count = sum(1 for _ in root.iter())

    except Exception:
        pass

    return info


def _parse_svg_length(value: str) -> float:
    """解析 SVG 长度值（支持 px, pt, mm, em, % 等单位）

    Returns:
        像素值（近似）
    """
    if not value:
        return 0.0

    value = value.strip()
    match = re.match(r'^([\d.]+)\s*(px|pt|mm|cm|in|em|%)?$', value)
    if not match:
        try:
            return float(value)
        except ValueError:
            return 0.0

    num = float(match.group(1))
    unit = match.group(2) or "px"

    # 转换为像素
    conversions = {
        "px": 1.0,
        "pt": 96 / 72,        # 1pt = 1.333px
        "mm": 96 / 25.4,      # 1mm = 3.78px
        "cm": 96 / 2.54,      # 1cm = 37.8px
        "in": 96,             # 1in = 96px
        "em": 16,             # 假设 1em = 16px
        "%": 1.0,             # 百分比需要上下文，这里返回原始值
    }

    return num * conversions.get(unit, 1.0)


def svg_to_html_embed(svg_content: str, width: float = 0, height: float = 0) -> str:
    """将 SVG 内联嵌入 HTML

    Args:
        svg_content: SVG 原始内容
        width: 指定宽度（覆盖原始值）
        height: 指定高度（覆盖原始值）

    Returns:
        可直接嵌入 HTML 的 SVG 字符串
    """
    if width > 0:
        svg_content = re.sub(r'width="[^"]*"', f'width="{width}"', svg_content)
    if height > 0:
        svg_content = re.sub(r'height="[^"]*"', f'height="{height}"', svg_content)
    return svg_content


def estimate_render_size(
    svg_info: SVGInfo,
    container_width: float,
    container_height: float,
) -> tuple[float, float]:
    """估算 SVG 在容器中的渲染尺寸（保持宽高比）

    Args:
        svg_info: SVG 信息
        container_width: 容器宽度（mm）
        container_height: 容器高度（mm）

    Returns:
        (width, height) mm
    """
    if svg_info.width <= 0 or svg_info.height <= 0:
        return (container_width, container_height)

    aspect = svg_info.width / svg_info.height
    container_aspect = container_width / container_height

    if aspect > container_aspect:
        w = container_width
        h = w / aspect
    else:
        h = container_height
        w = h * aspect

    return (round(w, 2), round(h, 2))
