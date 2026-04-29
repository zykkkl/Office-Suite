"""HTML CSS 生成工具 — 从 dom.py 提取的 CSS 构建逻辑

本模块集中管理 CSS 样式生成函数。

使用方式：
    from office_suite.renderer.html.css import position_css, text_css, shadow_css
"""

from ...ir.types import IRPosition, IRStyle


def position_parts(pos: IRPosition | None) -> list[str]:
    """生成 CSS 定位属性片段"""
    if pos is None:
        return []
    parts = []
    if pos.x_mm >= 0:
        parts.append(f"left: {pos.x_mm}mm")
    if pos.y_mm >= 0:
        parts.append(f"top: {pos.y_mm}mm")
    if pos.width_mm > 0:
        parts.append(f"width: {pos.width_mm}mm")
    if pos.height_mm > 0:
        parts.append(f"height: {pos.height_mm}mm")
    return parts


def position_css(pos: IRPosition | None) -> str:
    """生成 CSS 定位样式"""
    parts = position_parts(pos)
    if not parts:
        return ""
    return "; ".join(parts)


def text_style_parts(style: IRStyle | None) -> list[str]:
    """生成 CSS 文本样式属性片段"""
    if style is None:
        return []
    parts = []
    if style.font_family:
        parts.append(f"font-family: '{style.font_family}', sans-serif")
    if style.font_size:
        parts.append(f"font-size: {style.font_size}pt")
    if style.font_weight:
        parts.append(f"font-weight: {style.font_weight}")
    if style.font_italic:
        parts.append("font-style: italic")
    if style.font_color:
        parts.append(f"color: {style.font_color}")
    return parts


def text_style_css(style: IRStyle | None) -> str:
    """生成 CSS 文本样式"""
    parts = text_style_parts(style)
    return "; ".join(parts) if parts else ""


def shadow_css(shadow: dict | None) -> str:
    """生成 CSS box-shadow"""
    if not shadow:
        return ""
    x = shadow.get("x", 2)
    y = shadow.get("y", 2)
    blur = shadow.get("blur", 4)
    color = shadow.get("color", "rgba(0,0,0,0.3)")
    return f"box-shadow: {x}px {y}px {blur}px {color}"


def border_css(border: dict | None) -> str:
    """生成 CSS border"""
    if not border:
        return ""
    width = border.get("width", 1)
    color = border.get("color", "#000000")
    style = border.get("style", "solid")
    return f"border: {width}px {style} {color}"


def background_css(bg_style: IRStyle | None) -> str:
    """生成 CSS 背景样式"""
    if bg_style is None:
        return ""
    parts = []
    if bg_style.fill_color:
        parts.append(f"background-color: {bg_style.fill_color}")
    if bg_style.fill_gradient:
        grad = bg_style.fill_gradient
        colors = grad.get("colors", [])
        if colors:
            stops = ", ".join(colors)
            parts.append(f"background: linear-gradient({stops})")
    return "; ".join(parts)


def join_css(parts: list[str]) -> str:
    """拼接 CSS 属性列表"""
    return "; ".join(p for p in parts if p)
