"""设计品质增强测试

验证新增的设计模块：
  1. 背景板预设（21种）
  2. 装饰工具箱（8种）
  3. 幻灯片模板（5种）
  4. 智能配色适配
  5. 纹理生成器
"""

import pytest

from office_suite.design import (
    # 背景板预设
    business_clean, gradient_spotlight, card_layered, subtle_texture,
    split_accent, frosted_glass, dark_elegant, gradient_mesh,
    neon_glow, paper_texture, geometric_blocks, diagonal_split,
    watermark_bg, morandi_soft, minimal_lines, polygon_geometric,
    chinese_ink_wash, gradient_abstract, dotted_grid_bg, striped_bg,
    # 装饰工具箱
    corner_ribbon, bottom_wave, side_accent_bar, circle_frame,
    underline_accent, divider_line, badge, arrow_connector,
    # 幻灯片模板
    cover_slide, content_slide, closing_slide, section_slide, quote_slide,
    # 智能配色
    get_accent, get_subtle, get_decor, resolve_color, auto_border,
    auto_shadow, auto_fill, get_gradient_pair, get_text_style, get_card_style,
)
from office_suite.design.patterns import (
    dot_grid, line_grid, hex_grid, wave_bottom, concentric_circles,
)


# ── 背景板预设 ──

class TestBackgroundPresets:
    """背景板预设测试"""

    def _assert_valid_board(self, board: dict, preset_name: str):
        """验证背景板结构"""
        assert "background" in board, f"{preset_name}: missing 'background'"
        assert "illustration" in board, f"{preset_name}: missing 'illustration'"
        assert "scrim" in board, f"{preset_name}: missing 'scrim'"
        assert "ornament" in board, f"{preset_name}: missing 'ornament'"
        assert isinstance(board["background"], dict), f"{preset_name}: background should be dict"
        assert isinstance(board["illustration"], list), f"{preset_name}: illustration should be list"
        assert isinstance(board["scrim"], list), f"{preset_name}: scrim should be list"
        assert isinstance(board["ornament"], list), f"{preset_name}: ornament should be list"

    def test_business_clean(self):
        board = business_clean("corporate")
        self._assert_valid_board(board, "business_clean")
        assert board["background"]["type"] == "color"

    def test_gradient_spotlight(self):
        board = gradient_spotlight("tech")
        self._assert_valid_board(board, "gradient_spotlight")
        assert board["background"]["type"] == "gradient"

    def test_card_layered(self):
        board = card_layered("minimal", card_count=4)
        self._assert_valid_board(board, "card_layered")
        assert len(board["illustration"]) == 4

    def test_subtle_texture(self):
        board = subtle_texture("editorial", texture_type="dot")
        self._assert_valid_board(board, "subtle_texture")

    def test_split_accent(self):
        board = split_accent("corporate", side="left")
        self._assert_valid_board(board, "split_accent")
        assert len(board["illustration"]) == 1

    def test_frosted_glass(self):
        board = frosted_glass("minimal")
        self._assert_valid_board(board, "frosted_glass")
        assert board["background"]["type"] == "gradient"

    def test_dark_elegant(self):
        board = dark_elegant("creative")
        self._assert_valid_board(board, "dark_elegant")
        assert len(board["illustration"]) == 2

    def test_gradient_mesh(self):
        board = gradient_mesh("ocean")
        self._assert_valid_board(board, "gradient_mesh")
        assert len(board["illustration"]) == 2

    def test_neon_glow(self):
        board = neon_glow("tech")
        self._assert_valid_board(board, "neon_glow")

    def test_paper_texture(self):
        board = paper_texture("warm")
        self._assert_valid_board(board, "paper_texture")

    def test_geometric_blocks(self):
        board = geometric_blocks("minimal")
        self._assert_valid_board(board, "geometric_blocks")

    def test_diagonal_split(self):
        board = diagonal_split("corporate", angle="forward")
        self._assert_valid_board(board, "diagonal_split")

    def test_watermark_bg(self):
        board = watermark_bg("editorial")
        self._assert_valid_board(board, "watermark_bg")

    def test_morandi_soft(self):
        board = morandi_soft("morandi")
        self._assert_valid_board(board, "morandi_soft")
        assert board["background"]["type"] == "gradient"

    def test_minimal_lines(self):
        board = minimal_lines("minimal_bw")
        self._assert_valid_board(board, "minimal_lines")
        assert len(board["ornament"]) == 3

    def test_polygon_geometric(self):
        board = polygon_geometric("corporate", polygon_count=3)
        self._assert_valid_board(board, "polygon_geometric")
        assert len(board["illustration"]) == 3

    def test_chinese_ink_wash(self):
        board = chinese_ink_wash("chinese_ink")
        self._assert_valid_board(board, "chinese_ink_wash")
        assert len(board["illustration"]) == 2

    def test_gradient_abstract(self):
        board = gradient_abstract("ocean")
        self._assert_valid_board(board, "gradient_abstract")
        assert len(board["illustration"]) == 3

    def test_dotted_grid_bg(self):
        board = dotted_grid_bg("editorial", dot_spacing=10.0)
        self._assert_valid_board(board, "dotted_grid_bg")
        assert len(board["illustration"]) > 0

    def test_striped_bg(self):
        board = striped_bg("minimal_bw")
        self._assert_valid_board(board, "striped_bg")
        assert len(board["illustration"]) > 0

    def test_all_presets_with_palette(self):
        """所有预设都应支持不同配色方案"""
        palettes = ["corporate", "editorial", "creative", "tech", "morandi", "chinese_ink"]
        presets = [business_clean, gradient_spotlight, frosted_glass, dark_elegant, morandi_soft]

        for preset_fn in presets:
            for palette in palettes:
                board = preset_fn(palette)
                self._assert_valid_board(board, f"{preset_fn.__name__}({palette})")


# ── 装饰工具箱 ──

class TestOrnaments:
    """装饰工具箱测试"""

    def _assert_valid_elements(self, elements: list, name: str):
        """验证元素列表结构"""
        assert isinstance(elements, list), f"{name}: should return list"
        assert len(elements) > 0, f"{name}: should return non-empty list"
        for elem in elements:
            assert "type" in elem, f"{name}: element missing 'type'"
            assert "position" in elem, f"{name}: element missing 'position'"

    def test_corner_ribbon(self):
        elements = corner_ribbon(color="#F97316", text="NEW")
        self._assert_valid_elements(elements, "corner_ribbon")
        assert len(elements) == 2  # shape + text

    def test_bottom_wave(self):
        elements = bottom_wave(color="#E2E8F0")
        self._assert_valid_elements(elements, "bottom_wave")
        assert len(elements) > 10  # 多条线段

    def test_side_accent_bar(self):
        elements = side_accent_bar(color="#2563EB", position="left")
        self._assert_valid_elements(elements, "side_accent_bar")
        assert len(elements) == 1

    def test_circle_frame(self):
        elements = circle_frame(x=100, y=70, radius=15, color="#CBD5E1")
        self._assert_valid_elements(elements, "circle_frame")
        assert len(elements) == 1

    def test_underline_accent(self):
        elements = underline_accent(x=30, y=40, width=50, height=2.5)
        self._assert_valid_elements(elements, "underline_accent")
        assert len(elements) == 1

    def test_divider_line(self):
        elements = divider_line(x=25, y=100, width=200)
        self._assert_valid_elements(elements, "divider_line")
        assert len(elements) == 1

    def test_divider_line_dotted(self):
        elements = divider_line(x=25, y=100, width=200, style="dotted")
        self._assert_valid_elements(elements, "divider_line_dotted")
        assert len(elements) == 2  # line + dot

    def test_badge(self):
        elements = badge(20, 20, "Q1", bg_color="#2563EB")
        self._assert_valid_elements(elements, "badge")
        assert len(elements) == 2  # shape + text

    def test_arrow_connector(self):
        elements = arrow_connector(50, 50, 150, 50)
        self._assert_valid_elements(elements, "arrow_connector")
        assert len(elements) == 2  # line + triangle


# ── 幻灯片模板 ──

class TestSlideTemplates:
    """幻灯片模板测试"""

    def _assert_valid_slide(self, slide: dict, name: str):
        """验证幻灯片结构"""
        assert "layout" in slide, f"{name}: missing 'layout'"
        assert "background_board" in slide, f"{name}: missing 'background_board'"
        assert "elements" in slide, f"{name}: missing 'elements'"
        assert isinstance(slide["elements"], list), f"{name}: elements should be list"

    def test_cover_slide_center(self):
        slide = cover_slide(palette="corporate", title="Test", layout="center")
        self._assert_valid_slide(slide, "cover_slide_center")
        assert len(slide["elements"]) >= 2  # title + underline

    def test_cover_slide_left(self):
        slide = cover_slide(palette="corporate", title="Test", layout="left")
        self._assert_valid_slide(slide, "cover_slide_left")

    def test_cover_slide_split(self):
        slide = cover_slide(palette="corporate", title="Test", layout="split")
        self._assert_valid_slide(slide, "cover_slide_split")

    def test_content_slide_full(self):
        slide = content_slide(palette="corporate", title="Test", layout="full")
        self._assert_valid_slide(slide, "content_slide_full")

    def test_content_slide_two_column(self):
        slide = content_slide(palette="corporate", title="Test", layout="two_column")
        self._assert_valid_slide(slide, "content_slide_two_column")

    def test_content_slide_three_column(self):
        slide = content_slide(palette="corporate", title="Test", layout="three_column")
        self._assert_valid_slide(slide, "content_slide_three_column")

    def test_closing_slide(self):
        slide = closing_slide(palette="corporate", message="Thanks")
        self._assert_valid_slide(slide, "closing_slide")

    def test_section_slide(self):
        slide = section_slide(palette="corporate", section_title="Intro", section_number=1)
        self._assert_valid_slide(slide, "section_slide")

    def test_quote_slide(self):
        slide = quote_slide(palette="corporate", quote="Hello", author="Test")
        self._assert_valid_slide(slide, "quote_slide")

    def test_templates_with_different_palettes(self):
        """模板应支持不同配色方案"""
        palettes = ["corporate", "tech", "creative", "morandi"]

        for palette in palettes:
            slide = cover_slide(palette=palette, title="Test")
            self._assert_valid_slide(slide, f"cover_slide({palette})")


# ── 智能配色 ──

class TestAutoStyle:
    """智能配色测试"""

    def test_get_accent(self):
        accent = get_accent("corporate")
        assert isinstance(accent, str)
        assert accent.startswith("#")

    def test_get_subtle(self):
        subtle = get_subtle("corporate")
        assert isinstance(subtle, str)
        assert subtle.startswith("#")

    def test_get_decor(self):
        decor = get_decor("corporate")
        assert isinstance(decor, dict)
        assert "accent" in decor
        assert "primary" in decor
        assert "subtle" in decor

    def test_resolve_color_full_opacity(self):
        color = resolve_color("corporate", "accent", 1.0)
        assert isinstance(color, str)
        assert color.startswith("#")
        assert len(color) == 7  # #RRGGBB

    def test_resolve_color_half_opacity(self):
        color = resolve_color("corporate", "accent", 0.5)
        assert isinstance(color, str)
        assert color.startswith("#")
        assert len(color) == 9  # #RRGGBBAA

    def test_auto_border(self):
        border = auto_border("corporate", width=0.5)
        assert isinstance(border, dict)
        assert "border" in border
        assert border["border"]["width"] == 0.5

    def test_auto_shadow(self):
        shadow = auto_shadow("corporate", level="md")
        assert isinstance(shadow, dict)

    def test_auto_fill(self):
        fill = auto_fill("corporate", role="bg")
        assert isinstance(fill, dict)
        assert "fill" in fill

    def test_get_gradient_pair(self):
        pair = get_gradient_pair("corporate")
        assert isinstance(pair, tuple)
        assert len(pair) == 2
        assert pair[0].startswith("#")
        assert pair[1].startswith("#")

    def test_get_text_style(self):
        style = get_text_style("corporate", role="heading")
        assert isinstance(style, dict)
        assert "font" in style

    def test_get_card_style(self):
        card = get_card_style("corporate", elevated=True)
        assert isinstance(card, dict)
        assert "fill" in card
        assert "border" in card
        assert "shadow" in card

    def test_auto_style_with_different_palettes(self):
        """智能配色应支持不同配色方案"""
        palettes = ["corporate", "editorial", "creative", "tech", "morandi", "chinese_ink"]

        for palette in palettes:
            accent = get_accent(palette)
            assert isinstance(accent, str), f"get_accent({palette}) should return string"
            assert accent.startswith("#"), f"get_accent({palette}) should start with #"


# ── 纹理生成器 ──

class TestPatterns:
    """纹理生成器测试"""

    def _assert_valid_elements(self, elements: list, name: str):
        """验证元素列表结构"""
        assert isinstance(elements, list), f"{name}: should return list"
        assert len(elements) > 0, f"{name}: should return non-empty list"
        for elem in elements:
            assert "type" in elem, f"{name}: element missing 'type'"
            assert "position" in elem, f"{name}: element missing 'position'"

    def test_dot_grid(self):
        elements = dot_grid(density=0.5, color="#E2E8F0")
        self._assert_valid_elements(elements, "dot_grid")
        assert len(elements) > 10

    def test_line_grid(self):
        elements = line_grid(spacing=10.0, color="#E2E8F0")
        self._assert_valid_elements(elements, "line_grid")
        assert len(elements) > 5

    def test_hex_grid(self):
        elements = hex_grid(size=6.0, color="#CBD5E1")
        self._assert_valid_elements(elements, "hex_grid")
        assert len(elements) > 5

    def test_wave_bottom(self):
        elements = wave_bottom(color="#E2E8F0")
        self._assert_valid_elements(elements, "wave_bottom")
        assert len(elements) > 10

    def test_concentric_circles(self):
        elements = concentric_circles(center_x=127, center_y=71, max_radius=50, step=10)
        self._assert_valid_elements(elements, "concentric_circles")
        assert len(elements) == 5  # 50/10 = 5 circles

    def test_dot_grid_density(self):
        """不同密度应产生不同数量的点"""
        sparse = dot_grid(density=1.0, color="#E2E8F0")
        dense = dot_grid(density=0.2, color="#E2E8F0")
        assert len(dense) > len(sparse)

    def test_line_grid_angle(self):
        """不同角度应产生不同方向的线"""
        horizontal = line_grid(angle=0, color="#E2E8F0")
        diagonal = line_grid(angle=45, color="#E2E8F0")
        assert len(horizontal) > 0
        assert len(diagonal) > 0


# ── 配色方案 ──

class TestPalettes:
    """配色方案测试"""

    def test_all_palettes_exist(self):
        """所有配色方案都应存在"""
        from office_suite.design.tokens import PALETTE
        expected = [
            "corporate", "editorial", "creative", "minimal", "tech",
            "elegant", "flat", "chinese", "warm", "morandi",
            "minimal_bw", "chinese_ink", "morandi_blue", "morandi_pink", "morandi_green",
        ]
        for name in expected:
            assert name in PALETTE, f"Missing palette: {name}"

    def test_palette_structure(self):
        """每个配色方案应包含必要字段"""
        from office_suite.design.tokens import PALETTE
        required_keys = ["primary", "secondary", "accent", "bg", "bg_alt", "text", "text_secondary", "border"]

        for name, palette in PALETTE.items():
            for key in required_keys:
                assert key in palette, f"Palette '{name}' missing key '{key}'"
                assert palette[key].startswith("#"), f"Palette '{name}' key '{key}' should start with #"
