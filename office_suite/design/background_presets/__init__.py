"""背景板预设模板 — 封装 background_board 四层系统

利用已有的 background_board（background → illustration → scrim → ornament）
封装成可直接调用的风格模板，解决"背景单调、品质不高"的问题。

用法：
    from office_suite.design.background_presets import business_clean, gradient_spotlight
    slide.background_board = business_clean(palette="corporate")
"""

from .gradient import (
    gradient_spotlight,
    frosted_glass,
    dark_elegant,
    gradient_mesh,
    neon_glow,
    gradient_abstract,
)
from .texture import (
    paper_texture,
    geometric_blocks,
    diagonal_split,
    watermark_bg,
    dotted_grid_bg,
    striped_bg,
)
from .mood import (
    card_layered,
    morandi_soft,
    minimal_lines,
    polygon_geometric,
    chinese_ink_wash,
)
from .business import business_clean, subtle_texture, split_accent

__all__ = [
    # gradient
    "gradient_spotlight",
    "frosted_glass",
    "dark_elegant",
    "gradient_mesh",
    "neon_glow",
    "gradient_abstract",
    # texture
    "paper_texture",
    "geometric_blocks",
    "diagonal_split",
    "watermark_bg",
    "dotted_grid_bg",
    "striped_bg",
    # mood
    "card_layered",
    "morandi_soft",
    "minimal_lines",
    "polygon_geometric",
    "chinese_ink_wash",
    # business
    "business_clean",
    "subtle_texture",
    "split_accent",
]
