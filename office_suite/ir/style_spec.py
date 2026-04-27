"""IR 样式规格 — 定义级联样式系统

样式级联优先级（低→高）：
  theme → document → slide → element → inline

本模块提供样式合并、解析和工具函数。
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FontSpec:
    """字体规格"""
    family: str | None = None
    size: float | None = None      # pt
    weight: int | None = None      # 100-900
    color: str | None = None       # hex
    italic: bool | None = None
    underline: bool | None = None


@dataclass(frozen=True)
class GradientStop:
    """渐变色标"""
    color: str
    position: float = 0.0    # 0.0 - 1.0


@dataclass(frozen=True)
class GradientSpec:
    """渐变规格"""
    type: str = "linear"     # linear / radial
    angle: float = 0.0       # 度
    stops: list[GradientStop] = field(default_factory=list)


@dataclass(frozen=True)
class ShadowSpec:
    """阴影规格"""
    blur: float = 0.0        # mm
    offset_x: float = 0.0    # mm
    offset_y: float = 0.0    # mm
    color: str = "#00000040"
    spread: float = 0.0      # mm


@dataclass(frozen=True)
class FillSpec:
    """填充规格"""
    color: str | None = None
    gradient: GradientSpec | None = None
    image: str | None = None


@dataclass(frozen=True)
class BorderSpec:
    """边框规格"""
    color: str = "#000000"
    width: float = 0.0       # mm
    style: str = "solid"     # solid / dashed / dotted


@dataclass
class StyleSpec:
    """统一样式规格"""
    font: FontSpec | None = None
    fill: FillSpec | None = None
    gradient: GradientSpec | None = None
    shadow: ShadowSpec | None = None
    border: BorderSpec | None = None
    opacity: float | None = None     # 0.0 - 1.0
    text_effect: dict | None = None  # WordArt 变换等

    def merge(self, override: "StyleSpec") -> "StyleSpec":
        """合并样式：override 中非 None 的字段覆盖 self"""
        return StyleSpec(
            font=override.font if override.font is not None else self.font,
            fill=override.fill if override.fill is not None else self.fill,
            gradient=override.gradient if override.gradient is not None else self.gradient,
            shadow=override.shadow if override.shadow is not None else self.shadow,
            border=override.border if override.border is not None else self.border,
            opacity=override.opacity if override.opacity is not None else self.opacity,
            text_effect=override.text_effect if override.text_effect is not None else self.text_effect,
        )


def cascade_styles(layers: list[StyleSpec]) -> StyleSpec:
    """多层样式级联

    Args:
        layers: 样式层列表，从低优先级到高优先级

    Returns:
        合并后的 StyleSpec
    """
    result = StyleSpec()
    for layer in layers:
        result = result.merge(layer)
    return result


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """#RRGGBB → (r, g, b)"""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    """#RRGGBBAA → (r, g, b, a)，无 alpha 时默认 255"""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = hex_to_rgb(h)
        return r, g, b, 255
    if len(h) == 8:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16)
    r, g, b = hex_to_rgb(h)
    return r, g, b, 255


def luminance(hex_color: str) -> float:
    """计算相对亮度（WCAG 2.1）"""
    r, g, b = hex_to_rgb(hex_color)
    rs, gs, bs = r / 255, g / 255, b / 255
    rl = rs / 12.92 if rs <= 0.03928 else ((rs + 0.055) / 1.055) ** 2.4
    gl = gs / 12.92 if gs <= 0.03928 else ((gs + 0.055) / 1.055) ** 2.4
    bl = bs / 12.92 if bs <= 0.03928 else ((bs + 0.055) / 1.055) ** 2.4
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl


def contrast_ratio(color1: str, color2: str) -> float:
    """计算两色对比度（WCAG 2.1）"""
    l1 = luminance(color1)
    l2 = luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)
