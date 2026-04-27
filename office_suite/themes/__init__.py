"""主题系统 — 设计令牌 + 预设样式

设计方案第十章：内置 Fluent Design + 通用主题。

使用方式：
  from office_suite.themes import get_theme
  theme = get_theme("fluent")
  style_dict = theme.to_style_dict()
"""

from .engine import (
    Theme,
    ThemeColors,
    ThemeTypography,
    ThemeSpacing,
    ThemeEffects,
    register_theme,
    get_theme,
    get_theme_or_default,
    list_themes,
    inherit_theme,
    blend_themes,
)

# 确保内置主题被注册
from . import fluent  # noqa: F401
from . import universal  # noqa: F401
from . import material3  # noqa: F401
from . import apple_hig  # noqa: F401

__all__ = [
    "Theme",
    "ThemeColors",
    "ThemeTypography",
    "ThemeSpacing",
    "ThemeEffects",
    "register_theme",
    "get_theme",
    "get_theme_or_default",
    "list_themes",
    "inherit_theme",
    "blend_themes",
]
