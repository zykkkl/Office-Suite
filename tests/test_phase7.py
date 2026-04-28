"""Phase 7 测试套件：PDF + HTML 渲染器

验收标准：
1. PDF：矢量文字 + 精确布局 + 表格
2. HTML：CSS 渲染 + 完整页面
3. 各渲染器 capability 声明 + 降级路径
4. 端到端: DSL → PDF / HTML
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.ir.validator import validate_ir_v2
from office_suite.ir.types import IRDocument, IRNode, NodeType
from office_suite.renderer.pdf.canvas import PDFRenderer
from office_suite.renderer.html.dom import HTMLRenderer


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
# 测试 1-6: PDF 渲染器能力声明
# ============================================================

def test_pdf_capability():
    section("1. PDF 渲染器能力声明")

    renderer = PDFRenderer()
    cap = renderer.capability

    check("支持 TEXT", NodeType.TEXT in cap.supported_node_types)
    check("支持 TABLE", NodeType.TABLE in cap.supported_node_types)
    check("支持 SHAPE", NodeType.SHAPE in cap.supported_node_types)
    check("支持 IMAGE", NodeType.IMAGE in cap.supported_node_types)
    check("支持 CHART", NodeType.CHART in cap.supported_node_types)
    check("不支持动画", len(cap.supported_animations) == 0)
    check("不支持艺术字", len(cap.supported_text_transforms) == 0)
    check("有降级映射", len(cap.fallback_map) > 0)


# ============================================================
# 测试 7-11: PDF 渲染 — 文本
# ============================================================

def test_pdf_text():
    section("2. PDF 文本渲染")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: text
        content: "PDF 标题测试"
        style: { font: { size: 32, weight: 700, color: "#1E3A5F" } }
        position: { x: 20mm, y: 20mm, width: 200mm, height: 15mm }
      - type: text
        content: "这是正文内容，用于测试 PDF 渲染效果。"
        style: { font: { size: 14, color: "#475569" } }
        position: { x: 20mm, y: 40mm, width: 200mm, height: 10mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    result = validate_ir_v2(ir)
    check("IR 校验通过", result.is_valid)

    output = PROJECT_ROOT / "tests" / "output" / "phase7_text.pdf"
    renderer = PDFRenderer()
    out_path = renderer.render(ir, output)
    check("PDF 文件生成", out_path.exists())
    check("PDF > 1KB", out_path.stat().st_size > 1000, f"{out_path.stat().st_size} bytes")


# ============================================================
# 测试 12-14: PDF 渲染 — 表格
# ============================================================

def test_pdf_table():
    section("3. PDF 表格渲染")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: text
        content: "数据报表"
        style: { font: { size: 24, weight: 700 } }
        position: { x: 20mm, y: 10mm, width: 200mm, height: 12mm }
      - type: table
        rows: 4
        cols: 3
        data:
          - ["项目", "状态", "进度"]
          - ["Alpha", "进行中", "80%"]
          - ["Beta", "完成", "100%"]
          - ["Gamma", "计划", "20%"]
        position: { x: 20mm, y: 30mm, width: 200mm, height: 60mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase7_table.pdf"
    renderer = PDFRenderer()
    out_path = renderer.render(ir, output)
    check("PDF 表格生成", out_path.exists())
    check("PDF 表格 > 1KB", out_path.stat().st_size > 1000, f"{out_path.stat().st_size} bytes")


# ============================================================
# 测试 15-17: PDF 渲染 — 形状
# ============================================================

def test_pdf_shape():
    section("4. PDF 形状渲染")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: shape
        shape_type: rounded_rectangle
        content: "卡片"
        style: { fill: { color: "#EFF6FF" }, font: { size: 14, color: "#2563EB" } }
        position: { x: 20mm, y: 20mm, width: 80mm, height: 30mm }
      - type: shape
        shape_type: circle
        style: { fill: { color: "#16A34A" } }
        position: { x: 120mm, y: 20mm, width: 40mm, height: 40mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase7_shape.pdf"
    renderer = PDFRenderer()
    out_path = renderer.render(ir, output)
    check("PDF 形状生成", out_path.exists())


# ============================================================
# 测试 18-20: PDF 渲染 — 图表
# ============================================================

def test_pdf_chart():
    section("5. PDF 图表渲染")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: chart
        chart_type: line
        extra:
          title: "月度趋势"
          categories: ["1月", "2月", "3月", "4月"]
          series:
            - name: "营收"
              values: [100, 120, 150, 180]
            - name: "成本"
              values: [60, 70, 85, 95]
        position: { x: 20mm, y: 20mm, width: 200mm, height: 95mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase7_chart.pdf"
    renderer = PDFRenderer()
    out_path = renderer.render(ir, output)
    check("PDF 图表生成", out_path.exists())
    check("PDF 图表 > 1KB", out_path.stat().st_size > 1000, f"{out_path.stat().st_size} bytes")


# ============================================================
# 测试 21-25: HTML 渲染器能力声明
# ============================================================

def test_html_capability():
    section("5. HTML 渲染器能力声明")

    renderer = HTMLRenderer()
    cap = renderer.capability

    check("支持 TEXT", NodeType.TEXT in cap.supported_node_types)
    check("支持 TABLE", NodeType.TABLE in cap.supported_node_types)
    check("支持 IMAGE", NodeType.IMAGE in cap.supported_node_types)
    check("支持 CHART", NodeType.CHART in cap.supported_node_types)
    check("支持 SHAPE", NodeType.SHAPE in cap.supported_node_types)


# ============================================================
# 测试 26-30: HTML 渲染 — 文本
# ============================================================

def test_html_text():
    section("6. HTML 文本渲染")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: text
        content: "HTML 标题"
        style: { font: { size: 32, weight: 700, color: "#0F172A" } }
        position: { x: 20mm, y: 20mm, width: 200mm, height: 15mm }
      - type: text
        content: "正文段落内容。"
        style: { font: { size: 14, color: "#475569" } }
        position: { x: 20mm, y: 40mm, width: 200mm, height: 10mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase7_text.html"
    renderer = HTMLRenderer()
    out_path = renderer.render(ir, output)
    check("HTML 文件生成", out_path.exists())
    check("HTML > 500B", out_path.stat().st_size > 500, f"{out_path.stat().st_size} bytes")

    # 检查内容
    content = out_path.read_text(encoding="utf-8")
    check("HTML 含 DOCTYPE", "<!DOCTYPE html>" in content)
    check("HTML 含标题", "HTML 标题" in content)
    check("HTML 含正文", "正文段落内容" in content)


# ============================================================
# 测试 31-33: HTML 渲染 — 表格
# ============================================================

def test_html_table():
    section("7. HTML 表格渲染")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: table
        rows: 3
        cols: 3
        data:
          - ["A", "B", "C"]
          - ["1", "2", "3"]
          - ["4", "5", "6"]
        position: { x: 20mm, y: 20mm, width: 200mm, height: 40mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase7_table.html"
    renderer = HTMLRenderer()
    out_path = renderer.render(ir, output)
    check("HTML 表格生成", out_path.exists())

    content = out_path.read_text(encoding="utf-8")
    check("HTML 含 <table>", "<table" in content)
    check("HTML 含 <th>", "<th" in content)


# ============================================================
# 测试 34-36: HTML 渲染 — 图表
# ============================================================

def test_html_chart():
    section("8. HTML 图表渲染")

    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: chart
        chart_type: bar
        extra:
          title: "月度对比"
          categories: ["1月", "2月", "3月"]
          series:
            - name: "营收"
              values: [100, 120, 150]
        position: { x: 20mm, y: 20mm, width: 200mm, height: 100mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase7_chart.html"
    renderer = HTMLRenderer()
    out_path = renderer.render(ir, output)
    check("HTML 图表生成", out_path.exists())

    content = out_path.read_text(encoding="utf-8")
    check("HTML 含 SVG 图表", "<svg" in content)
    check("HTML 含柱形", "<rect" in content)
    check("HTML 不含图表占位", "[Chart" not in content)


# ============================================================
# 测试 37-39: 端到端 DSL → PDF + HTML
# ============================================================

def test_e2e():
    section("9. 端到端 DSL → PDF + HTML")

    dsl = """
version: "4.0"
type: presentation
styles:
  title: { font: { size: 28, weight: 700, color: "#0F172A" } }
  body: { font: { size: 14, color: "#475569" } }
slides:
  - layout: blank
    elements:
      - type: text
        content: "Office Suite 4.0 阶段报告"
        style: title
        position: { x: 20mm, y: 20mm, width: 200mm, height: 15mm }
      - type: text
        content: "由 Office Suite 4.0 引擎自动生成。"
        style: body
        position: { x: 20mm, y: 40mm, width: 200mm, height: 10mm }
      - type: table
        rows: 4
        cols: 3
        data:
          - ["阶段", "状态", "测试数"]
          - ["Phase 0", "完成", 4]
          - ["Phase 1", "完成", 65]
          - ["Phase 2", "完成", 60]
        position: { x: 20mm, y: 60mm, width: 200mm, height: 50mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    # PDF
    pdf_out = PROJECT_ROOT / "tests" / "output" / "phase7_e2e.pdf"
    pdf_renderer = PDFRenderer()
    pdf_path = pdf_renderer.render(ir, pdf_out)
    check("PDF 综合生成", pdf_path.exists())

    # HTML
    html_out = PROJECT_ROOT / "tests" / "output" / "phase7_e2e.html"
    html_renderer = HTMLRenderer()
    html_path = html_renderer.render(ir, html_out)
    check("HTML 综合生成", html_path.exists())
    check("HTML > 1KB", html_path.stat().st_size > 1000, f"{html_path.stat().st_size} bytes")


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("  Office Suite 4.0 — Phase 7 测试套件")
    print("=" * 60)

    test_pdf_capability()
    test_pdf_text()
    test_pdf_table()
    test_pdf_shape()
    test_pdf_chart()
    test_html_capability()
    test_html_text()
    test_html_table()
    test_html_chart()
    test_e2e()

    print(f"\n{'=' * 60}")
    print(f"  结果:  PASS={_pass_count}  FAIL={_fail_count}")
    print(f"{'=' * 60}")

    return _fail_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
