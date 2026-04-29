"""P1 增强测试 — OKLCH 色彩 + 布局规范修复

验证：
1. compiler 正确解析 oklch(l, c, h) 颜色格式
2. LayoutSpec GRID 模式使用 row_height 而非 col_width
3. LayoutSpec FLEX 模式委托给 FlexLayout
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from office_suite.engine.style.color import OKLCH, oklch_to_hex, hex_to_oklch
from office_suite.ir.layout_spec import (
    LayoutSpec, LayoutMode, AbsolutePosition, GridPosition, FlexPosition,
    FlexDirection, FlexJustify, FlexAlign,
)
from office_suite.ir.compiler import _resolve_color, compile_style
from office_suite.dsl.schema import StyleSpec, FontSpec, FillSpec


# ============================================================
# OKLCH 颜色解析
# ============================================================

class TestOKLCHColorResolution:
    """compiler._resolve_color 支持 oklch 格式"""

    def test_hex_passthrough(self):
        assert _resolve_color("#FF0000") == "#FF0000"
        assert _resolve_color("#000") == "#000"
        assert _resolve_color(None) is None
        assert _resolve_color("") == ""

    def test_oklch_red(self):
        """oklch(0.63, 0.26, 29) 应接近纯红"""
        result = _resolve_color("oklch(0.63, 0.26, 29)")
        assert result is not None
        assert result.startswith("#")
        # 转回 OKLCH 验证
        lch = hex_to_oklch(result)
        assert abs(lch.l - 0.63) < 0.02
        assert abs(lch.c - 0.26) < 0.02
        assert abs(lch.h - 29) < 2

    def test_oklch_white(self):
        """oklch(1.0, 0.0, 0) 应为白色"""
        result = _resolve_color("oklch(1.0, 0.0, 0)")
        assert result == "#FFFFFF"

    def test_oklch_black(self):
        """oklch(0.0, 0.0, 0) 应为黑色"""
        result = _resolve_color("oklch(0.0, 0.0, 0)")
        assert result == "#000000"

    def test_oklch_case_insensitive(self):
        """大小写不敏感"""
        r1 = _resolve_color("oklch(0.5, 0.1, 120)")
        r2 = _resolve_color("OKLCH(0.5, 0.1, 120)")
        assert r1 == r2

    def test_oklch_with_spaces(self):
        """容许空格"""
        r1 = _resolve_color("oklch(0.5,0.1,120)")
        r2 = _resolve_color("oklch( 0.5 , 0.1 , 120 )")
        assert r1 == r2

    def test_compile_style_font_color_oklch(self):
        """compile_style 将 oklch 颜色转为 hex"""
        style = StyleSpec(font=FontSpec(color="oklch(0.63, 0.26, 29)"))
        ir = compile_style(style)
        assert ir is not None
        assert ir.font_color is not None
        assert ir.font_color.startswith("#")
        assert ir.font_color != "oklch(0.63, 0.26, 29)"

    def test_compile_style_fill_color_oklch(self):
        """compile_style 将 fill 的 oklch 颜色转为 hex"""
        style = StyleSpec(fill=FillSpec(color="oklch(0.7, 0.15, 200)"))
        ir = compile_style(style)
        assert ir is not None
        assert ir.fill_color is not None
        assert ir.fill_color.startswith("#")


# ============================================================
# LayoutSpec GRID 修复
# ============================================================

class TestLayoutSpecGrid:
    """LayoutSpec GRID 模式使用 row_height"""

    def test_grid_uses_row_height(self):
        """row_height 应独立于 col_width"""
        spec = LayoutSpec(
            mode=LayoutMode.GRID,
            grid=GridPosition(column=1, row=2, column_span=1, row_span=1, columns=12),
        )
        # 容器 240mm 宽, 120mm 高, 列宽=20mm, 行高=30mm
        pos = spec.resolve_mm(240.0, 120.0, row_height=30.0)
        assert pos.x == 0  # 第1列
        assert pos.y == 30.0  # 第2行 * 30mm
        assert pos.width == 20.0  # 1列宽

    def test_grid_default_row_height_is_col_width(self):
        """不传 row_height 时默认等于 col_width"""
        spec = LayoutSpec(
            mode=LayoutMode.GRID,
            grid=GridPosition(column=2, row=3, column_span=1, row_span=1, columns=12),
        )
        pos = spec.resolve_mm(240.0, 120.0)
        col_width = 240.0 / 12
        assert pos.y == pytest.approx(2 * col_width)

    def test_grid_span_uses_row_height(self):
        """row_span 应使用 row_height"""
        spec = LayoutSpec(
            mode=LayoutMode.GRID,
            grid=GridPosition(column=1, row=1, column_span=2, row_span=3, columns=12),
        )
        pos = spec.resolve_mm(240.0, 120.0, row_height=25.0)
        assert pos.width == pytest.approx(2 * 20.0)
        assert pos.height == pytest.approx(3 * 25.0)


# ============================================================
# LayoutSpec FLEX 修复
# ============================================================

class TestLayoutSpecFlex:
    """LayoutSpec FLEX 模式委托给 FlexLayout"""

    def test_flex_single_item_fallback(self):
        """无 flex_items 时，单 item 占满容器"""
        spec = LayoutSpec(
            mode=LayoutMode.FLEX,
            flex=FlexPosition(direction=FlexDirection.ROW),
        )
        pos = spec.resolve_mm(254.0, 142.875)
        assert pos.width > 0 or pos.height > 0

    def test_flex_multi_item_row(self):
        """多 item ROW 模式：3 个等宽 item"""
        from office_suite.engine.layout.flex import FlexItem as FItem
        spec = LayoutSpec(
            mode=LayoutMode.FLEX,
            flex=FlexPosition(direction=FlexDirection.ROW, gap=2.0),
        )
        items = [
            FItem(width=80, height=30),
            FItem(width=80, height=30),
            FItem(width=80, height=30),
        ]
        pos0 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=0)
        pos1 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=1)
        pos2 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=2)

        # 第一个 item 从 x=0 开始
        assert pos0.x == 0
        # 第二个 item 在第一个右边（加 gap）
        assert pos1.x > pos0.x + pos0.width
        # 第三个 item 在第二个右边
        assert pos2.x > pos1.x + pos1.width
        # 所有 item 的 y 相同（ROW 模式）
        assert pos0.y == pos1.y == pos2.y

    def test_flex_multi_item_column(self):
        """多 item COLUMN 模式：3 个等高 item"""
        from office_suite.engine.layout.flex import FlexItem as FItem
        spec = LayoutSpec(
            mode=LayoutMode.FLEX,
            flex=FlexPosition(direction=FlexDirection.COLUMN, gap=5.0),
        )
        items = [
            FItem(width=200, height=30),
            FItem(width=200, height=30),
            FItem(width=200, height=30),
        ]
        pos0 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=0)
        pos1 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=1)
        pos2 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=2)

        # COLUMN 模式：y 递增
        assert pos0.y == 0
        assert pos1.y > pos0.y + pos0.height
        assert pos2.y > pos1.y + pos1.height
        # x 相同
        assert pos0.x == pos1.x == pos2.x

    def test_flex_grow_distribution(self):
        """grow 属性分配剩余空间"""
        from office_suite.engine.layout.flex import FlexItem as FItem
        spec = LayoutSpec(
            mode=LayoutMode.FLEX,
            flex=FlexPosition(direction=FlexDirection.ROW),
        )
        items = [
            FItem(width=50, height=30, grow=0),
            FItem(width=50, height=30, grow=1),
            FItem(width=50, height=30, grow=1),
        ]
        pos0 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=0)
        pos1 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=1)
        pos2 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=2)

        # grow=0 的 item 保持原宽度
        assert pos0.width == pytest.approx(50)
        # grow=1 的两个 item 平分剩余空间，比 grow=0 的宽
        assert pos1.width > 50
        assert pos2.width > 50
        # 两个 grow=1 的 item 宽度相同
        assert pos1.width == pytest.approx(pos2.width)

    def test_flex_justify_space_between(self):
        """justify-content: space-between — 首尾贴边，中间均匀"""
        from office_suite.engine.layout.flex import FlexItem as FItem
        spec = LayoutSpec(
            mode=LayoutMode.FLEX,
            flex=FlexPosition(direction=FlexDirection.ROW, justify=FlexJustify.SPACE_BETWEEN),
        )
        items = [FItem(width=30, height=20) for _ in range(3)]
        positions = [spec.resolve_mm(200.0, 100.0, flex_items=items, flex_index=i) for i in range(3)]

        # 第一个贴左边
        assert positions[0].x == pytest.approx(0)
        # 最后一个贴右边
        assert positions[2].x + positions[2].width == pytest.approx(200.0)
        # 中间均匀分布
        gap = (200.0 - 3 * 30) / 2
        assert positions[1].x == pytest.approx(30 + gap)

    def test_flex_justify_space_evenly(self):
        """justify-content: space-evenly — 所有间距相等"""
        from office_suite.engine.layout.flex import FlexItem as FItem
        spec = LayoutSpec(
            mode=LayoutMode.FLEX,
            flex=FlexPosition(direction=FlexDirection.ROW, justify=FlexJustify.SPACE_EVENLY),
        )
        items = [FItem(width=30, height=20) for _ in range(3)]
        positions = [spec.resolve_mm(200.0, 100.0, flex_items=items, flex_index=i) for i in range(3)]

        # 4 个间距（两端 + 中间两个）各为 (200 - 90) / 4 = 27.5
        expected_gap = (200.0 - 3 * 30) / 4
        assert positions[0].x == pytest.approx(expected_gap)
        assert positions[1].x == pytest.approx(expected_gap * 2 + 30)
        assert positions[2].x == pytest.approx(expected_gap * 3 + 60)

    def test_flex_justify_space_around(self):
        """justify-content: space-around — 两端间距是中间的一半"""
        from office_suite.engine.layout.flex import FlexItem as FItem
        spec = LayoutSpec(
            mode=LayoutMode.FLEX,
            flex=FlexPosition(direction=FlexDirection.ROW, justify=FlexJustify.SPACE_AROUND),
        )
        items = [FItem(width=30, height=20) for _ in range(3)]
        positions = [spec.resolve_mm(200.0, 100.0, flex_items=items, flex_index=i) for i in range(3)]

        # 每个 item 分到的间距 = (200 - 90) / 3 = 36.67，两端各占一半 = 18.33
        per_gap = (200.0 - 3 * 30) / 3
        assert positions[0].x == pytest.approx(per_gap / 2, abs=0.1)
        assert positions[1].x == pytest.approx(per_gap / 2 + 30 + per_gap, abs=0.1)

    def test_flex_wrap(self):
        """flex-wrap: wrap — 子项溢出时换行"""
        from office_suite.engine.layout.flex import FlexItem as FItem
        from office_suite.ir.layout_spec import FlexWrap
        spec = LayoutSpec(
            mode=LayoutMode.FLEX,
            flex=FlexPosition(direction=FlexDirection.ROW, wrap=FlexWrap.WRAP, gap=5.0),
        )
        # shrink=0 防止收缩；100*3+5*2=210 < 254，但 100*3+5*2=210+100+5=315 > 254
        items = [FItem(width=100, height=30, shrink=0) for _ in range(3)]
        pos0 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=0)
        pos1 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=1)
        pos2 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=2)

        # 前两个在同一行（100+5+100=205 <= 254）
        assert pos0.y == pos1.y
        # 第三个换行（205+5+100=310 > 254），y 更大
        assert pos2.y > pos0.y

    def test_flex_stretch(self):
        """align-items: stretch — 子项交叉轴撑满"""
        from office_suite.engine.layout.flex import FlexItem as FItem
        spec = LayoutSpec(
            mode=LayoutMode.FLEX,
            flex=FlexPosition(direction=FlexDirection.ROW, align=FlexAlign.STRETCH),
        )
        items = [FItem(width=80, height=0), FItem(width=80, height=0)]
        pos0 = spec.resolve_mm(254.0, 100.0, flex_items=items, flex_index=0)

        # height 应撑满容器高度
        assert pos0.height == pytest.approx(100.0)

    def test_flex_column_wrap(self):
        """flex-direction: column + wrap — 纵向排列换列"""
        from office_suite.engine.layout.flex import FlexItem as FItem
        from office_suite.ir.layout_spec import FlexWrap
        spec = LayoutSpec(
            mode=LayoutMode.FLEX,
            flex=FlexPosition(direction=FlexDirection.COLUMN, wrap=FlexWrap.WRAP, gap=5.0),
        )
        # shrink=0 防止收缩；60*3+5*2=130 < 142.875，但 60*3+5*2+60+5=195 > 142.875
        items = [FItem(width=50, height=60, shrink=0) for _ in range(3)]
        pos0 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=0)
        pos1 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=1)
        pos2 = spec.resolve_mm(254.0, 142.875, flex_items=items, flex_index=2)

        # 前两个在同一列（60+5+60=125 <= 142.875）
        assert pos0.x == pos1.x
        # 第三个换列（125+5+60=190 > 142.875），x 更大
        assert pos2.x > pos0.x


# ============================================================
# OKLCH 工具函数
# ============================================================

class TestOKLCHUtilities:
    """engine/style/color.py 工具函数"""

    def test_roundtrip(self):
        """hex → oklch → hex 往返一致"""
        for hex_color in ["#FF0000", "#00FF00", "#0000FF", "#E8576D", "#3D1A2A"]:
            lch = hex_to_oklch(hex_color)
            result = oklch_to_hex(lch)
            assert result == hex_color, f"{hex_color} → {lch} → {result}"

    def test_palette_count(self):
        """generate_palette 返回指定数量"""
        from office_suite.engine.style.color import generate_palette
        palette = generate_palette("#E8576D", count=5)
        assert len(palette) == 5
        for c in palette:
            assert c.startswith("#")

    def test_complementary(self):
        """互补色色相旋转 180 度"""
        from office_suite.engine.style.color import complementary, rotate_hue
        # 验证 rotate_hue 在 OKLCH 层面精确旋转
        lch_orig = hex_to_oklch("#E8576D")
        rotated = rotate_hue("#E8576D", 180)
        lch_rot = hex_to_oklch(rotated)
        diff = abs(lch_rot.h - lch_orig.h)
        assert abs(diff - 180) < 2  # hex 量化误差

    def test_adjust_lightness(self):
        """调整亮度后 L 值变化"""
        from office_suite.engine.style.color import adjust_lightness
        lighter = adjust_lightness("#000000", 0.3)
        lch = hex_to_oklch(lighter)
        assert lch.l > 0.2
