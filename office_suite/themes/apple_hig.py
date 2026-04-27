"""Apple Human Interface Guidelines 主题

特点：
  - SF Pro 字体体系
  - 克制的色彩、大量留白
  - 毛玻璃效果、圆角
  - 适合 macOS/iOS 风格的文档
"""

from .engine import (
    Theme, ThemeColors, ThemeTypography, ThemeSpacing, ThemeEffects,
    register_theme,
)


def create_apple_hig_light() -> Theme:
    """创建 Apple HIG 浅色主题"""
    return Theme(
        name="apple_hig_light",
        display_name="Apple HIG (Light)",
        colors=ThemeColors(
            primary="#007AFF",
            secondary="#5856D6",
            accent="#FF9500",
            background="#FFFFFF",
            surface="#F2F2F7",
            text_primary="#000000",
            text_secondary="#3C3C43",
            text_inverse="#FFFFFF",
            border="#C6C6C8",
            error="#FF3B30",
            success="#34C759",
            warning="#FF9500",
        ),
        typography=ThemeTypography(
            title_font="SF Pro Display, -apple-system, sans-serif",
            body_font="SF Pro Text, -apple-system, sans-serif",
            mono_font="SF Mono, Menlo, monospace",
            base_size=17,
            scale_ratio=1.2,
        ),
        spacing=ThemeSpacing(
            unit=8,
            xs=4, sm=8, md=16, lg=24, xl=32,
        ),
        effects=ThemeEffects(
            border_radius=10,
            shadow="0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06)",
            blur=20,
        ),
    )


def create_apple_hig_dark() -> Theme:
    """创建 Apple HIG 深色主题"""
    return Theme(
        name="apple_hig_dark",
        display_name="Apple HIG (Dark)",
        colors=ThemeColors(
            primary="#0A84FF",
            secondary="#5E5CE6",
            accent="#FF9F0A",
            background="#000000",
            surface="#1C1C1E",
            text_primary="#FFFFFF",
            text_secondary="#EBEBF5",
            text_inverse="#000000",
            border="#38383A",
            error="#FF453A",
            success="#30D158",
            warning="#FF9F0A",
        ),
        typography=ThemeTypography(
            title_font="SF Pro Display, -apple-system, sans-serif",
            body_font="SF Pro Text, -apple-system, sans-serif",
            mono_font="SF Mono, Menlo, monospace",
            base_size=17,
            scale_ratio=1.2,
        ),
        spacing=ThemeSpacing(
            unit=8,
            xs=4, sm=8, md=16, lg=24, xl=32,
        ),
        effects=ThemeEffects(
            border_radius=10,
            shadow="0 1px 3px rgba(0,0,0,0.3), 0 4px 12px rgba(0,0,0,0.2)",
            blur=20,
        ),
    )


# 注册 Apple HIG 主题
register_theme(create_apple_hig_light())
register_theme(create_apple_hig_dark())
