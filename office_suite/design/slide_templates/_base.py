"""共享常量和导入"""
from __future__ import annotations

from typing import Any

from ..tokens import get_palette, get_font_for_palette
from ..background_presets import (
    business_clean,
    gradient_spotlight,
    dark_elegant,
    gradient_mesh,
    neon_glow,
    paper_texture,
    subtle_texture,
    frosted_glass,
)
from ..ornaments import (
    side_accent_bar,
    underline_accent,
    gradient_underline,
    gradient_bar,
    divider_line,
    badge,
    circle_frame,
)

from ...constants import SLIDE_WIDTH_MM as SLIDE_W, SLIDE_HEIGHT_MM as SLIDE_H


def _palette_colors(name: str) -> dict[str, str]:
    """获取配色方案，回退到 corporate"""
    return get_palette(name)
