"""Microsoft Fluent Design 主题

设计方案第十章：Fluent Design — 桌面原生感，与 PPTX 生态最贴近。

设计令牌来源于 Microsoft Fluent UI:
  - 配色: 品牌蓝 + 中性灰体系
  - 排版: Segoe UI 字体族
  - 圆角: 轻微圆角 (4px)
  - 阴影: 层级阴影
  - 间距: 4px 基础网格

P0 实现完整的 light 模式。
"""

from .engine import (
    Theme, ThemeColors, ThemeTypography, ThemeSpacing, ThemeEffects,
    register_theme,
)


def create_fluent_light() -> Theme:
    """创建 Fluent Design 浅色主题"""
    colors = ThemeColors(
        # 品牌蓝
        primary="#0078D4",
        primary_light="#60CDFF",
        primary_dark="#005A9E",
        # 辅助紫
        secondary="#8764B8",
        secondary_light="#B4A0FF",
        # 强调
        accent="#0078D4",
        # 语义
        success="#107C10",
        warning="#FFB900",
        error="#D13438",
        info="#0078D4",
        # 背景
        background="#FFFFFF",
        surface="#F5F5F5",
        surface_alt="#FAFAFA",
        # 文本
        text_primary="#242424",
        text_secondary="#616161",
        text_disabled="#A0A0A0",
        text_inverse="#FFFFFF",
        # 边框
        border="#E0E0E0",
        border_light="#F0F0F0",
        # 分割线
        divider="#E0E0E0",
    )

    typography = ThemeTypography(
        heading_font="Segoe UI",
        body_font="Segoe UI",
        mono_font="Cascadia Code",
        display_size=42,
        h1_size=34,
        h2_size=28,
        h3_size=22,
        body_size=14,
        caption_size=12,
        small_size=10,
        weight_regular=400,
        weight_medium=600,
        weight_bold=700,
        line_height=1.4,
    )

    spacing = ThemeSpacing(
        xs=2, sm=4, md=8, lg=16, xl=24, xxl=32,
        page_margin=20,
        element_gap=12,
    )

    effects = ThemeEffects(
        shadow_sm="0 2px 4px rgba(0,0,0,0.04)",
        shadow_md="0 4px 8px rgba(0,0,0,0.08)",
        shadow_lg="0 8px 16px rgba(0,0,0,0.14)",
        radius_sm=2,
        radius_md=4,
        radius_lg=8,
        border_width=1,
    )

    # 样式预设
    presets = {
        "title_slide": {
            "font": {
                "family": "Segoe UI",
                "size": 42,
                "weight": 700,
                "color": "#FFFFFF",
            },
            "fill": {"color": "#0078D4"},
        },
        "section_header": {
            "font": {
                "family": "Segoe UI",
                "size": 28,
                "weight": 700,
                "color": "#0078D4",
            },
        },
        "card": {
            "fill": {"color": "#FFFFFF"},
            "border": {"color": "#E0E0E0", "width": 1},
            "shadow": {"blur": 4, "offset": [0, 2], "color": "rgba(0,0,0,0.08)"},
        },
        "highlight": {
            "font": {
                "family": "Segoe UI",
                "size": 14,
                "weight": 600,
                "color": "#0078D4",
            },
        },
        "footer": {
            "font": {
                "family": "Segoe UI",
                "size": 10,
                "color": "#A0A0A0",
            },
        },
    }

    return Theme(
        name="fluent",
        display_name="Microsoft Fluent Design",
        mode="light",
        colors=colors,
        typography=typography,
        spacing=spacing,
        effects=effects,
        presets=presets,
        metadata={
            "author": "Microsoft",
            "version": "1.0",
            "reference": "https://fluent2.microsoft.design/",
        },
    )


def create_fluent_dark() -> Theme:
    """创建 Fluent Design 深色主题"""
    base = create_fluent_light()

    colors = ThemeColors(
        primary="#60CDFF",
        primary_light="#98DFFF",
        primary_dark="#0078D4",
        secondary="#B4A0FF",
        secondary_light="#D0C0FF",
        accent="#60CDFF",
        success="#6CCB5F",
        warning="#FCE100",
        error="#FF99A4",
        info="#60CDFF",
        background="#202020",
        surface="#2D2D2D",
        surface_alt="#383838",
        text_primary="#FFFFFF",
        text_secondary="#A0A0A0",
        text_disabled="#616161",
        text_inverse="#242424",
        border="#404040",
        border_light="#333333",
        divider="#404040",
    )

    return Theme(
        name="fluent_dark",
        display_name="Microsoft Fluent Design (Dark)",
        mode="dark",
        colors=colors,
        typography=base.typography,
        spacing=base.spacing,
        effects=base.effects,
        presets=base.presets,
        metadata=base.metadata,
    )


# 自动注册
register_theme(create_fluent_light())
register_theme(create_fluent_dark())
