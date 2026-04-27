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
            heading_font="SF Pro Display, -apple-system, sans-serif",
            body_font="SF Pro Text, -apple-system, sans-serif",
            mono_font="SF Mono, Menlo, monospace",
            body_size=17,
            h1_size=34,
            h2_size=28,
            h3_size=22,
        ),
        spacing=ThemeSpacing(
            xs=4, sm=8, md=16, lg=24, xl=32, xxl=48,
            page_margin=20,
            element_gap=8,
        ),
        effects=ThemeEffects(
            radius_sm=4,
            radius_md=8,
            radius_lg=12,
            radius_full=999,
            shadow_sm="0 1px 2px rgba(0,0,0,0.08)",
            shadow_md="0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06)",
            shadow_lg="0 4px 12px rgba(0,0,0,0.08), 0 12px 32px rgba(0,0,0,0.06)",
            border_width=1,
        ),
    )


def create_apple_hig_dark() -> Theme:
    """创建 Apple HIG 深色主题"""
    return Theme(
        name="apple_hig_dark",
        display_name="Apple HIG (Dark)",
        mode="dark",
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
            heading_font="SF Pro Display, -apple-system, sans-serif",
            body_font="SF Pro Text, -apple-system, sans-serif",
            mono_font="SF Mono, Menlo, monospace",
            body_size=17,
            h1_size=34,
            h2_size=28,
            h3_size=22,
        ),
        spacing=ThemeSpacing(
            xs=4, sm=8, md=16, lg=24, xl=32, xxl=48,
            page_margin=20,
            element_gap=8,
        ),
        effects=ThemeEffects(
            radius_sm=4,
            radius_md=8,
            radius_lg=12,
            radius_full=999,
            shadow_sm="0 1px 2px rgba(0,0,0,0.3)",
            shadow_md="0 1px 3px rgba(0,0,0,0.3), 0 4px 12px rgba(0,0,0,0.2)",
            shadow_lg="0 4px 12px rgba(0,0,0,0.3), 0 12px 32px rgba(0,0,0,0.2)",
            border_width=1,
        ),
    )


# 注册 Apple HIG 主题
register_theme(create_apple_hig_light())
register_theme(create_apple_hig_dark())
