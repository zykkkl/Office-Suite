"""主题引擎 — 管理和应用设计主题

设计方案第十章：内置四大设计系统，主题可继承、覆盖、混合。

架构位置：
  Theme (数据) → ThemeEngine (管理) → IR 编译器 (应用) → 渲染器 (输出)

主题提供：
  - 配色方案 (colors)
  - 排版系统 (typography)
  - 间距系统 (spacing)
  - 效果定义 (effects: shadow, gradient, border)
  - 样式预设 (style presets: heading, body, caption, ...)

级联: theme → document → slide → element → inline
theme 是最底层，被上层覆盖。
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ThemeColors:
    """主题配色"""
    # 品牌色
    primary: str = "#2563EB"
    primary_light: str = "#60A5FA"
    primary_dark: str = "#1D4ED8"
    # 辅助色
    secondary: str = "#7C3AED"
    secondary_light: str = "#A78BFA"
    # 强调色
    accent: str = "#F59E0B"
    # 语义色
    success: str = "#10B981"
    warning: str = "#F59E0B"
    error: str = "#EF4444"
    info: str = "#3B82F6"
    # 背景
    background: str = "#FFFFFF"
    surface: str = "#F8FAFC"
    surface_alt: str = "#F1F5F9"
    # 文本
    text_primary: str = "#0F172A"
    text_secondary: str = "#475569"
    text_disabled: str = "#94A3B8"
    text_inverse: str = "#F1F5F9"
    # 边框
    border: str = "#E2E8F0"
    border_light: str = "#F1F5F9"
    # 分割线
    divider: str = "#E2E8F0"


@dataclass
class ThemeTypography:
    """主题排版"""
    # 字体族
    heading_font: str = "Microsoft YaHei UI"
    body_font: str = "Microsoft YaHei UI"
    mono_font: str = "Consolas"
    # 字号体系 (pt)
    display_size: int = 44      # 展示标题
    h1_size: int = 36           # 一级标题
    h2_size: int = 28           # 二级标题
    h3_size: int = 22           # 三级标题
    body_size: int = 14         # 正文
    caption_size: int = 11      # 注释
    small_size: int = 9         # 小字
    # 字重
    weight_regular: int = 400
    weight_medium: int = 500
    weight_bold: int = 700
    # 行高
    line_height: float = 1.5


@dataclass
class ThemeSpacing:
    """主题间距 (mm)"""
    xs: int = 2
    sm: int = 4
    md: int = 8
    lg: int = 16
    xl: int = 24
    xxl: int = 32
    # 页面边距
    page_margin: int = 20
    # 元素间距
    element_gap: int = 10


@dataclass
class ThemeEffects:
    """主题效果"""
    # 阴影
    shadow_sm: str = "0 1px 2px rgba(0,0,0,0.05)"
    shadow_md: str = "0 4px 6px rgba(0,0,0,0.07)"
    shadow_lg: str = "0 10px 15px rgba(0,0,0,0.1)"
    # 圆角 (mm)
    radius_sm: int = 2
    radius_md: int = 4
    radius_lg: int = 8
    radius_full: int = 999
    # 边框
    border_width: int = 1


@dataclass
class Theme:
    """完整主题定义"""
    name: str = "default"
    display_name: str = "Default"
    # 主题类型: light / dark
    mode: str = "light"
    # 配色
    colors: ThemeColors = field(default_factory=ThemeColors)
    # 排版
    typography: ThemeTypography = field(default_factory=ThemeTypography)
    # 间距
    spacing: ThemeSpacing = field(default_factory=ThemeSpacing)
    # 效果
    effects: ThemeEffects = field(default_factory=ThemeEffects)
    # 样式预设 (名称 → IRStyle 兼容 dict)
    presets: dict[str, dict] = field(default_factory=dict)
    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_preset(self, name: str) -> dict:
        """获取样式预设"""
        return self.presets.get(name, {})

    def to_style_dict(self) -> dict:
        """导出为 DSL styles 格式"""
        return {
            "heading": {
                "font": {
                    "family": self.typography.heading_font,
                    "size": self.typography.h1_size,
                    "weight": self.typography.weight_bold,
                    "color": self.colors.text_primary,
                },
            },
            "heading2": {
                "font": {
                    "family": self.typography.heading_font,
                    "size": self.typography.h2_size,
                    "weight": self.typography.weight_bold,
                    "color": self.colors.text_primary,
                },
            },
            "heading3": {
                "font": {
                    "family": self.typography.heading_font,
                    "size": self.typography.h3_size,
                    "weight": self.typography.weight_medium,
                    "color": self.colors.text_primary,
                },
            },
            "body": {
                "font": {
                    "family": self.typography.body_font,
                    "size": self.typography.body_size,
                    "weight": self.typography.weight_regular,
                    "color": self.colors.text_primary,
                },
            },
            "caption": {
                "font": {
                    "family": self.typography.body_font,
                    "size": self.typography.caption_size,
                    "weight": self.typography.weight_regular,
                    "color": self.colors.text_secondary,
                },
            },
            "accent": {
                "font": {
                    "family": self.typography.body_font,
                    "size": self.typography.body_size,
                    "weight": self.typography.weight_medium,
                    "color": self.colors.primary,
                },
            },
        }


# ============================================================
# 主题注册表
# ============================================================

_THEME_REGISTRY: dict[str, Theme] = {}


def register_theme(theme: Theme):
    """注册主题"""
    _THEME_REGISTRY[theme.name] = theme


def get_theme(name: str) -> Optional[Theme]:
    """获取主题（不存在返回 None）"""
    return _THEME_REGISTRY.get(name)


def list_themes() -> list[str]:
    """列出所有已注册主题名"""
    return list(_THEME_REGISTRY.keys())


def get_theme_or_default(name: str) -> Theme:
    """获取主题，不存在时返回默认主题"""
    theme = _THEME_REGISTRY.get(name)
    if theme is None:
        # 尝试模糊匹配
        for key in _THEME_REGISTRY:
            if name.lower() in key.lower():
                return _THEME_REGISTRY[key]
        return _THEME_REGISTRY.get("fluent", _create_fallback_theme())
    return theme


def _create_fallback_theme() -> Theme:
    """创建兜底主题"""
    return Theme(name="fallback", display_name="Fallback")


# ============================================================
# 主题继承与混合
# ============================================================

def inherit_theme(base: Theme, overrides: dict) -> Theme:
    """基于父主题创建子主题

    Args:
        base: 父主题
        overrides: 覆盖项 (支持嵌套 dict)

    Returns:
        新的 Theme 实例
    """
    import copy
    theme = copy.deepcopy(base)

    if "name" in overrides:
        theme.name = overrides["name"]
    if "display_name" in overrides:
        theme.display_name = overrides["display_name"]
    if "mode" in overrides:
        theme.mode = overrides["mode"]

    # 配色覆盖
    if "colors" in overrides:
        for k, v in overrides["colors"].items():
            if hasattr(theme.colors, k):
                setattr(theme.colors, k, v)

    # 排版覆盖
    if "typography" in overrides:
        for k, v in overrides["typography"].items():
            if hasattr(theme.typography, k):
                setattr(theme.typography, k, v)

    # 间距覆盖
    if "spacing" in overrides:
        for k, v in overrides["spacing"].items():
            if hasattr(theme.spacing, k):
                setattr(theme.spacing, k, v)

    # 预设覆盖/新增
    if "presets" in overrides:
        theme.presets.update(overrides["presets"])

    return theme


def blend_themes(theme_a: Theme, theme_b: Theme, ratio: float = 0.5) -> Theme:
    """混合两个主题

    Args:
        theme_a: 主题 A
        theme_b: 主题 B
        ratio: A 的权重 (0.0 ~ 1.0)

    Returns:
        混合后的新主题
    """
    # 简单实现：按 ratio 选择 A 或 B 的字段
    # P0 不做颜色插值，直接按比例选择
    import copy
    result = copy.deepcopy(theme_a)
    result.name = f"{theme_a.name}_x_{theme_b.name}"
    result.display_name = f"{theme_a.display_name} × {theme_b.display_name}"

    if ratio < 0.5:
        # B 为主
        result.colors = copy.deepcopy(theme_b.colors)
        result.typography = copy.deepcopy(theme_b.typography)
        result.spacing = copy.deepcopy(theme_b.spacing)

    return result
