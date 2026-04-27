"""通用主题 — 跨行业通用的简洁设计

设计方案第十章：P0 实现 Fluent + 通用主题。

通用主题特点：
  - 中性配色，适合所有行业
  - 清晰的层次结构
  - 平衡的留白与信息密度
  - 兼容深色/浅色模式
"""

from .engine import (
    Theme, ThemeColors, ThemeTypography, ThemeSpacing, ThemeEffects,
    register_theme,
)


def create_universal_light() -> Theme:
    """创建通用浅色主题"""
    colors = ThemeColors(
        primary="#1E3A5F",
        primary_light="#4A90D9",
        primary_dark="#0F2440",
        secondary="#6B7280",
        secondary_light="#9CA3AF",
        accent="#D97706",
        success="#059669",
        warning="#D97706",
        error="#DC2626",
        info="#2563EB",
        background="#FFFFFF",
        surface="#F9FAFB",
        surface_alt="#F3F4F6",
        text_primary="#111827",
        text_secondary="#6B7280",
        text_disabled="#9CA3AF",
        text_inverse="#FFFFFF",
        border="#E5E7EB",
        border_light="#F3F4F6",
        divider="#E5E7EB",
    )

    typography = ThemeTypography(
        heading_font="Microsoft YaHei UI",
        body_font="Microsoft YaHei UI",
        mono_font="Consolas",
        display_size=40,
        h1_size=32,
        h2_size=26,
        h3_size=20,
        body_size=14,
        caption_size=11,
        small_size=9,
        weight_regular=400,
        weight_medium=500,
        weight_bold=700,
        line_height=1.6,
    )

    spacing = ThemeSpacing(
        xs=2, sm=4, md=8, lg=16, xl=24, xxl=32,
        page_margin=20,
        element_gap=10,
    )

    effects = ThemeEffects(
        shadow_sm="0 1px 3px rgba(0,0,0,0.06)",
        shadow_md="0 4px 6px rgba(0,0,0,0.08)",
        shadow_lg="0 10px 20px rgba(0,0,0,0.12)",
        radius_sm=2,
        radius_md=4,
        radius_lg=6,
        border_width=1,
    )

    presets = {
        "title_slide": {
            "font": {
                "family": "Microsoft YaHei UI",
                "size": 40,
                "weight": 700,
                "color": "#FFFFFF",
            },
            "fill": {"color": "#1E3A5F"},
        },
        "section_header": {
            "font": {
                "family": "Microsoft YaHei UI",
                "size": 26,
                "weight": 700,
                "color": "#1E3A5F",
            },
        },
        "card": {
            "fill": {"color": "#FFFFFF"},
            "border": {"color": "#E5E7EB", "width": 1},
        },
        "data_highlight": {
            "font": {
                "family": "Microsoft YaHei UI",
                "size": 36,
                "weight": 700,
                "color": "#1E3A5F",
            },
        },
        "subtitle": {
            "font": {
                "family": "Microsoft YaHei UI",
                "size": 18,
                "weight": 400,
                "color": "#6B7280",
            },
        },
    }

    return Theme(
        name="universal",
        display_name="Universal",
        mode="light",
        colors=colors,
        typography=typography,
        spacing=spacing,
        effects=effects,
        presets=presets,
        metadata={
            "description": "跨行业通用的简洁设计主题",
            "version": "1.0",
        },
    )


def create_universal_dark() -> Theme:
    """创建通用深色主题"""
    base = create_universal_light()

    colors = ThemeColors(
        primary="#60A5FA",
        primary_light="#93C5FD",
        primary_dark="#3B82F6",
        secondary="#9CA3AF",
        secondary_light="#D1D5DB",
        accent="#FBBF24",
        success="#34D399",
        warning="#FBBF24",
        error="#F87171",
        info="#60A5FA",
        background="#111827",
        surface="#1F2937",
        surface_alt="#374151",
        text_primary="#F9FAFB",
        text_secondary="#9CA3AF",
        text_disabled="#6B7280",
        text_inverse="#111827",
        border="#374151",
        border_light="#1F2937",
        divider="#374151",
    )

    return Theme(
        name="universal_dark",
        display_name="Universal (Dark)",
        mode="dark",
        colors=colors,
        typography=base.typography,
        spacing=base.spacing,
        effects=base.effects,
        presets=base.presets,
        metadata=base.metadata,
    )


# 自动注册
register_theme(create_universal_light())
register_theme(create_universal_dark())
