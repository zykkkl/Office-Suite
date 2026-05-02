"""Phase 4 测试套件：DOCX + XLSX 渲染器

验收标准：
1. DOCX：标题/段落/表格/图片/样式级联
2. XLSX：Sheet/数据/图表/条件格式
3. 各渲染器 capability 声明 + 降级路径
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.ir.validator import validate_ir_v2
from office_suite.ir.types import IRDocument, IRNode, NodeType
from office_suite.renderer.docx.document import DOCXRenderer
from office_suite.renderer.xlsx.workbook import XLSXRenderer


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
# 测试 1-4: DOCX 渲染器能力声明
# ============================================================

def test_docx_capability():
    section("1. DOCX 渲染器能力声明")

    renderer = DOCXRenderer()
    cap = renderer.capability

    check("支持 TEXT", NodeType.TEXT in cap.supported_node_types)
    check("支持 TABLE", NodeType.TABLE in cap.supported_node_types)
    check("支持 IMAGE", NodeType.IMAGE in cap.supported_node_types)
    check("不支持 CHART", NodeType.CHART not in cap.supported_node_types)
    check("不支持动画", len(cap.supported_animations) == 0)
    check("不支持艺术字", len(cap.supported_text_transforms) == 0)
    check("有降级映射", len(cap.fallback_map) > 0)


# ============================================================
# 测试 5-9: DOCX 渲染 — 文本 + 标题
# ============================================================

def test_docx_text():
    section("2. DOCX 文本渲染")

    dsl = """
version: "4.0"
type: document
styles:
  heading:
    font: { size: 32, weight: 700, color: "#0F172A" }
  body:
    font: { size: 14, color: "#334155" }
slides:
  - layout: blank
    elements:
      - type: text
        content: "文档标题"
        style: heading
        position: { x: 20mm, y: 20mm, width: 200mm, height: 15mm }
      - type: text
        content: "这是正文段落，应该渲染为普通段落。"
        style: body
        position: { x: 20mm, y: 40mm, width: 200mm, height: 10mm }
      - type: text
        content: "子标题"
        style: { font: { size: 22, weight: 700 } }
        position: { x: 20mm, y: 55mm, width: 200mm, height: 10mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    result = validate_ir_v2(ir)
    check("IR 校验通过", result.is_valid)

    output = PROJECT_ROOT / "tests" / "output" / "phase4_docx_text.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    check("DOCX 文件生成", out_path.exists())
    check("DOCX > 5KB", out_path.stat().st_size > 5000, f"{out_path.stat().st_size} bytes")


# ============================================================
# 测试 10-13: DOCX 渲染 — 表格
# ============================================================

def test_docx_table():
    section("3. DOCX 表格渲染")

    dsl = """
version: "4.0"
type: document
slides:
  - layout: blank
    elements:
      - type: text
        content: "项目进度表"
        style: { font: { size: 24, weight: 700 } }
        position: { x: 20mm, y: 20mm, width: 200mm, height: 12mm }
      - type: table
        rows: 4
        cols: 3
        data:
          - ["项目", "状态", "进度"]
          - ["Alpha", "进行中", "80%"]
          - ["Beta", "完成", "100%"]
          - ["Gamma", "计划", "20%"]
        position: { x: 20mm, y: 40mm, width: 200mm, height: 60mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase4_docx_table.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    check("DOCX 表格生成", out_path.exists())


# ============================================================
# 测试 14-17: DOCX 渲染 — 形状降级
# ============================================================

def test_docx_shape_fallback():
    section("4. DOCX 形状降级")

    dsl = """
version: "4.0"
type: document
slides:
  - layout: blank
    elements:
      - type: shape
        shape_type: rounded_rectangle
        content: "这是一个形状卡片"
        style:
          fill: { color: "#EFF6FF" }
          font: { size: 14, color: "#2563EB" }
        position: { x: 20mm, y: 20mm, width: 80mm, height: 30mm }
      - type: shape
        shape_type: circle
        position: { x: 120mm, y: 20mm, width: 40mm, height: 40mm }
        style: { fill: { color: "#16A34A" } }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase4_docx_shape.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    check("DOCX 形状降级生成", out_path.exists())

    # 检查 capability 降级路径
    cap = renderer.capability
    check("gradient_fill 降级为 solid_fill", cap.get_fallback("gradient_fill") == "solid_fill")


# ============================================================
# 测试 18-21: XLSX 渲染器能力声明
# ============================================================

def test_xlsx_capability():
    section("5. XLSX 渲染器能力声明")

    renderer = XLSXRenderer()
    cap = renderer.capability

    check("支持 TABLE", NodeType.TABLE in cap.supported_node_types)
    check("支持 CHART", NodeType.CHART in cap.supported_node_types)
    check("支持 TEXT", NodeType.TEXT in cap.supported_node_types)
    check("不支持 IMAGE", NodeType.IMAGE not in cap.supported_node_types)


# ============================================================
# 测试 22-26: XLSX 渲染 — 表格数据
# ============================================================

def test_xlsx_table():
    section("6. XLSX 表格渲染")

    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    elements:
      - type: table
        rows: 5
        cols: 4
        data:
          - ["产品", "Q1", "Q2", "Q3"]
          - ["产品A", 100, 120, 150]
          - ["产品B", 80, 90, 110]
          - ["产品C", 60, 70, 85]
          - ["合计", 240, 280, 345]
        position: { x: 0mm, y: 0mm, width: 200mm, height: 100mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase4_xlsx_table.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    check("XLSX 文件生成", out_path.exists())
    check("XLSX > 3KB", out_path.stat().st_size > 3000, f"{out_path.stat().st_size} bytes")


# ============================================================
# 测试 27-30: XLSX 渲染 — 图表
# ============================================================

def test_xlsx_chart():
    section("7. XLSX 图表渲染")

    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    elements:
      - type: table
        rows: 5
        cols: 3
        data:
          - ["月份", "营收", "成本"]
          - ["1月", 120, 80]
          - ["2月", 150, 90]
          - ["3月", 180, 100]
          - ["4月", 200, 110]
        position: { x: 0mm, y: 0mm }
      - type: chart
        chart_type: bar
        position: { x: 0mm, y: 80mm }
        extra:
          title: "月度对比"
          categories: ["1月", "2月", "3月", "4月"]
          series:
            - name: "营收"
              values: [120, 150, 180, 200]
            - name: "成本"
              values: [80, 90, 100, 110]
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase4_xlsx_chart.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    check("XLSX 图表生成", out_path.exists())
    check("XLSX 图表 > 5KB", out_path.stat().st_size > 5000, f"{out_path.stat().st_size} bytes")


# ============================================================
# 测试 31-33: XLSX 多 Sheet
# ============================================================

def test_xlsx_multi_sheet():
    section("8. XLSX 多 Sheet")

    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    extra: { title: "销售数据" }
    elements:
      - type: table
        rows: 2
        cols: 2
        data: [["月份","销售额"],["1月",1000]]
        position: { x: 0mm, y: 0mm }
  - layout: blank
    extra: { title: "成本分析" }
    elements:
      - type: table
        rows: 2
        cols: 2
        data: [["项目","金额"],["人力",500]]
        position: { x: 0mm, y: 0mm }
  - layout: blank
    extra: { title: "图表汇总" }
    elements:
      - type: chart
        chart_type: pie
        extra:
          categories: ["产品A", "产品B"]
          series:
            - name: "占比"
              values: [60, 40]
        position: { x: 0mm, y: 0mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase4_xlsx_multi.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    check("XLSX 多 Sheet 生成", out_path.exists())


# ============================================================
# 测试 34-35: 端到端 DOCX + XLSX 综合
# ============================================================

def test_e2e_comprehensive():
    section("9. 端到端 DOCX + XLSX 综合")

    dsl = """
version: "4.0"
type: document
styles:
  title: { font: { size: 28, weight: 700, color: "#0F172A" } }
  body: { font: { size: 12, color: "#475569" } }
slides:
  - layout: blank
    elements:
      - type: text
        content: "Office Suite 4.0 阶段报告"
        style: title
        position: { x: 20mm, y: 20mm, width: 200mm, height: 15mm }
      - type: text
        content: "本文档由 Office Suite 4.0 引擎自动生成。"
        style: body
        position: { x: 20mm, y: 40mm, width: 200mm, height: 10mm }
      - type: table
        rows: 4
        cols: 3
        data:
          - ["阶段", "状态", "测试数"]
          - ["Phase 0", "完成", "4"]
          - ["Phase 1", "完成", "65"]
          - ["Phase 2", "完成", "60"]
        position: { x: 20mm, y: 60mm, width: 200mm, height: 50mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    # DOCX
    docx_out = PROJECT_ROOT / "tests" / "output" / "phase4_e2e.docx"
    docx_renderer = DOCXRenderer()
    docx_path = docx_renderer.render(ir, docx_out)
    check("DOCX 综合生成", docx_path.exists())

    # XLSX
    xlsx_dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    elements:
      - type: table
        rows: 4
        cols: 3
        data:
          - ["阶段", "状态", "测试数"]
          - ["Phase 0", "完成", 4]
          - ["Phase 1", "完成", 65]
          - ["Phase 2", "完成", 60]
        position: { x: 0mm, y: 0mm }
      - type: chart
        chart_type: column
        extra:
          title: "测试趋势"
          categories: ["Phase 0", "Phase 1", "Phase 2"]
          series:
            - name: "测试数"
              values: [4, 65, 60]
        position: { x: 0mm, y: 60mm }
"""
    xlsx_doc = parse_yaml_string(xlsx_dsl)
    xlsx_ir = compile_document(xlsx_doc)

    xlsx_out = PROJECT_ROOT / "tests" / "output" / "phase4_e2e.xlsx"
    xlsx_renderer = XLSXRenderer()
    xlsx_path = xlsx_renderer.render(xlsx_ir, xlsx_out)
    check("XLSX 综合生成", xlsx_path.exists())


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("  Office Suite 4.0 — Phase 4 测试套件")
    print("=" * 60)

    test_docx_capability()
    test_docx_text()
    test_docx_table()
    test_docx_shape_fallback()
    test_xlsx_capability()
    test_xlsx_table()
    test_xlsx_chart()
    test_xlsx_multi_sheet()
    test_e2e_comprehensive()

    print(f"\n{'=' * 60}")
    print(f"  结果:  PASS={_pass_count}  FAIL={_fail_count}")
    print(f"{'=' * 60}")

    return _fail_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
