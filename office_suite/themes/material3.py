"""Material Design 3 主题 — Google 的动态配色系统

特点：
  - 从种子色自动生成完整色系
  - Tonal palette（色调调色板）
  - 圆角、阴影、层次感
  - 适合 Android/Web 应用风格的文档
"""

from .engine import (
    Theme, ThemeColors, ThemeTypography, ThemeSpacing, ThemeEffects,
    register_theme,
)


def _seed_to_palette(seed: str) -> dict[str, str]:
    """从种子色生成 Material 3 色系（简化版）

    真实的 Material 3 使用 HCT 色彩空间，这里用简化近似。
    """
    h = seed.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def _shift(dr, dg, db, factor=1.0):
        nr = min(255, max(0, r + int(dr * factor)))
        ng = min(255, max(0, g + int(dg * factor)))
        nb = min(255, max(0, b + int(db * factor)))
        return f"#{nr:02X}{ng:02X}{nb:02X}"

    return {
        "primary": seed,
        "on_primary": "#FFFFFF",
        "primary_container": _shift(80, 80, 80),
        "on_primary_container": _shift(-60, -60, -60),
        "secondary": _shift(40, 20, -20),
        "on_secondary": "#FFFFFF",
        "secondary_container": _shift(90, 80, 70),
        "surface": "#FFFBFE",
        "on_surface": "#1C1B1F",
        "surface_variant": "#E7E0EC",
        "on_surface_variant": "#49454F",
        "outline": "#79747E",
        "outline_variant": "#CAC4D0",
        "error": "#B3261E",
        "on_error": "#FFFFFF",
    }


def create_material3_light(seed_color: str = "#6750A4") -> Theme:
    """创建 Material Design 3 浅色主题"""
    palette = _seed_to_palette(seed_color)
    return Theme(
        name="material3_light",
        display_name="Material Design 3 (Light)",
        colors=ThemeColors(
            primary=palette["primary"],
            secondary=palette["secondary"],
            accent=palette["primary_container"],
            background=palette["surface"],
            surface=palette["surface_variant"],
            text_primary=palette["on_surface"],
            text_secondary=palette["on_surface_variant"],
            text_inverse=palette["on_primary"],
            border=palette["outline"],
            error=palette["error"],
            success="#386A20",
            warning="#7D5700",
        ),
        typography=ThemeTypography(
            title_font="Roboto, sans-serif",
            body_font="Roboto, sans-serif",
            mono_font="Roboto Mono, monospace",
            base_size=14,
            scale_ratio=1.25,
        ),
        spacing=ThemeSpacing(
            unit=4,
            xs=4, sm=8, md=16, lg=24, xl=32,
        ),
        effects=ThemeEffects(
            border_radius=12,
            shadow="0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
            blur=4,
        ),
    )


def create_material3_dark(seed_color: str = "#6750A4") -> Theme:
    """创建 Material Design 3 深色主题"""
    palette = _seed_to_palette(seed_color)
    return Theme(
        name="material3_dark",
        display_name="Material Design 3 (Dark)",
        colors=ThemeColors(
            primary=palette["primary_container"],
            secondary=palette["secondary_container"],
            accent=palette["primary"],
            background="#1C1B1F",
            surface="#2B2930",
            text_primary="#E6E1E5",
            text_secondary="#CAC4D0",
            text_inverse="#1C1B1F",
            border="#49454F",
            error="#F2B8B5",
            success="#A8DAB5",
            warning="#FFDDB3",
        ),
        typography=ThemeTypography(
            title_font="Roboto, sans-serif",
            body_font="Roboto, sans-serif",
            mono_font="Roboto Mono, monospace",
            base_size=14,
            scale_ratio=1.25,
        ),
        spacing=ThemeSpacing(
            unit=4,
            xs=4, sm=8, md=16, lg=24, xl=32,
        ),
        effects=ThemeEffects(
            border_radius=12,
            shadow="0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.6)",
            blur=4,
        ),
    )


# 注册默认 Material 3 主题
register_theme(create_material3_light())
register_theme(create_material3_dark())
