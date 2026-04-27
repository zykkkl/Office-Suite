"""Phase 2 测试套件：PPTX 渲染器核心完善

验收标准：
1. 母版布局渲染正确
2. 图表/表格数据绑定生效
3. 渐变/阴影/主题色输出正确
4. IR→PPTX 映射测试 20+ 用例通过
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.ir.validator import validate_ir_v2
from office_suite.ir.types import IRDocument, IRNode, IRPosition, IRStyle, NodeType
from office_suite.renderer.pptx.deck import PPTXRenderer, CHART_TYPE_MAP


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


def render_dsl(dsl: str, name: str = "test") -> tuple[IRDocument, Path]:
    """解析 + 编译 + 渲染，返回 IR 和输出路径"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    output = PROJECT_ROOT / "tests" / "output" / f"phase2_{name}.pptx"
    renderer = PPTXRenderer()
    renderer.render(ir, output)
    return ir, output


# ============================================================
# 测试 1-4: 母版布局
# ============================================================

def test_master_layouts():
    section("1. 母版布局")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: text
        content: "Blank Layout"
        position: { x: 20mm, y: 20mm, width: 200mm, height: 20mm }
  - layout: title
    elements:
      - type: text
        content: "Title Layout"
        position: { x: 20mm, y: 20mm, width: 200mm, height: 20mm }
  - layout: title_content
    elements:
      - type: text
        content: "Title+Content Layout"
        position: { x: 20mm, y: 20mm, width: 200mm, height: 20mm }
"""
    ir, output = render_dsl(dsl, "layouts")
    check("3 张幻灯片", len(ir.children) == 3, f"got {len(ir.children)}")
    check("文件生成成功", output.exists())
    check("文件大小 > 0", output.stat().st_size > 0, f"{output.stat().st_size} bytes")

    # 验证布局名称映射
    renderer = PPTXRenderer()
    check("blank → 6", renderer._get_layout_index("blank") == 6)
    check("title → 0", renderer._get_layout_index("title") == 0)
    check("title_content → 1", renderer._get_layout_index("title_content") == 1)
    check("section → 2", renderer._get_layout_index("section") == 2)


# ============================================================
# 测试 5-9: 图表渲染
# ============================================================

def test_chart_rendering():
    section("2. 图表渲染")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: chart
        chart_type: bar
        position: { x: 20mm, y: 20mm, width: 210mm, height: 100mm }
        extra:
          title: "季度营收"
          categories: ["Q1", "Q2", "Q3", "Q4"]
          series:
            - name: "营收"
              values: [100, 120, 150, 180]
            - name: "利润"
              values: [30, 40, 50, 60]
          colors: ["#2563EB", "#16A34A"]

      - type: chart
        chart_type: line
        position: { x: 20mm, y: 125mm, width: 210mm, height: 60mm }
        extra:
          title: "趋势线"
          categories: ["1月", "2月", "3月"]
          series:
            - name: "用户数"
              values: [1000, 1500, 2200]

      - type: chart
        chart_type: pie
        position: { x: 20mm, y: 20mm, width: 80mm, height: 80mm }
        extra:
          categories: ["产品A", "产品B", "产品C"]
          series:
            - name: "占比"
              values: [40, 35, 25]
"""
    ir, output = render_dsl(dsl, "charts")
    check("图表 DSL 解析", len(ir.children) == 1)
    slide = ir.children[0]
    check("3 个图表元素", len(slide.children) == 3, f"got {len(slide.children)}")

    # 检查图表类型映射
    check("bar → XL_CHART_TYPE", "bar" in CHART_TYPE_MAP)
    check("line → XL_CHART_TYPE", "line" in CHART_TYPE_MAP)
    check("pie → XL_CHART_TYPE", "pie" in CHART_TYPE_MAP)
    check("column → XL_CHART_TYPE", "column" in CHART_TYPE_MAP)
    check("scatter → XL_CHART_TYPE", "scatter" in CHART_TYPE_MAP)

    # 验证渲染
    check("图表 PPTX 生成", output.exists())
    check("图表 PPTX > 10KB", output.stat().st_size > 10000, f"{output.stat().st_size} bytes")


# ============================================================
# 测试 10-13: 表格样式
# ============================================================

def test_table_styling():
    section("3. 表格样式增强")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: table
        rows: 4
        cols: 3
        data:
          - ["名称", "数值", "状态"]
          - ["项目A", "100", "完成"]
          - ["项目B", "200", "进行中"]
          - ["项目C", "150", "计划"]
        position: { x: 20mm, y: 20mm, width: 210mm, height: 80mm }
"""
    ir, output = render_dsl(dsl, "tables")
    slide = ir.children[0]
    check("表格元素存在", len(slide.children) == 1)
    table_node = slide.children[0]
    check("节点类型 TABLE", table_node.node_type == NodeType.TABLE)
    check("行数=4", table_node.extra.get("rows") == 4)
    check("列数=3", table_node.extra.get("cols") == 3)
    check("内联数据", len(table_node.extra.get("data", [])) == 4)

    check("表格 PPTX 生成", output.exists())


# ============================================================
# 测试 14-17: 渐变填充
# ============================================================

def test_gradient_fill():
    section("4. 渐变填充")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    background:
      gradient:
        type: linear
        angle: 135
        stops: ["#0F172A", "#1E293B"]
    elements:
      - type: shape
        shape_type: rounded_rectangle
        content: "渐变卡片"
        position: { x: 30mm, y: 30mm, width: 80mm, height: 50mm }
        style:
          fill:
            gradient:
              type: linear
              angle: 90
              stops: ["#2563EB", "#7C3AED"]
          font:
            size: 16
            color: "#FFFFFF"
            weight: 600

      - type: shape
        shape_type: circle
        position: { x: 140mm, y: 30mm, width: 50mm, height: 50mm }
        style:
          fill:
            color: "#16A34A"
            opacity: 0.8
"""
    ir, output = render_dsl(dsl, "gradients")
    slide = ir.children[0]

    # 检查背景渐变
    bg = slide.extra.get("background", {})
    check("背景有渐变", "gradient" in bg)
    check("渐变类型 linear", bg.get("gradient", {}).get("type") == "linear")
    check("渐变角度 135", bg.get("gradient", {}).get("angle") == 135)

    # 检查形状渐变
    shape1 = slide.children[0]
    check("形状有渐变填充", shape1.style.fill_gradient is not None)

    # 检查纯色 + 透明度
    shape2 = slide.children[1]
    check("纯色填充", shape2.style.fill_color == "#16A34A")

    check("渐变 PPTX 生成", output.exists())


# ============================================================
# 测试 18-20: 阴影/边框
# ============================================================

def test_shadow_border():
    section("5. 阴影 & 边框")

    dsl = """
version: "4.0"
type: presentation
styles:
  card:
    font: { size: 14, color: "#1E293B" }
    fill: { color: "#FFFFFF" }
    shadow: { blur: 8, offset: [0, 4], color: "#00000020" }
slides:
  - layout: blank
    elements:
      - type: shape
        shape_type: rounded_rectangle
        content: "阴影卡片"
        style: card
        position: { x: 30mm, y: 30mm, width: 80mm, height: 50mm }
        outline:
          color: "#E2E8F0"
          width: 1

      - type: shape
        shape_type: rectangle
        content: "虚线边框"
        position: { x: 140mm, y: 30mm, width: 80mm, height: 50mm }
        style:
          fill: { color: "#F8FAFC" }
          font: { size: 12, color: "#64748B" }
        outline:
          color: "#94A3B8"
          width: 1
          dash: dashed
"""
    ir, output = render_dsl(dsl, "shadows")
    slide = ir.children[0]

    card = slide.children[0]
    check("卡片有阴影", card.style.shadow is not None)
    check("阴影 blur=8", card.style.shadow.get("blur") == 8)
    check("卡片有边框", card.extra.get("outline") is not None)

    dashed = slide.children[1]
    check("虚线边框", dashed.extra.get("outline", {}).get("dash") == "dashed")

    check("阴影/边框 PPTX 生成", output.exists())


# ============================================================
# 测试 21-23: 形状类型
# ============================================================

def test_shape_types():
    section("6. 形状类型")

    renderer = PPTXRenderer()
    shapes = ["rectangle", "rounded_rectangle", "circle", "oval",
              "triangle", "diamond", "arrow", "star", "hexagon", "pentagon"]
    for s in shapes:
        check(f"形状 {s} 有映射", renderer._get_shape_type(s) is not None)

    # 未知形状降级为 rectangle
    from pptx.enum.shapes import MSO_SHAPE
    check("未知形状 → RECTANGLE",
          renderer._get_shape_type("unknown") == MSO_SHAPE.RECTANGLE)


# ============================================================
# 测试 24-25: 坐标居中 + 底部定位
# ============================================================

def test_position_extras():
    section("7. 坐标居中 & 底部定位")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: text
        content: "居中标题"
        position: { x: 0mm, y: 50mm, width: 254mm, height: 20mm, center: true }
        style: { font: { size: 36, weight: 700 } }

      - type: text
        content: "底部页码"
        position: { x: 0mm, bottom: 10mm, width: 254mm, height: 10mm }
        style: { font: { size: 12, color: "#94A3B8" } }
"""
    ir, output = render_dsl(dsl, "positioning")
    slide = ir.children[0]

    centered = slide.children[0]
    check("居中元素标记", centered.position.is_center)

    bottom = slide.children[1]
    check("底部定位 y > 150mm", bottom.position.y_mm > 150, f"y={bottom.position.y_mm}")

    check("坐标 PPTX 生成", output.exists())


# ============================================================
# 测试 26-27: GROUP 嵌套
# ============================================================

def test_group_nesting():
    section("8. GROUP 嵌套渲染")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: group
        position: { x: 20mm, y: 20mm, width: 100mm, height: 80mm }
        children:
          - type: text
            content: "组标题"
            position: { x: 0mm, y: 0mm, width: 100mm, height: 15mm }
            style: { font: { size: 18, weight: 700 } }
          - type: text
            content: "组内容"
            position: { x: 0mm, y: 20mm, width: 100mm, height: 10mm }
            style: { font: { size: 14, color: "#64748B" } }
          - type: shape
            shape_type: rectangle
            position: { x: 0mm, y: 40mm, width: 60mm, height: 20mm }
            style: { fill: { color: "#EFF6FF" } }
"""
    ir, output = render_dsl(dsl, "groups")
    slide = ir.children[0]
    group = slide.children[0]
    check("GROUP 节点", group.node_type == NodeType.GROUP)
    check("GROUP 有 3 个子元素", len(group.children) == 3)
    check("GROUP PPTX 生成", output.exists())


# ============================================================
# 测试 28-30: 样式级联集成
# ============================================================

def test_style_cascade_integration():
    section("9. 样式级联集成")

    dsl = """
version: "4.0"
type: presentation
theme: default
styles:
  heading:
    font: { family: "Arial", size: 28, weight: 700, color: "#0F172A" }
  body:
    font: { family: "Microsoft YaHei UI", size: 16, color: "#475569" }
slides:
  - layout: blank
    elements:
      - type: text
        content: "全局样式标题"
        style: heading
        position: { x: 20mm, y: 20mm, width: 200mm, height: 15mm }

      - type: text
        content: "内联覆盖"
        style: { font: { size: 48, color: "#FF0000" } }
        position: { x: 20mm, y: 40mm, width: 200mm, height: 20mm }

      - type: text
        content: "默认样式"
        position: { x: 20mm, y: 65mm, width: 200mm, height: 10mm }
"""
    ir, output = render_dsl(dsl, "cascade")
    slide = ir.children[0]

    heading = slide.children[0]
    check("heading font_size=28", heading.style.font_size == 28)
    check("heading font_color=#0F172A", heading.style.font_color == "#0F172A")

    inline = slide.children[1]
    check("内联 font_size=48", inline.style.font_size == 48)
    check("内联 font_color=#FF0000", inline.style.font_color == "#FF0000")

    default = slide.children[2]
    check("默认 font_size=None", default.style.font_size is None)

    check("级联 PPTX 生成", output.exists())


# ============================================================
# 测试 31-33: 端到端综合
# ============================================================

def test_e2e_comprehensive():
    section("10. 端到端综合演示")

    dsl = """
version: "4.0"
type: presentation
styles:
  title:
    font: { family: "Arial", size: 36, weight: 700, color: "#FFFFFF" }
  subtitle:
    font: { family: "Microsoft YaHei UI", size: 18, color: "#CBD5E1" }
  body:
    font: { family: "Microsoft YaHei UI", size: 14, color: "#334155" }
slides:
  # 封面
  - layout: blank
    background:
      gradient: { type: linear, angle: 135, stops: ["#0F172A", "#1E40AF"] }
    elements:
      - type: text
        content: "Office Suite 4.0"
        style: title
        position: { x: 30mm, y: 60mm, width: 194mm, height: 20mm }
      - type: text
        content: "Phase 2 PPTX 渲染器核心完善"
        style: subtitle
        position: { x: 30mm, y: 85mm, width: 194mm, height: 10mm }

  # 图表页
  - layout: blank
    elements:
      - type: text
        content: "数据可视化"
        style: { font: { size: 24, weight: 700, color: "#0F172A" } }
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
      - type: chart
        chart_type: column
        position: { x: 20mm, y: 30mm, width: 214mm, height: 100mm }
        extra:
          title: "月度数据"
          categories: ["1月", "2月", "3月", "4月", "5月", "6月"]
          series:
            - name: "销售额"
              values: [120, 150, 180, 200, 220, 260]
            - name: "成本"
              values: [80, 90, 100, 110, 120, 140]
          colors: ["#2563EB", "#F97316"]

  # 表格页
  - layout: blank
    elements:
      - type: text
        content: "项目进度"
        style: { font: { size: 24, weight: 700, color: "#0F172A" } }
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
      - type: table
        rows: 5
        cols: 4
        data:
          - ["项目", "负责人", "进度", "状态"]
          - ["Alpha", "张三", "80%", "进行中"]
          - ["Beta", "李四", "100%", "完成"]
          - ["Gamma", "王五", "50%", "进行中"]
          - ["Delta", "赵六", "20%", "计划中"]
        position: { x: 20mm, y: 30mm, width: 214mm, height: 80mm }
"""
    ir, output = render_dsl(dsl, "comprehensive")
    check("3 张幻灯片", len(ir.children) == 3)

    result = validate_ir_v2(ir)
    check("IR 校验通过", result.is_valid, f"errors: {len(result.errors)}")

    check("综合 PPTX 生成", output.exists())
    check("综合 PPTX > 20KB", output.stat().st_size > 20000, f"{output.stat().st_size} bytes")


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("  Office Suite 4.0 — Phase 2 测试套件")
    print("=" * 60)

    test_master_layouts()
    test_chart_rendering()
    test_table_styling()
    test_gradient_fill()
    test_shadow_border()
    test_shape_types()
    test_position_extras()
    test_group_nesting()
    test_style_cascade_integration()
    test_e2e_comprehensive()

    print(f"\n{'=' * 60}")
    print(f"  结果:  PASS={_pass_count}  FAIL={_fail_count}")
    print(f"{'=' * 60}")

    return _fail_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
