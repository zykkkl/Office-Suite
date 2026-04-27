"""Office Suite 4.0 — 全格式端到端演示

生成 5 个文件，展示完整编译管线:
  demo_output.pptx  — 科技风格季度汇报 PPT
  demo_output.docx  — 项目文档
  demo_output.xlsx  — 数据报表
  demo_output.pdf   — PDF 版本
  demo_output.html  — HTML 预览版
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.renderer.pptx.deck import PPTXRenderer
from office_suite.renderer.docx.document import DOCXRenderer
from office_suite.renderer.xlsx.workbook import XLSXRenderer
from office_suite.renderer.pdf.canvas import PDFRenderer
from office_suite.renderer.html.dom import HTMLRenderer
from office_suite.themes import get_theme
from office_suite.components import generate_component
from office_suite.ai import parse_intent, suggest_design

OUTPUT_DIR = PROJECT_ROOT / "demo_output"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    theme = get_theme("fluent")
    cs = theme.colors

    print("=" * 60)
    print("  Office Suite 4.0 — 全格式演示")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. PPTX — 科技风格季度汇报
    # --------------------------------------------------------
    print("\n[1/5] 生成 PPTX...")
    pptx_dsl = f"""
version: "4.0"
type: presentation
styles:
  title:
    font: {{ size: 36, weight: 700, color: "#FFFFFF" }}
    fill: {{ color: "{cs.primary}" }}
  subtitle:
    font: {{ size: 16, color: "{cs.text_secondary}" }}
  heading:
    font: {{ size: 28, weight: 700, color: "{cs.text_primary}" }}
  body:
    font: {{ size: 14, color: "{cs.text_secondary}" }}
  accent:
    font: {{ size: 48, weight: 700, color: "{cs.primary}" }}
slides:
  - layout: blank
    elements:
      - type: shape
        shape_type: rounded_rectangle
        style:
          fill: {{ color: "{cs.primary}" }}
        position: {{ x: 0mm, y: 0mm, width: 254mm, height: 190mm }}
      - type: text
        content: "2026 Q1 季度汇报"
        style: title
        position: {{ x: 30mm, y: 50mm, width: 194mm, height: 20mm }}
        animation: {{ effect: fade_in, duration: 0.8 }}
      - type: text
        content: "Office Suite 4.0 全媒体融合文档引擎"
        style: subtitle
        position: {{ x: 30mm, y: 75mm, width: 194mm, height: 12mm }}
        animation: {{ effect: slide_up, duration: 0.6, trigger: after_previous }}

  - layout: blank
    elements:
      - type: text
        content: "关键指标"
        style: heading
        position: {{ x: 20mm, y: 10mm, width: 214mm, height: 12mm }}
      - type: text
        content: "¥2.4M"
        style: accent
        position: {{ x: 20mm, y: 35mm, width: 70mm, height: 20mm }}
        animation: {{ effect: zoom_in, duration: 0.5 }}
      - type: text
        content: "季度营收"
        style: body
        position: {{ x: 20mm, y: 55mm, width: 70mm, height: 8mm }}
      - type: text
        content: "+28%"
        style: {{ font: {{ size: 48, weight: 700, color: "#10B981" }} }}
        position: {{ x: 95mm, y: 35mm, width: 70mm, height: 20mm }}
        animation: {{ effect: zoom_in, duration: 0.5, delay: 0.3 }}
      - type: text
        content: "同比增长"
        style: body
        position: {{ x: 95mm, y: 55mm, width: 70mm, height: 8mm }}
      - type: text
        content: "95%"
        style: {{ font: {{ size: 48, weight: 700, color: "{cs.primary}" }} }}
        position: {{ x: 170mm, y: 35mm, width: 60mm, height: 20mm }}
        animation: {{ effect: zoom_in, duration: 0.5, delay: 0.6 }}
      - type: text
        content: "客户满意度"
        style: body
        position: {{ x: 170mm, y: 55mm, width: 60mm, height: 8mm }}

  - layout: blank
    elements:
      - type: text
        content: "月度营收趋势"
        style: heading
        position: {{ x: 20mm, y: 10mm, width: 214mm, height: 12mm }}
      - type: chart
        chart_type: line
        position: {{ x: 20mm, y: 30mm, width: 214mm, height: 130mm }}
        extra:
          title: "月度营收"
          categories: ["1月", "2月", "3月", "4月", "5月", "6月"]
          series:
            - name: "营收"
              values: [320, 380, 420, 510, 580, 650]
            - name: "成本"
              values: [200, 210, 220, 240, 250, 260]

  - layout: blank
    elements:
      - type: text
        content: "项目进度"
        style: heading
        position: {{ x: 20mm, y: 10mm, width: 214mm, height: 12mm }}
      - type: table
        rows: 6
        cols: 4
        data:
          - ["项目", "负责人", "状态", "进度"]
          - ["AI 意图解析", "张三", "完成", "100%"]
          - ["主题系统", "李四", "完成", "100%"]
          - ["PDF 渲染器", "王五", "进行中", "80%"]
          - ["动画引擎", "赵六", "计划", "30%"]
          - ["模板库", "钱七", "计划", "0%"]
        position: {{ x: 20mm, y: 30mm, width: 214mm, height: 80mm }}
"""
    doc = parse_yaml_string(pptx_dsl)
    ir = compile_document(doc)
    pptx_out = PPTXRenderer().render(ir, OUTPUT_DIR / "demo_output.pptx")
    print(f"  -> {pptx_out} ({pptx_out.stat().st_size:,} bytes)")

    # --------------------------------------------------------
    # 2. DOCX — 项目文档
    # --------------------------------------------------------
    print("\n[2/5] 生成 DOCX...")
    docx_dsl = """
version: "4.0"
type: document
styles:
  title: { font: { size: 32, weight: 700, color: "#0F172A" } }
  heading: { font: { size: 22, weight: 700, color: "#1E40AF" } }
  body: { font: { size: 14, color: "#334155" } }
slides:
  - layout: blank
    elements:
      - type: text
        content: "Office Suite 4.0 技术方案"
        style: title
        position: { x: 20mm, y: 20mm, width: 170mm, height: 15mm }
      - type: text
        content: "一、项目概述"
        style: heading
        position: { x: 20mm, y: 40mm, width: 170mm, height: 10mm }
      - type: text
        content: "Office Suite 4.0 是一个全媒体融合文档引擎，采用 LLVM 式编译架构：YAML DSL → IR 中间表示 → 多格式渲染器。支持 PPTX、DOCX、XLSX、PDF、HTML 五种输出格式。"
        style: body
        position: { x: 20mm, y: 55mm, width: 170mm, height: 20mm }
      - type: text
        content: "二、架构设计"
        style: heading
        position: { x: 20mm, y: 80mm, width: 170mm, height: 10mm }
      - type: text
        content: "核心管线：DSL Parser → IR Compiler → IR Validator → Renderer。样式级联遵循 theme → document → slide → element → inline 的优先级递增规则。每个渲染器通过 RendererCapability 声明支持的特性，不支持的特性自动降级。"
        style: body
        position: { x: 20mm, y: 95mm, width: 170mm, height: 25mm }
      - type: text
        content: "三、测试覆盖"
        style: heading
        position: { x: 20mm, y: 125mm, width: 170mm, height: 10mm }
      - type: table
        rows: 5
        cols: 3
        data:
          - ["阶段", "测试数", "状态"]
          - ["Phase 1-2", "125", "全绿"]
          - ["Phase 3-4", "74", "全绿"]
          - ["Phase 5-6", "99", "全绿"]
          - ["Phase 7-8", "88", "全绿"]
        position: { x: 20mm, y: 140mm, width: 170mm, height: 40mm }
"""
    doc = parse_yaml_string(docx_dsl)
    ir = compile_document(doc)
    docx_out = DOCXRenderer().render(ir, OUTPUT_DIR / "demo_output.docx")
    print(f"  -> {docx_out} ({docx_out.stat().st_size:,} bytes)")

    # --------------------------------------------------------
    # 3. XLSX — 数据报表
    # --------------------------------------------------------
    print("\n[3/5] 生成 XLSX...")
    xlsx_dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    extra: { title: "营收数据" }
    elements:
      - type: table
        rows: 7
        cols: 5
        data:
          - ["月份", "营收(万)", "成本(万)", "利润(万)", "利润率"]
          - ["1月", 320, 200, 120, "37.5%"]
          - ["2月", 380, 210, 170, "44.7%"]
          - ["3月", 420, 220, 200, "47.6%"]
          - ["4月", 510, 240, 270, "52.9%"]
          - ["5月", 580, 250, 330, "56.9%"]
          - ["6月", 650, 260, 390, "60.0%"]
        position: { x: 0mm, y: 0mm }
      - type: chart
        chart_type: column
        position: { x: 0mm, y: 80mm }
        extra:
          title: "月度营收 vs 成本"
          categories: ["1月", "2月", "3月", "4月", "5月", "6月"]
          series:
            - name: "营收"
              values: [320, 380, 420, 510, 580, 650]
            - name: "成本"
              values: [200, 210, 220, 240, 250, 260]
  - layout: blank
    extra: { title: "项目统计" }
    elements:
      - type: table
        rows: 5
        cols: 3
        data:
          - ["指标", "数值", "备注"]
          - ["总代码行数", "9000+", "Python"]
          - ["测试用例", "390", "全绿"]
          - ["输出格式", "5", "PPTX/DOCX/XLSX/PDF/HTML"]
          - ["内置组件", "5", "图表/统计/时间线/对比/信息图"]
        position: { x: 0mm, y: 0mm }
"""
    doc = parse_yaml_string(xlsx_dsl)
    ir = compile_document(doc)
    xlsx_out = XLSXRenderer().render(ir, OUTPUT_DIR / "demo_output.xlsx")
    print(f"  -> {xlsx_out} ({xlsx_out.stat().st_size:,} bytes)")

    # --------------------------------------------------------
    # 4. PDF — 矢量文档
    # --------------------------------------------------------
    print("\n[4/5] 生成 PDF...")
    pdf_dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "#0078D4" } }
        position: { x: 0mm, y: 0mm, width: 254mm, height: 50mm }
      - type: text
        content: "Office Suite 4.0"
        style: { font: { size: 32, weight: 700, color: "#FFFFFF" } }
        position: { x: 20mm, y: 15mm, width: 200mm, height: 20mm }
      - type: text
        content: "All-media Fusion Document Engine"
        style: { font: { size: 14, color: "#B0B0B0" } }
        position: { x: 20mm, y: 35mm, width: 200mm, height: 10mm }
      - type: text
        content: "Architecture"
        style: { font: { size: 22, weight: 700, color: "#0F172A" } }
        position: { x: 20mm, y: 60mm, width: 200mm, height: 12mm }
      - type: text
        content: "YAML DSL -> IR -> Renderer -> .pptx / .docx / .xlsx / .pdf / .html"
        style: { font: { size: 14, color: "#475569" } }
        position: { x: 20mm, y: 78mm, width: 200mm, height: 10mm }
      - type: table
        rows: 5
        cols: 3
        data:
          - ["Module", "Tests", "Status"]
          - ["DSL + IR", "65", "PASS"]
          - ["Renderers", "171", "PASS"]
          - ["AI + Theme", "99", "PASS"]
          - ["Animation", "58", "PASS"]
        position: { x: 20mm, y: 95mm, width: 200mm, height: 50mm }
"""
    doc = parse_yaml_string(pdf_dsl)
    ir = compile_document(doc)
    pdf_out = PDFRenderer().render(ir, OUTPUT_DIR / "demo_output.pdf")
    print(f"  -> {pdf_out} ({pdf_out.stat().st_size:,} bytes)")

    # --------------------------------------------------------
    # 5. HTML — 预览版
    # --------------------------------------------------------
    print("\n[5/5] 生成 HTML...")
    html_dsl = """
version: "4.0"
type: presentation
styles:
  title: { font: { size: 32, weight: 700, color: "#0F172A" } }
  body: { font: { size: 14, color: "#475569" } }
slides:
  - layout: blank
    elements:
      - type: shape
        shape_type: rounded_rectangle
        style: { fill: { color: "#EFF6FF" } }
        position: { x: 20mm, y: 15mm, width: 214mm, height: 40mm }
      - type: text
        content: "Office Suite 4.0 Demo"
        style: { font: { size: 28, weight: 700, color: "#1E40AF" } }
        position: { x: 30mm, y: 22mm, width: 194mm, height: 12mm }
      - type: text
        content: "HTML Preview — 5 format output engine"
        style: body
        position: { x: 30mm, y: 38mm, width: 194mm, height: 8mm }
      - type: text
        content: "Features"
        style: title
        position: { x: 20mm, y: 65mm, width: 214mm, height: 12mm }
      - type: table
        rows: 5
        cols: 2
        data:
          - ["Feature", "Status"]
          - ["DSL Parser", "Done"]
          - ["IR Compiler", "Done"]
          - ["5 Renderers", "Done"]
          - ["AI + Theme", "Done"]
        position: { x: 20mm, y: 82mm, width: 214mm, height: 50mm }
      - type: chart
        chart_type: bar
        extra:
          title: "Test Coverage"
          categories: ["Phase 1", "Phase 2", "Phase 3-4", "Phase 5-6", "Phase 7-8"]
          series:
            - name: "Tests"
              values: [65, 60, 74, 99, 88]
        position: { x: 20mm, y: 140mm, width: 214mm, height: 45mm }
"""
    doc = parse_yaml_string(html_dsl)
    ir = compile_document(doc)
    html_out = HTMLRenderer().render(ir, OUTPUT_DIR / "demo_output.html")
    print(f"  -> {html_out} ({html_out.stat().st_size:,} bytes)")

    # --------------------------------------------------------
    # 汇总
    # --------------------------------------------------------
    print(f"\n{'=' * 60}")
    print("  生成完成!")
    print(f"  输出目录: {OUTPUT_DIR}")
    print(f"{'=' * 60}")

    for f in sorted(OUTPUT_DIR.glob("demo_output.*")):
        size = f.stat().st_size
        print(f"  {f.name:25s} {size:>10,} bytes")

    print()


if __name__ == "__main__":
    main()
