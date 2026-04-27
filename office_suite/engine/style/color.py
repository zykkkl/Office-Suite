"""色彩空间引擎 — OKLCH + sRGB 转换

设计方案第四章：色彩空间。

OKLCH 是感知均匀的色彩空间，比 HEX/RGB 更适合设计：
  - L (Lightness): 0-1 亮度
  - C (Chroma): 0-0.4 饱和度
  - H (Hue): 0-360 色相

优势：
  - 相同 L 值的不同颜色视觉亮度一致
  - 自动处理对比度和无障碍适配
  - 渐变更自然（无灰色中间态）

P0 使用 sRGB/HEX，OKLCH 作为 P1 增强特性。
本模块提供双向转换 + 设计辅助函数。
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class OKLCH:
    """OKLCH 色彩"""
    l: float = 0.0   # Lightness: 0.0 - 1.0
    c: float = 0.0   # Chroma: 0.0 - 0.4
    h: float = 0.0   # Hue: 0.0 - 360.0


@dataclass(frozen=True)
class OKLAB:
    """OKLAB 色彩"""
    l: float = 0.0
    a: float = 0.0
    b: float = 0.0


@dataclass(frozen=True)
class SRGB:
    """sRGB 色彩 (0-255)"""
    r: int = 0
    g: int = 0
    b: int = 0


# ============================================================
# sRGB ↔ 线性 RGB
# ============================================================

def srgb_to_linear(c: float) -> float:
    """sRGB 分量 → 线性 (0-1)"""
    c = c / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    """线性 → sRGB 分量 (0-255)"""
    if c <= 0.0031308:
        v = c * 12.92
    else:
        v = 1.055 * (c ** (1.0 / 2.4)) - 0.055
    return max(0, min(255, round(v * 255)))


# ============================================================
# sRGB ↔ OKLAB
# ============================================================

def srgb_to_oklab(r: int, g: int, b: int) -> OKLAB:
    """sRGB → OKLAB"""
    lr = srgb_to_linear(r)
    lg = srgb_to_linear(g)
    lb = srgb_to_linear(b)

    l_ = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
    m_ = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
    s_ = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb

    l_c = l_ ** (1 / 3)
    m_c = m_ ** (1 / 3)
    s_c = s_ ** (1 / 3)

    return OKLAB(
        l=0.2104542553 * l_c + 0.7936177850 * m_c - 0.0040720468 * s_c,
        a=1.9779984951 * l_c - 2.4285922050 * m_c + 0.4505937099 * s_c,
        b=0.0259040371 * l_c + 0.7827717662 * m_c - 0.8086757660 * s_c,
    )


def oklab_to_srgb(lab: OKLAB) -> SRGB:
    """OKLAB → sRGB"""
    l_ = lab.l + 0.3963377774 * lab.a + 0.2158037573 * lab.b
    m_ = lab.l - 0.1055613458 * lab.a - 0.0638541728 * lab.b
    s_ = lab.l - 0.0894841775 * lab.a - 1.2914855480 * lab.b

    l = l_ * l_ * l_
    m = m_ * m_ * m_
    s = s_ * s_ * s_

    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    return SRGB(
        r=linear_to_srgb(max(0, min(1, r))),
        g=linear_to_srgb(max(0, min(1, g))),
        b=linear_to_srgb(max(0, min(1, b))),
    )


# ============================================================
# OKLAB ↔ OKLCH
# ============================================================

def oklab_to_oklch(lab: OKLAB) -> OKLCH:
    """OKLAB → OKLCH"""
    c = math.sqrt(lab.a ** 2 + lab.b ** 2)
    h = math.degrees(math.atan2(lab.b, lab.a)) % 360
    return OKLCH(l=lab.l, c=c, h=h)


def oklch_to_oklab(lch: OKLCH) -> OKLAB:
    """OKLCH → OKLAB"""
    h_rad = math.radians(lch.h)
    return OKLAB(
        l=lch.l,
        a=lch.c * math.cos(h_rad),
        b=lch.c * math.sin(h_rad),
    )


# ============================================================
# 完整转换链
# ============================================================

def hex_to_oklch(hex_color: str) -> OKLCH:
    """HEX → OKLCH"""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    lab = srgb_to_oklab(r, g, b)
    return oklab_to_oklch(lab)


def oklch_to_hex(lch: OKLCH) -> str:
    """OKLCH → HEX"""
    lab = oklch_to_oklab(lch)
    rgb = oklab_to_srgb(lab)
    return f"#{rgb.r:02X}{rgb.g:02X}{rgb.b:02X}"


# ============================================================
# 设计辅助函数
# ============================================================

def adjust_lightness(hex_color: str, delta: float) -> str:
    """调整亮度

    Args:
        hex_color: 输入颜色
        delta: 亮度变化 (-1.0 ~ 1.0)

    Returns:
        调整后的 HEX 颜色
    """
    lch = hex_to_oklch(hex_color)
    new_l = max(0, min(1, lch.l + delta))
    return oklch_to_hex(OKLCH(l=new_l, c=lch.c, h=lch.h))


def adjust_chroma(hex_color: str, factor: float) -> str:
    """调整饱和度

    Args:
        hex_color: 输入颜色
        factor: 饱和度倍数 (0 = 灰色, 1 = 原始, >1 = 更鲜艳)

    Returns:
        调整后的 HEX 颜色
    """
    lch = hex_to_oklch(hex_color)
    new_c = max(0, min(0.4, lch.c * factor))
    return oklch_to_hex(OKLCH(l=lch.l, c=new_c, h=lch.h))


def rotate_hue(hex_color: str, degrees: float) -> str:
    """旋转色相

    Args:
        hex_color: 输入颜色
        degrees: 旋转角度

    Returns:
        调整后的 HEX 颜色
    """
    lch = hex_to_oklch(hex_color)
    new_h = (lch.h + degrees) % 360
    return oklch_to_hex(OKLCH(l=lch.l, c=lch.c, h=new_h))


def generate_palette(hex_color: str, count: int = 5) -> list[str]:
    """从种子色生成配色方案

    通过调整亮度生成一组和谐的颜色。

    Args:
        hex_color: 种子颜色
        count: 生成数量

    Returns:
        HEX 颜色列表
    """
    lch = hex_to_oklch(hex_color)
    palette = []
    step = 0.8 / max(1, count - 1)

    for i in range(count):
        new_l = 0.15 + step * i
        palette.append(oklch_to_hex(OKLCH(l=new_l, c=lch.c, h=lch.h)))

    return palette


def complementary(hex_color: str) -> str:
    """互补色"""
    return rotate_hue(hex_color, 180)


def analogous(hex_color: str, angle: float = 30) -> tuple[str, str]:
    """类似色（左右各偏移 angle 度）"""
    return rotate_hue(hex_color, -angle), rotate_hue(hex_color, angle)


def triadic(hex_color: str) -> tuple[str, str]:
    """三角色（120 度间隔）"""
    return rotate_hue(hex_color, 120), rotate_hue(hex_color, 240)
