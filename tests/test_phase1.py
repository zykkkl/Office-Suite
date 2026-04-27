"""Phase 1 完整测试：DSL + IR 核心

验收标准：
1. DSL 包含/属性约束校验生效
2. 文本+图片+形状+表格 IR 节点完整
3. position mm/% 映射到 EMU 正确
4. 样式级联 3 层生效
"""

import sys
from pathlib import Path
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document, compile_position, _parse_length, compile_style
from office_suite.ir.cascade import cascade_style, cascade_style_by_name, DEFAULT_THEME_STYLES
from office_suite.ir.types import (
    IRDocument, IRNode, IRPosition, IRStyle, NodeType,
    CONTAINMENT_RULES, LEAF_NODES, REQUIRED_PROPS,
    validate_ir,
)
from office_suite.ir.validator import validate_ir_v2, Severity
from office_suite.renderer.pptx.deck import PPTXRenderer


# ============================================================
# 辅助函数
# ============================================================

_pass_count = 0
_fail_count = 0


def check(name: str, condition: bool, detail: str = ""):
    global _pass_count, _fail_count
    if condition:
        _pass_count += 1
        print(f"  PASS  {name}")
    else:
        _fail_count += 1
        msg = f"  FAIL  {name}"
        if detail:
            msg += f" — {detail}"
        print(msg)


def section(title: str):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


# ============================================================
# 测试 1：包含约束校验
# ============================================================

def test_containment_rules():
    section("1. 包含约束校验")

    # DOCUMENT 可包含 SLIDE
    check("DOCUMENT → SLIDE 合法",
          NodeType.SLIDE in CONTAINMENT_RULES[NodeType.DOCUMENT])

    # DOCUMENT 不可包含 TEXT
    check("DOCUMENT → TEXT 非法",
          NodeType.TEXT not in CONTAINMENT_RULES[NodeType.DOCUMENT])

    # SLIDE 可包含 TEXT/IMAGE/SHAPE/TABLE/GROUP
    slide_children = CONTAINMENT_RULES[NodeType.SLIDE]
    check("SLIDE → TEXT 合法", NodeType.TEXT in slide_children)
    check("SLIDE → IMAGE 合法", NodeType.IMAGE in slide_children)
    check("SLIDE → SHAPE 合法", NodeType.SHAPE in slide_children)
    check("SLIDE → TABLE 合法", NodeType.TABLE in slide_children)
    check("SLIDE → GROUP 合法", NodeType.GROUP in slide_children)

    # SLIDE 不可包含 SLIDE（幻灯片不能嵌套幻灯片）
    check("SLIDE → SLIDE 非法", NodeType.SLIDE not in slide_children)

    # GROUP 可包含内容节点，不可包含 SLIDE
    group_children = CONTAINMENT_RULES[NodeType.GROUP]
    check("GROUP → TEXT 合法", NodeType.TEXT in group_children)
    check("GROUP → SLIDE 非法", NodeType.SLIDE not in group_children)

    # 叶子节点不能包含子节点
    check("TEXT 是叶子节点", NodeType.TEXT in LEAF_NODES)
    check("IMAGE 是叶子节点", NodeType.IMAGE in LEAF_NODES)


# ============================================================
# 测试 2：IR 必需属性校验
# ============================================================

def test_required_props():
    section("2. 必需属性校验")

    # TEXT 必须有 content
    check("TEXT 需要 content", "content" in REQUIRED_PROPS[NodeType.TEXT])

    # IMAGE 必须有 source
    check("IMAGE 需要 source", "source" in REQUIRED_PROPS[NodeType.IMAGE])

    # CHART 必须有 chart_type
    check("CHART 需要 chart_type", "chart_type" in REQUIRED_PROPS[NodeType.CHART])

    # 用实际 DSL 测试缺失属性校验
    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: text
        # 故意缺少 content
        position: { x: 50mm, y: 50mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    result = validate_ir_v2(ir)
    check("缺失 content 检测到 ERROR",
          any(i.severity == Severity.ERROR and "content" in i.message for i in result.issues),
          f"找到 {len(result.errors)} 个错误")


# ============================================================
# 测试 3：坐标映射 mm/% → 绝对值
# ============================================================

def test_position_mapping():
    section("3. 坐标映射 (mm/% → 绝对值)")

    # mm 解析
    val, rel, auto = _parse_length("100mm", 254)
    check("100mm → 100.0", val == 100.0, f"got {val}")
    check("100mm 非相对", not rel)

    # % 解析
    val, rel, auto = _parse_length("50%", 254)
    check("50% of 254 → 127.0", abs(val - 127.0) < 0.01, f"got {val}")
    check("50% 是相对", rel)

    # % 解析 — 高度
    val, rel, auto = _parse_length("100%", 190.5)
    check("100% of 190.5 → 190.5", abs(val - 190.5) < 0.01, f"got {val}")

    # auto 解析
    val, rel, auto = _parse_length("auto", 254)
    check("auto → 0 + is_auto", val == 0 and auto, f"val={val}, auto={auto}")

    # 数值直接传入
    val, rel, auto = _parse_length(50, 254)
    check("数值 50 → 50.0", val == 50.0)

    # None
    val, rel, auto = _parse_length(None, 254)
    check("None → 0", val == 0)

    # 完整 PositionSpec 测试
    from office_suite.dsl.schema import PositionSpec
    pos = PositionSpec(x="20mm", y="10%", width="80%", height="50mm", center=False)
    ir_pos = compile_position(pos, parent_w=254.0, parent_h=190.5)
    check("x=20mm → x_mm=20", ir_pos.x_mm == 20.0, f"got {ir_pos.x_mm}")
    check("y=10% of 190.5 → 19.05", abs(ir_pos.y_mm - 19.05) < 0.1, f"got {ir_pos.y_mm}")
    check("width=80% of 254 → 203.2", abs(ir_pos.width_mm - 203.2) < 0.1, f"got {ir_pos.width_mm}")
    check("height=50mm → 50", ir_pos.height_mm == 50.0, f"got {ir_pos.height_mm}")

    # bottom 定位
    pos2 = PositionSpec(x="0mm", bottom="10mm", width="100mm", height="20mm")
    ir_pos2 = compile_position(pos2, parent_w=254.0, parent_h=190.5)
    expected_y = 190.5 - 10 - 20  # 160.5
    check(f"bottom=10mm → y={expected_y}", abs(ir_pos2.y_mm - expected_y) < 0.1, f"got {ir_pos2.y_mm}")


# ============================================================
# 测试 4：样式级联（3 层）
# ============================================================

def test_style_cascade():
    section("4. 样式级联 (theme → document → element)")

    # 层 1：默认样式
    default = IRStyle()

    # 层 2：主题样式（模拟 "title"）
    theme_title = DEFAULT_THEME_STYLES.get("title")
    check("主题 title 样式存在", theme_title is not None)
    check("主题 title size=44", theme_title.font_size == 44)

    # 层 3：文档级全局样式
    doc_style = IRStyle(font_size=36, font_color="#FF0000")

    # 级联测试：文档样式覆盖主题样式
    result = cascade_style(default, theme_title, doc_style)
    check("级联后 font_size=36 (doc 覆盖 theme)",
          result.font_size == 36, f"got {result.font_size}")
    check("级联后 font_color=#FF0000",
          result.font_color == "#FF0000", f"got {result.font_color}")
    check("级联后 font_weight=700 (继承自 theme)",
          result.font_weight == 700, f"got {result.font_weight}")

    # 级联测试：只有主题，无文档覆盖
    result2 = cascade_style(default, theme_title)
    check("仅主题级联 size=44", result2.font_size == 44)
    check("仅主题级联 weight=700", result2.font_weight == 700)

    # 级联测试：空默认 → 无层提供值时为 None（渲染器用默认值填充）
    result3 = cascade_style(default)
    check("仅默认级联 size=None（渲染器回退）", result3.font_size is None)

    # element 内联样式覆盖所有
    inline = IRStyle(font_size=72, font_weight=900)
    result4 = cascade_style(default, theme_title, doc_style, inline)
    check("内联覆盖 size=72", result4.font_size == 72, f"got {result4.font_size}")
    check("内联覆盖 weight=900", result4.font_weight == 900, f"got {result4.font_weight}")


# ============================================================
# 测试 5：完整 DSL → IR 节点类型测试
# ============================================================

def test_ir_node_types():
    section("5. IR 节点类型完整性")

    dsl = """
version: "4.0"
type: presentation
theme: default
slides:
  - layout: blank
    elements:
      - type: text
        content: "标题"
        position: { x: 50mm, y: 50mm, width: 100mm, height: 20mm }
      - type: shape
        shape_type: rectangle
        position: { x: 20mm, y: 80mm, width: 60mm, height: 30mm }
        style:
          fill: { color: "#2563EB" }
      - type: image
        source: "file://test.png"
        position: { x: 100mm, y: 80mm, width: 50mm, height: 50mm }
      - type: table
        rows: 2
        cols: 2
        data: [["A","B"],["1","2"]]
        position: { x: 20mm, y: 120mm, width: 200mm, height: 40mm }
      - type: chart
        chart_type: bar
        data_ref: "revenue"
        position: { x: 20mm, y: 120mm, width: 200mm, height: 50mm }
      - type: group
        position: { x: 10mm, y: 10mm, width: 50mm, height: 50mm }
        children:
          - type: text
            content: "组内文本"
            position: { x: 0mm, y: 0mm, width: 40mm, height: 10mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    slide = ir.children[0]
    check("slide 有 6 个元素", len(slide.children) == 6, f"got {len(slide.children)}")

    # 检查各节点类型
    types = [c.node_type for c in slide.children]
    check("TEXT 节点", NodeType.TEXT in types)
    check("SHAPE 节点", NodeType.SHAPE in types)
    check("IMAGE 节点", NodeType.IMAGE in types)
    check("TABLE 节点", NodeType.TABLE in types)
    check("CHART 节点", NodeType.CHART in types)
    check("GROUP 节点", NodeType.GROUP in types)

    # GROUP 内有子节点
    group_node = [c for c in slide.children if c.node_type == NodeType.GROUP][0]
    check("GROUP 内有 1 个子节点", len(group_node.children) == 1, f"got {len(group_node.children)}")
    check("GROUP 子节点是 TEXT", group_node.children[0].node_type == NodeType.TEXT)

    # 校验通过
    result = validate_ir_v2(ir)
    check("IR 校验通过", result.is_valid, f"errors: {len(result.errors)}")


# ============================================================
# 测试 6：样式级联集成测试（DSL → IR）
# ============================================================

def test_cascade_integration():
    section("6. 样式级联集成 (DSL → IR)")

    dsl = """
version: "4.0"
type: presentation
theme: default
styles:
  heading:
    font:
      family: "Arial"
      size: 32
      weight: 700
      color: "#1E293B"
    fill:
      color: "#F8FAFC"
slides:
  - layout: blank
    elements:
      - type: text
        content: "全局样式标题"
        style: heading
        position: { x: 20mm, y: 20mm, width: 200mm, height: 20mm }
      - type: text
        content: "内联样式"
        style:
          font:
            size: 48
            color: "#FF0000"
        position: { x: 20mm, y: 50mm, width: 200mm, height: 20mm }
      - type: text
        content: "默认样式文本"
        position: { x: 20mm, y: 80mm, width: 200mm, height: 20mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    slide = ir.children[0]

    # 元素 1：引用全局样式 "heading"
    elem1 = slide.children[0]
    check("引用 heading 样式有 style", elem1.style is not None)
    check("heading font_size=32",
          elem1.style.font_size == 32, f"got {elem1.style.font_size}")
    check("heading font_color=#1E293B",
          elem1.style.font_color == "#1E293B", f"got {elem1.style.font_color}")
    check("heading fill_color=#F8FAFC",
          elem1.style.fill_color == "#F8FAFC", f"got {elem1.style.fill_color}")

    # 元素 2：内联样式
    elem2 = slide.children[1]
    check("内联样式有 style", elem2.style is not None)
    check("内联 font_size=48",
          elem2.style.font_size == 48, f"got {elem2.style.font_size}")
    check("内联 font_color=#FF0000",
          elem2.style.font_color == "#FF0000", f"got {elem2.style.font_color}")

    # 元素 3：默认样式（无 style 声明）→ IR 中为 None，渲染器用默认值填充
    elem3 = slide.children[2]
    check("默认样式有 style", elem3.style is not None)
    check("默认 font_size=None（渲染器回退到 18）",
          elem3.style.font_size is None, f"got {elem3.style.font_size}")

    # 校验通过
    result = validate_ir_v2(ir)
    check("IR 校验通过", result.is_valid)


# ============================================================
# 测试 7：增强版校验器
# ============================================================

def test_validator():
    section("7. 增强版 IR 校验器")

    # 故意构造一个有问题的 IR
    bad_doc = IRDocument(
        version="4.0",
        children=[
            IRNode(
                node_type=NodeType.SLIDE,
                children=[
                    # TEXT 缺少 content
                    IRNode(
                        node_type=NodeType.TEXT,
                        content=None,
                        position=IRPosition(x_mm=10, y_mm=10, width_mm=100, height_mm=20),
                    ),
                    # SHAPE 放在 SLIDE 内是合法的
                    IRNode(
                        node_type=NodeType.SHAPE,
                        position=IRPosition(x_mm=10, y_mm=40, width_mm=50, height_mm=50),
                    ),
                    # 文字节点放了一个 SLIDE 子节点（非法包含）
                    IRNode(
                        node_type=NodeType.TEXT,
                        content="test",
                        position=IRPosition(x_mm=10, y_mm=100, width_mm=50, height_mm=10),
                        children=[
                            IRNode(node_type=NodeType.SLIDE)  # 非法
                        ],
                    ),
                ],
            )
        ],
    )

    result = validate_ir_v2(bad_doc)
    check("检测到错误", not result.is_valid, f"errors: {len(result.errors)}")

    # 检查是否有缺失 content 的错误
    content_errors = [e for e in result.errors if "content" in e.message]
    check("检测到 TEXT 缺少 content", len(content_errors) > 0)

    # 检查是否有非法包含的错误
    containment_errors = [e for e in result.errors if "不可包含" in e.message]
    check("检测到非法包含约束", len(containment_errors) > 0)


# ============================================================
# 测试 8：端到端 PPTX 渲染
# ============================================================

def test_e2e_render():
    section("8. 端到端 PPTX 渲染")

    dsl = """
version: "4.0"
type: presentation
theme: default
styles:
  heading:
    font: { family: "Arial", size: 28, weight: 700, color: "#0F172A" }
  body:
    font: { family: "Microsoft YaHei UI", size: 16, weight: 400, color: "#475569" }
slides:
  - layout: blank
    background:
      gradient:
        type: linear
        angle: 180
        stops: ["#0F172A", "#334155"]
    elements:
      - type: text
        content: "Phase 1 验证页"
        style: heading
        position: { x: 30mm, y: 20mm, width: 194mm, height: 15mm }

      - type: text
        content: "样式级联 + 坐标映射 + 包含约束 + 增强校验 全部通过"
        style: body
        position: { x: 30mm, y: 40mm, width: 194mm, height: 10mm }

      - type: shape
        shape_type: rounded_rectangle
        content: "DSL → IR → PPTX"
        position: { x: 30mm, y: 60mm, width: 80mm, height: 30mm }
        style:
          fill: { color: "#2563EB" }
          font: { family: "Arial", size: 14, weight: 600, color: "#FFFFFF" }

      - type: table
        rows: 3
        cols: 2
        data: [["功能","状态"],["级联样式","PASS"],["坐标映射","PASS"]]
        position: { x: 30mm, y: 100mm, width: 194mm, height: 50mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    result = validate_ir_v2(ir)

    check("IR 校验通过", result.is_valid, f"errors: {[str(e) for e in result.errors]}")

    output = PROJECT_ROOT / "tests" / "output" / "phase1_demo.pptx"
    renderer = PPTXRenderer()
    out_path = renderer.render(ir, output)
    check("PPTX 文件生成", out_path.exists())
    check("PPTX 文件大小 > 0", out_path.stat().st_size > 0, f"{out_path.stat().st_size} bytes")


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("  Office Suite 4.0 — Phase 1 测试套件")
    print("=" * 60)

    test_containment_rules()
    test_required_props()
    test_position_mapping()
    test_style_cascade()
    test_ir_node_types()
    test_cascade_integration()
    test_validator()
    test_e2e_render()

    print(f"\n{'=' * 60}")
    print(f"  结果:  PASS={_pass_count}  FAIL={_fail_count}")
    print(f"{'=' * 60}")

    return _fail_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
