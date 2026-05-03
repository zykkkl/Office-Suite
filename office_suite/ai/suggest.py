"""设计建议引擎 — 根据 DesignBrief 推荐布局/配色/排版

设计方案第九章：
  - 自动布局: 根据内容类型推荐最佳布局
  - 配色方案: 根据风格/情绪推荐配色
  - 排版建议: 字体/字号/间距推荐

数据流：
  DesignBrief → [本模块] → DesignSuggestion
  DesignSuggestion → DSL 编译器 → IR → 渲染器

所有建议均为"推荐"，用户可覆盖。
"""

from dataclasses import dataclass, field, replace
from typing import Optional

from .intent import DesignBrief


@dataclass
class ColorScheme:
    """配色方案"""
    name: str = ""
    # 主色
    primary: str = "#2563EB"
    # 辅助色
    secondary: str = "#7C3AED"
    # 强调色
    accent: str = "#F59E0B"
    # 背景色
    background: str = "#FFFFFF"
    # 表面色
    surface: str = "#F8FAFC"
    # 文本色
    text_primary: str = "#0F172A"
    text_secondary: str = "#475569"
    # 边框色
    border: str = "#E2E8F0"

    def copy(self) -> "ColorScheme":
        """返回深拷贝，避免修改全局预设"""
        return replace(self)


@dataclass
class LayoutSuggestion:
    """布局建议"""
    # 布局名称
    name: str = "blank"
    # 元素位置建议 (name → position dict)
    positions: dict[str, dict] = field(default_factory=dict)
    # 布局说明
    description: str = ""


@dataclass
class TypographySuggestion:
    """排版建议"""
    # 标题字体
    heading_font: str = "Microsoft YaHei UI"
    # 正文字体
    body_font: str = "Microsoft YaHei UI"
    # 标题字号范围 (min, max)
    heading_size_range: tuple[int, int] = (28, 44)
    # 正文字号
    body_size: int = 14
    # 行高
    line_height: float = 1.5


@dataclass
class DesignSuggestion:
    """综合设计建议"""
    # 配色方案
    color_scheme: ColorScheme = field(default_factory=ColorScheme)
    # 布局建议
    layout: LayoutSuggestion = field(default_factory=LayoutSuggestion)
    # 排版建议
    typography: TypographySuggestion = field(default_factory=TypographySuggestion)
    # 动画建议 (P1)
    animations: list[str] = field(default_factory=list)
    # 建议说明
    notes: list[str] = field(default_factory=list)


# ============================================================
# 预设配色方案
# ============================================================

COLOR_SCHEMES: dict[str, ColorScheme] = {
    "tech_dark": ColorScheme(
        name="科技深色",
        primary="#2563EB",
        secondary="#7C3AED",
        accent="#06B6D4",
        background="#0F172A",
        surface="#1E293B",
        text_primary="#F1F5F9",
        text_secondary="#94A3B8",
        border="#334155",
    ),
    "business_light": ColorScheme(
        name="商务浅色",
        primary="#1E40AF",
        secondary="#7C3AED",
        accent="#F59E0B",
        background="#FFFFFF",
        surface="#F8FAFC",
        text_primary="#0F172A",
        text_secondary="#475569",
        border="#E2E8F0",
    ),
    "minimal": ColorScheme(
        name="极简",
        primary="#18181B",
        secondary="#71717A",
        accent="#2563EB",
        background="#FFFFFF",
        surface="#FAFAFA",
        text_primary="#18181B",
        text_secondary="#71717A",
        border="#E4E4E7",
    ),
    "creative": ColorScheme(
        name="创意多彩",
        primary="#E11D48",
        secondary="#7C3AED",
        accent="#F59E0B",
        background="#FFFBEB",
        surface="#FEF3C7",
        text_primary="#1C1917",
        text_secondary="#57534E",
        border="#FED7AA",
    ),
    "academic": ColorScheme(
        name="学术",
        primary="#1E3A5F",
        secondary="#4A90D9",
        accent="#D97706",
        background="#FFFFFF",
        surface="#F0F4F8",
        text_primary="#1A202C",
        text_secondary="#4A5568",
        border="#CBD5E0",
    ),
}

# 主色覆盖映射: primary_color HEX → 最近似预设
_PRIMARY_TO_PRESET = {
    "#0F172A": "tech_dark",
    "#1E293B": "tech_dark",
    "#1E40AF": "business_light",
    "#18181B": "minimal",
    "#E11D48": "creative",
    "#1E3A5F": "academic",
}


# ============================================================
# 预设布局
# ============================================================

LAYOUT_PRESETS: dict[str, dict[str, LayoutSuggestion]] = {
    "presentation": {
        "cover": LayoutSuggestion(
            name="cover",
            description="封面页: 标题居中 + 副标题下方",
            positions={
                "title": {"x": "center", "y": "35%", "width": "80%", "height": "15%"},
                "subtitle": {"x": "center", "y": "55%", "width": "60%", "height": "8%"},
            },
        ),
        "content": LayoutSuggestion(
            name="content",
            description="内容页: 标题顶部 + 内容区域",
            positions={
                "title": {"x": "5%", "y": "5%", "width": "90%", "height": "10%"},
                "body": {"x": "5%", "y": "18%", "width": "90%", "height": "75%"},
            },
        ),
        "chart": LayoutSuggestion(
            name="chart",
            description="图表页: 标题 + 图表 + 注释",
            positions={
                "title": {"x": "5%", "y": "5%", "width": "90%", "height": "10%"},
                "chart": {"x": "5%", "y": "18%", "width": "90%", "height": "65%"},
                "caption": {"x": "5%", "y": "85%", "width": "90%", "height": "8%"},
            },
        ),
        "comparison": LayoutSuggestion(
            name="comparison",
            description="对比页: 左右两栏",
            positions={
                "title": {"x": "5%", "y": "5%", "width": "90%", "height": "10%"},
                "left": {"x": "5%", "y": "18%", "width": "42%", "height": "75%"},
                "right": {"x": "53%", "y": "18%", "width": "42%", "height": "75%"},
            },
        ),
    },
    "document": {
        "standard": LayoutSuggestion(
            name="standard",
            description="标准文档: 标题 + 正文",
            positions={
                "title": {"x": "20mm", "y": "20mm", "width": "170mm", "height": "15mm"},
                "body": {"x": "20mm", "y": "40mm", "width": "170mm", "height": "247mm"},
            },
        ),
    },
    "spreadsheet": {
        "standard": LayoutSuggestion(
            name="standard",
            description="标准表格: 全幅数据区",
            positions={
                "table": {"x": "0mm", "y": "0mm", "width": "200mm", "height": "100mm"},
            },
        ),
    },
}


# ============================================================
# 排版预设
# ============================================================

TYPOGRAPHY_PRESETS: dict[str, TypographySuggestion] = {
    "tech_dark": TypographySuggestion(
        heading_font="Segoe UI",
        body_font="Segoe UI",
        heading_size_range=(32, 48),
        body_size=14,
        line_height=1.6,
    ),
    "business_light": TypographySuggestion(
        heading_font="Microsoft YaHei UI",
        body_font="Microsoft YaHei UI",
        heading_size_range=(28, 44),
        body_size=14,
        line_height=1.5,
    ),
    "minimal": TypographySuggestion(
        heading_font="Helvetica Neue",
        body_font="Helvetica Neue",
        heading_size_range=(24, 40),
        body_size=13,
        line_height=1.5,
    ),
    "creative": TypographySuggestion(
        heading_font="Impact",
        body_font="Arial",
        heading_size_range=(36, 56),
        body_size=14,
        line_height=1.4,
    ),
    "academic": TypographySuggestion(
        heading_font="Times New Roman",
        body_font="Times New Roman",
        heading_size_range=(22, 36),
        body_size=12,
        line_height=1.8,
    ),
}


def suggest_design(brief: DesignBrief) -> DesignSuggestion:
    """根据 DesignBrief 生成设计建议

    Args:
        brief: 结构化设计意图

    Returns:
        DesignSuggestion 综合建议
    """
    suggestion = DesignSuggestion()
    notes = []

    # 1. 配色方案
    if brief.primary_color and brief.primary_color in _PRIMARY_TO_PRESET:
        style_key = _PRIMARY_TO_PRESET[brief.primary_color]
        suggestion.color_scheme = COLOR_SCHEMES[style_key].copy()
        suggestion.color_scheme.primary = brief.primary_color
        notes.append(f"使用自定义主色 {brief.primary_color}")
    elif brief.style in COLOR_SCHEMES:
        suggestion.color_scheme = COLOR_SCHEMES[brief.style].copy()
    else:
        suggestion.color_scheme = COLOR_SCHEMES["business_light"]
        notes.append("使用默认商务浅色配色")

    # 背景覆盖
    if brief.background == "dark":
        suggestion.color_scheme.background = "#0F172A"
        suggestion.color_scheme.surface = "#1E293B"
        suggestion.color_scheme.text_primary = "#F1F5F9"
        suggestion.color_scheme.text_secondary = "#94A3B8"
        suggestion.color_scheme.border = "#334155"
        notes.append("强制深色背景")
    elif brief.background == "light":
        suggestion.color_scheme.background = "#FFFFFF"
        suggestion.color_scheme.surface = "#F8FAFC"
        suggestion.color_scheme.text_primary = "#0F172A"
        suggestion.color_scheme.text_secondary = "#475569"
        suggestion.color_scheme.border = "#E2E8F0"
        notes.append("强制浅色背景")

    # 2. 布局建议
    doc_layouts = LAYOUT_PRESETS.get(brief.doc_type, LAYOUT_PRESETS["presentation"])

    if brief.doc_type == "presentation":
        # 推荐封面 + 内容页布局
        suggestion.layout = doc_layouts["cover"]
        if "charts" in brief.emphasis or "data_visualization" in brief.emphasis:
            notes.append("推荐图表页布局用于数据展示")
        if "tables" in brief.emphasis:
            notes.append("推荐对比页布局用于表格展示")
    elif brief.doc_type == "document":
        suggestion.layout = doc_layouts["standard"]
    elif brief.doc_type == "spreadsheet":
        suggestion.layout = doc_layouts["standard"]

    # 3. 排版建议
    if brief.style in TYPOGRAPHY_PRESETS:
        suggestion.typography = TYPOGRAPHY_PRESETS[brief.style]
    else:
        suggestion.typography = TYPOGRAPHY_PRESETS["business_light"]

    # 4. 动画建议 (P1, 仅记录建议)
    if brief.doc_type == "presentation":
        if "modern" in brief.mood:
            suggestion.animations.append("fade_in")
            suggestion.animations.append("slide_up")
        if "playful" in brief.mood:
            suggestion.animations.append("scale_in")
            suggestion.animations.append("bounce")

    suggestion.notes = notes
    return suggestion


def suggest_color_scheme(style: str) -> ColorScheme:
    """快速获取配色方案"""
    return COLOR_SCHEMES.get(style, COLOR_SCHEMES["business_light"])


def suggest_layout(doc_type: str, page_type: str = "cover") -> LayoutSuggestion:
    """快速获取布局建议"""
    doc_layouts = LAYOUT_PRESETS.get(doc_type, LAYOUT_PRESETS["presentation"])
    return doc_layouts.get(page_type, list(doc_layouts.values())[0])
