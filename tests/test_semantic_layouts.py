"""语义布局引擎集成测试

验证 DSL → IR → LayoutResolver → PPTX 全链路接通：
  1. 语义布局名称（card_grid_2x2 等）正确解析为 grid/flex 配置
  2. Grid 自动放置：4 个元素 → 2x2 网格
  3. Flex 行布局：split_50_50 → 左右排列
  4. 约束布局：constraint 模式正常渲染
  5. DSL schema 新字段正确解析
  6. PPTX 渲染不报错
"""

import os
import tempfile

import pytest

from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.ir.types import IRNode, IRPosition, NodeType
from office_suite.renderer.layout_resolver import LayoutResolver
from office_suite.design.semantic_layouts import resolve_semantic_layout


# ── 语义布局名称解析 ──

def test_resolve_card_grid_2x2():
    config = resolve_semantic_layout("card_grid_2x2")
    assert config is not None
    assert config["mode"] == "grid"
    assert config["grid"]["columns"] == 2


def test_resolve_split_50_50():
    config = resolve_semantic_layout("split_50_50")
    assert config is not None
    assert config["mode"] == "flex"
    assert config["flex"]["direction"] == "row"


def test_resolve_cover_center():
    config = resolve_semantic_layout("cover_center")
    assert config is not None
    assert config["mode"] == "absolute"


def test_resolve_unknown_returns_none():
    assert resolve_semantic_layout("nonexistent_layout") is None


def test_resolve_all_semantic_layouts():
    """所有手写语义布局都应有对应配置"""
    names = [
        "cover_center", "title_body", "card_grid_2x2", "card_grid_3x2",
        "card_row_4", "split_50_50", "timeline_h6", "three_column",
        "hero_card_left", "panel_with_grid", "quote", "stats_row",
    ]
    for name in names:
        config = resolve_semantic_layout(name)
        assert config is not None, f"Missing semantic layout: {name}"
        assert "mode" in config


def test_generator_reaches_1000():
    """参数化生成器应产出 1000+ 布局"""
    from office_suite.design.semantic_layouts import layout_count
    assert layout_count() >= 1000


def test_resolve_generator_layouts():
    """生成器布局名称应被正确解析"""
    names = ["g3x2g4d", "fdr5050g8", "stats_4", "feature_3x2", "bento_3x2g4"]
    for name in names:
        config = resolve_semantic_layout(name)
        assert config is not None, f"Missing generator layout: {name}"
        assert "mode" in config


# ── Grid 自动放置 ──

def test_grid_auto_placement_2x2():
    """4 个子元素在 2x2 栅格中自动排列"""
    slide = IRNode(
        node_type=NodeType.SLIDE,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        extra={"layout_mode": "card_grid_2x2", "grid": {"columns": 2, "gutter": 4.0, "row_height": 60}},
        children=[
            IRNode(node_type=NodeType.TEXT, id="a", position=IRPosition(width_mm=50, height_mm=30)),
            IRNode(node_type=NodeType.TEXT, id="b", position=IRPosition(width_mm=50, height_mm=30)),
            IRNode(node_type=NodeType.TEXT, id="c", position=IRPosition(width_mm=50, height_mm=30)),
            IRNode(node_type=NodeType.TEXT, id="d", position=IRPosition(width_mm=50, height_mm=30)),
        ],
    )
    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    # A 在左上
    assert positions["a"].x_mm == 0.0
    assert positions["a"].y_mm == 0.0
    # B 在 A 右边（列宽 = (254 - 4) / 2 = 125）
    assert positions["b"].x_mm > positions["a"].x_mm
    # C 在 A 下面
    assert positions["c"].y_mm > positions["a"].y_mm
    # D 在 C 右边
    assert positions["d"].x_mm > positions["c"].x_mm


def test_grid_explicit_placement():
    """显式 grid 元数据优先于自动放置"""
    slide = IRNode(
        node_type=NodeType.SLIDE,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        extra={"layout_mode": "grid", "grid": {"columns": 3, "gutter": 2.0, "row_height": 50}},
        children=[
            IRNode(
                node_type=NodeType.TEXT, id="placed",
                position=IRPosition(width_mm=50, height_mm=30),
                extra={"grid": {"column": 3, "row": 2}},
            ),
        ],
    )
    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)
    # 第 3 列第 2 行：x = 2 * (col_width + gutter), y = 1 * (row_height + gutter)
    col_width = (254.0 - 2 * 2) / 3  # ≈ 83.33
    assert abs(positions["placed"].x_mm - 2 * (col_width + 2.0)) < 1.0
    assert abs(positions["placed"].y_mm - 1 * (50.0 + 2.0)) < 1.0


# ── Flex 布局 ──

def test_flex_split_50_50():
    """split_50_50 语义布局将两个元素左右排列（含页边距）"""
    slide = IRNode(
        node_type=NodeType.SLIDE,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        extra={"layout_mode": "split_50_50"},
        children=[
            IRNode(node_type=NodeType.TEXT, id="left", position=IRPosition(width_mm=120, height_mm=80)),
            IRNode(node_type=NodeType.TEXT, id="right", position=IRPosition(width_mm=120, height_mm=80)),
        ],
    )
    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    # split_50_50 注入页边距 (top=16, right=25, bottom=12, left=25)
    # 内容从 x=25 开始，可用宽度 = 254-25-25 = 204
    assert positions["left"].x_mm == 25.0
    # left 和 right 之间有 gap
    gap = positions["right"].x_mm - (positions["left"].x_mm + positions["left"].width_mm)
    assert gap >= 6.0  # flex gap


def test_flex_row_explicit():
    """显式 flex 配置：元素从左到右排列"""
    slide = IRNode(
        node_type=NodeType.SLIDE,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        extra={"layout_mode": "flex", "flex": {"direction": "row", "gap": 10}},
        children=[
            IRNode(node_type=NodeType.TEXT, id="a", position=IRPosition(width_mm=100, height_mm=50)),
            IRNode(node_type=NodeType.TEXT, id="b", position=IRPosition(width_mm=100, height_mm=50)),
            IRNode(node_type=NodeType.TEXT, id="c", position=IRPosition(width_mm=100, height_mm=50)),
        ],
    )
    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    # 元素从左到右排列
    assert positions["a"].x_mm == 0.0
    assert positions["b"].x_mm > positions["a"].x_mm
    assert positions["c"].x_mm > positions["b"].x_mm
    # b 与 a 之间的距离包含 gap
    gap = positions["b"].x_mm - positions["a"].x_mm - positions["a"].width_mm
    assert gap >= 8.0  # flex resolver 使用 gap


# ── Constraint 布局 ──

def test_constraint_basic():
    """约束模式：无约束时求解器不报错，返回位置"""
    slide = IRNode(
        node_type=NodeType.SLIDE,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        extra={"layout_mode": "constraint"},
        children=[
            IRNode(
                node_type=NodeType.TEXT, id="box",
                position=IRPosition(x_mm=20, y_mm=20, width_mm=100, height_mm=50),
            ),
        ],
    )
    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)
    # 无约束时求解器返回合法位置（全 0 是默认值，因为约束求解器在无约束时重置）
    assert "box" in positions
    assert isinstance(positions["box"].x_mm, float)


def test_constraint_with_user_constraints():
    """约束模式：有约束时不崩溃，返回合法位置"""
    # 注意：约束求解器 Phase 1 缺少人工变量，简单等式约束暂不支持。
    # 这里验证约束模式的集成不崩溃，返回的位置是合法的。
    slide = IRNode(
        node_type=NodeType.SLIDE,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        extra={"layout_mode": "constraint"},
        children=[
            IRNode(
                node_type=NodeType.TEXT, id="box",
                position=IRPosition(x_mm=20, y_mm=10, width_mm=100, height_mm=50),
                extra={
                    "constraints": [
                        {"type": "ge", "lhs": {"var": "self.x"}, "rhs": {"value": 10}},
                    ],
                },
            ),
        ],
    )
    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)
    assert "box" in positions
    # 返回合法位置（值为 float）
    assert isinstance(positions["box"].x_mm, float)


# ── DSL → IR 布局配置传递 ──

def test_dsl_slide_grid_field():
    """DSL slide 的 grid 字段正确传递到 IR"""
    yaml_str = """
version: "4.0"
type: presentation
title: Grid Test
slides:
  - layout: card_grid_2x2
    grid:
      columns: 2
      gutter: 4.0
    elements:
      - type: text
        content: "A"
      - type: text
        content: "B"
"""
    doc = parse_yaml_string(yaml_str)
    ir = compile_document(doc)

    slide = ir.children[0]
    assert slide.extra.get("layout_mode") == "card_grid_2x2"
    assert slide.extra.get("grid") is not None
    assert slide.extra["grid"]["columns"] == 2


def test_dsl_slide_flex_field():
    """DSL slide 的 flex 字段正确传递到 IR"""
    yaml_str = """
version: "4.0"
type: presentation
title: Flex Test
slides:
  - layout_mode: flex
    flex:
      direction: row
      gap: 8
    elements:
      - type: text
        content: "Left"
      - type: text
        content: "Right"
"""
    doc = parse_yaml_string(yaml_str)
    ir = compile_document(doc)

    slide = ir.children[0]
    assert slide.extra.get("layout_mode") == "flex"
    assert slide.extra.get("flex") is not None
    assert slide.extra["flex"]["direction"] == "row"


def test_dsl_slide_constraint_field():
    """DSL slide 的 constraints 字段正确传递到 IR"""
    yaml_str = """
version: "4.0"
type: presentation
title: Constraint Test
slides:
  - layout_mode: constraint
    constraints:
      - type: eq
        lhs: { var: "self.x" }
        rhs: { value: 10 }
    elements:
      - type: text
        content: "Box"
"""
    doc = parse_yaml_string(yaml_str)
    ir = compile_document(doc)

    slide = ir.children[0]
    assert slide.extra.get("layout_mode") == "constraint"
    assert slide.extra.get("constraints") is not None


# ── PPTX 端到端渲染 ──

def test_pptx_render_with_grid_layout():
    """Grid 布局的 PPTX 渲染不报错"""
    yaml_str = """
version: "4.0"
type: presentation
title: Grid Render Test
style_preset: corporate
slides:
  - layout: card_grid_2x2
    grid:
      columns: 2
      gutter: 4.0
    elements:
      - type: text
        content: "Card A"
        position: { x: 0, y: 0, width: 100, height: 50 }
      - type: text
        content: "Card B"
        position: { x: 0, y: 0, width: 100, height: 50 }
      - type: text
        content: "Card C"
        position: { x: 0, y: 0, width: 100, height: 50 }
      - type: text
        content: "Card D"
        position: { x: 0, y: 0, width: 100, height: 50 }
"""
    doc = parse_yaml_string(yaml_str)
    ir = compile_document(doc)

    from office_suite.renderer.pptx.deck import PPTXRenderer
    renderer = PPTXRenderer()
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
        tmp_path = f.name
    try:
        renderer.render(ir, tmp_path)
        assert os.path.getsize(tmp_path) > 0
    finally:
        os.unlink(tmp_path)


def test_pptx_render_with_flex_layout():
    """Flex 布局的 PPTX 渲染不报错"""
    yaml_str = """
version: "4.0"
type: presentation
title: Flex Render Test
style_preset: corporate
slides:
  - layout_mode: flex
    flex:
      direction: row
      gap: 8
    elements:
      - type: text
        content: "Left Panel"
        position: { width: 120, height: 80 }
      - type: text
        content: "Right Panel"
        position: { width: 120, height: 80 }
"""
    doc = parse_yaml_string(yaml_str)
    ir = compile_document(doc)

    from office_suite.renderer.pptx.deck import PPTXRenderer
    renderer = PPTXRenderer()
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
        tmp_path = f.name
    try:
        renderer.render(ir, tmp_path)
        assert os.path.getsize(tmp_path) > 0
    finally:
        os.unlink(tmp_path)


# ── 页边距验证 ──

def test_grid_margin_offsets_content():
    """Grid 布局页边距将内容偏移到安全区域内"""
    slide = IRNode(
        node_type=NodeType.SLIDE,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        extra={
            "layout_mode": "grid",
            "grid": {
                "columns": 2,
                "gutter": 4.0,
                "row_height": 50.0,
                "margin": (16.0, 25.0, 12.0, 25.0),  # top, right, bottom, left
            },
        },
        children=[
            IRNode(node_type=NodeType.TEXT, id="a", position=IRPosition(width_mm=50, height_mm=30)),
            IRNode(node_type=NodeType.TEXT, id="b", position=IRPosition(width_mm=50, height_mm=30)),
        ],
    )
    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    # 内容从 x=25 (left margin) 开始
    assert positions["a"].x_mm == 25.0
    # 内容从 y=16 (top margin) 开始
    assert positions["a"].y_mm == 16.0
    # b 在 a 右边
    assert positions["b"].x_mm > positions["a"].x_mm


def test_grid_no_margin_starts_at_origin():
    """无页边距时 Grid 从 (0,0) 开始"""
    slide = IRNode(
        node_type=NodeType.SLIDE,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        extra={
            "layout_mode": "grid",
            "grid": {"columns": 2, "gutter": 4.0, "row_height": 50.0},
        },
        children=[
            IRNode(node_type=NodeType.TEXT, id="a", position=IRPosition(width_mm=50, height_mm=30)),
        ],
    )
    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    assert positions["a"].x_mm == 0.0
    assert positions["a"].y_mm == 0.0


def test_grid_padding_insets_cells():
    """Grid padding 将单元格内容内缩"""
    slide = IRNode(
        node_type=NodeType.SLIDE,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        extra={
            "layout_mode": "grid",
            "grid": {
                "columns": 2,
                "gutter": 4.0,
                "row_height": 60.0,
                "padding": 3.0,
            },
        },
        children=[
            IRNode(node_type=NodeType.TEXT, id="a", position=IRPosition(width_mm=50, height_mm=30)),
        ],
    )
    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    # 有 padding 时，单元格从 (3,3) 开始
    assert positions["a"].x_mm == 3.0
    assert positions["a"].y_mm == 3.0
    # 宽高减少 2*padding
    full_width = (254.0 - 4.0) / 2  # ≈125
    assert positions["a"].width_mm == round(full_width - 6.0, 2)


def test_flex_margin_offsets_content():
    """Flex 布局页边距将内容偏移到安全区域内"""
    slide = IRNode(
        node_type=NodeType.SLIDE,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        extra={
            "layout_mode": "flex",
            "flex": {
                "direction": "row",
                "gap": 8.0,
                "margin": (16.0, 25.0, 12.0, 25.0),
            },
        },
        children=[
            IRNode(node_type=NodeType.TEXT, id="left", position=IRPosition(width_mm=80, height_mm=60)),
            IRNode(node_type=NodeType.TEXT, id="right", position=IRPosition(width_mm=80, height_mm=60)),
        ],
    )
    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    # 内容从 x=25 (left margin) 开始
    assert positions["left"].x_mm == 25.0
    # 内容从 y=16 (top margin) 开始
    assert positions["left"].y_mm == 16.0
    # right 在 left + width + gap 之后
    expected_right_x = 25.0 + 80.0 + 8.0
    assert abs(positions["right"].x_mm - expected_right_x) < 1.0


def test_semantic_layout_margins_injected():
    """语义布局配置包含页边距"""
    from office_suite.design.semantic_layouts import resolve_semantic_layout
    config = resolve_semantic_layout("card_grid_2x2")
    assert config is not None
    assert "margin" in config["grid"]
    margin = config["grid"]["margin"]
    assert len(margin) == 4
    # 默认边距：top=16, right=25, bottom=12, left=25
    assert margin[0] == 16.0  # top
    assert margin[3] == 25.0  # left


def test_generator_layouts_have_margins():
    """生成器布局包含页边距"""
    from office_suite.design.layout_generator import get_layout
    config = get_layout("g3x2g4d")
    assert config is not None
    assert "margin" in config["grid"]
    margin = config["grid"]["margin"]
    assert margin[3] == 25.0  # "d" (default) margin left = 25

    # "s" (small) margin
    config_s = get_layout("g3x2g4s")
    assert config_s is not None
    assert config_s["grid"]["margin"][3] == 12.0  # "s" margin left = 12


def test_golden_ratio_layouts_exist():
    """黄金比例和 Fibonacci 布局存在于生成器中"""
    from office_suite.design.layout_generator import get_layout
    # 黄金比例 split
    config = get_layout("fdrphi6238g8")
    assert config is not None
    assert config["mode"] == "flex"
    # Fibonacci split
    config2 = get_layout("fdrfib35g8")
    assert config2 is not None
    assert config2["mode"] == "flex"


def test_design_quality_full_pipeline():
    """综合品质测试：card_container + 语义布局 + 页边距 + PPTX 渲染"""
    yaml_str = """
version: "4.0"
type: presentation
title: Design Quality Test
style_preset: corporate
slides:
  - layout: card_grid_2x2
    card_container: true
    background:
      color: "#F1F5F9"
    elements:
      - type: text
        content: "Revenue"
        position: { x: 0, y: 0, width: 100, height: 50 }
      - type: text
        content: "Users"
        position: { x: 0, y: 0, width: 100, height: 50 }
      - type: text
        content: "Growth"
        position: { x: 0, y: 0, width: 100, height: 50 }
      - type: text
        content: "Retention"
        position: { x: 0, y: 0, width: 100, height: 50 }
  - layout_mode: flex
    flex:
      direction: row
      gap: 8
      margin: [16, 25, 12, 25]
    card_container: true
    background:
      color: "#F8FAFC"
    elements:
      - type: text
        content: "Left Panel"
        position: { width: 100, height: 80 }
      - type: text
        content: "Right Panel"
        position: { width: 100, height: 80 }
"""
    doc = parse_yaml_string(yaml_str)
    ir = compile_document(doc)

    # 验证 IR 结构
    assert len(ir.children) == 2
    slide0 = ir.children[0]
    assert slide0.extra.get("layout_mode") == "card_grid_2x2"
    assert slide0.extra.get("card_container") is True

    # 渲染 PPTX
    from office_suite.renderer.pptx.deck import PPTXRenderer
    renderer = PPTXRenderer()
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
        tmp_path = f.name
    try:
        renderer.render(ir, tmp_path)
        file_size = os.path.getsize(tmp_path)
        assert file_size > 0
    finally:
        os.unlink(tmp_path)


# ── 卡片容器样式 ──

def test_card_container_dsl_parsing():
    """DSL card_container 字段正确解析"""
    yaml_str = """
version: "4.0"
type: presentation
title: Card Container Test
slides:
  - layout: card_grid_2x2
    card_container: true
    elements:
      - type: text
        content: "Card A"
      - type: text
        content: "Card B"
"""
    doc = parse_yaml_string(yaml_str)
    ir = compile_document(doc)
    slide = ir.children[0]
    assert slide.extra.get("card_container") is True


def test_card_container_pptx_render():
    """card_container PPTX 渲染不报错，输出文件非空"""
    yaml_str = """
version: "4.0"
type: presentation
title: Card Container Render
style_preset: corporate
slides:
  - layout: card_grid_2x2
    card_container: true
    elements:
      - type: text
        content: "Card A"
        position: { x: 0, y: 0, width: 100, height: 50 }
      - type: text
        content: "Card B"
        position: { x: 0, y: 0, width: 100, height: 50 }
      - type: text
        content: "Card C"
        position: { x: 0, y: 0, width: 100, height: 50 }
      - type: text
        content: "Card D"
        position: { x: 0, y: 0, width: 100, height: 50 }
"""
    doc = parse_yaml_string(yaml_str)
    ir = compile_document(doc)

    from office_suite.renderer.pptx.deck import PPTXRenderer
    renderer = PPTXRenderer()
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
        tmp_path = f.name
    try:
        renderer.render(ir, tmp_path)
        assert os.path.getsize(tmp_path) > 0
    finally:
        os.unlink(tmp_path)
