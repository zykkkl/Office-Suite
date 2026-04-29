"""P0 增强功能测试

测试新增的 P0 功能：
  - DOCX：段落格式、列表、节管理、Word 样式
  - XLSX：scatter 图表、单元格合并、数字格式、条件格式、冻结窗格
  - Facade 模块导入
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.ir.types import IRDocument, IRNode, IRStyle, NodeType
from office_suite.renderer.docx.document import DOCXRenderer
from office_suite.renderer.xlsx.workbook import XLSXRenderer


# ============================================================
# 1. DOCX 段落格式
# ============================================================

def test_docx_paragraph_format():
    """DOCX 段落格式：对齐、间距、行距、缩进"""
    dsl = """
version: "4.0"
type: document
slides:
  - layout: blank
    elements:
      - type: text
        content: "居中对齐段落"
        extra:
          align: center
          space_before: 12
          space_after: 6
          line_spacing: 1.5
        position: { x: 20mm, y: 20mm, width: 200mm, height: 10mm }
      - type: text
        content: "首行缩进段落"
        extra:
          first_line_indent: 10
          left_indent: 5
        position: { x: 20mm, y: 40mm, width: 200mm, height: 10mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_docx_para_format.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()
    assert out_path.stat().st_size > 3000


def test_docx_list_bullet():
    """DOCX 无序列表渲染"""
    dsl = """
version: "4.0"
type: document
slides:
  - layout: blank
    elements:
      - type: text
        content: "项目要点"
        style: { font: { size: 24, weight: 700 } }
        position: { x: 20mm, y: 20mm, width: 200mm, height: 10mm }
      - type: text
        content: "第一项"
        extra: { list_type: bullet }
        position: { x: 20mm, y: 35mm, width: 200mm, height: 8mm }
      - type: text
        content: "第二项"
        extra: { list_type: bullet }
        position: { x: 20mm, y: 45mm, width: 200mm, height: 8mm }
      - type: text
        content: "第三项"
        extra: { list_type: bullet }
        position: { x: 20mm, y: 55mm, width: 200mm, height: 8mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_docx_list_bullet.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


def test_docx_list_numbered():
    """DOCX 有序列表渲染"""
    dsl = """
version: "4.0"
type: document
slides:
  - layout: blank
    elements:
      - type: text
        content: "步骤一"
        extra: { list_type: numbered }
        position: { x: 20mm, y: 20mm, width: 200mm, height: 8mm }
      - type: text
        content: "步骤二"
        extra: { list_type: numbered }
        position: { x: 20mm, y: 30mm, width: 200mm, height: 8mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_docx_list_numbered.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


def test_docx_heading_level():
    """DOCX 标题级别（extra.heading_level）"""
    dsl = """
version: "4.0"
type: document
slides:
  - layout: blank
    elements:
      - type: text
        content: "一级标题"
        extra: { heading_level: 1 }
        position: { x: 20mm, y: 20mm, width: 200mm, height: 15mm }
      - type: text
        content: "二级标题"
        extra: { heading_level: 2 }
        position: { x: 20mm, y: 40mm, width: 200mm, height: 10mm }
      - type: text
        content: "三级标题"
        extra: { heading_level: 3 }
        position: { x: 20mm, y: 55mm, width: 200mm, height: 10mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_docx_heading.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


def test_docx_section_break():
    """DOCX 节分隔符"""
    dsl = """
version: "4.0"
type: document
slides:
  - layout: blank
    extra:
      section_break: new_page
      page_size: a4
      orientation: portrait
    elements:
      - type: text
        content: "第一节"
        position: { x: 20mm, y: 20mm, width: 200mm, height: 10mm }
  - layout: blank
    extra:
      section_break: continuous
    elements:
      - type: text
        content: "第二节（连续）"
        position: { x: 20mm, y: 20mm, width: 200mm, height: 10mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_docx_section.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


def test_docx_page_break_between_slides():
    """DOCX 多幻灯片自动分页"""
    dsl = """
version: "4.0"
type: document
slides:
  - layout: blank
    elements:
      - type: text
        content: "第一页"
        position: { x: 20mm, y: 20mm, width: 200mm, height: 10mm }
  - layout: blank
    elements:
      - type: text
        content: "第二页"
        position: { x: 20mm, y: 20mm, width: 200mm, height: 10mm }
  - layout: blank
    elements:
      - type: text
        content: "第三页"
        position: { x: 20mm, y: 20mm, width: 200mm, height: 10mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_docx_pagebreak.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()
    # 3 slides = 2 page breaks, file should be larger
    assert out_path.stat().st_size > 4000


def test_docx_table_style():
    """DOCX 表格自定义样式"""
    dsl = """
version: "4.0"
type: document
slides:
  - layout: blank
    elements:
      - type: table
        rows: 3
        cols: 3
        data:
          - ["A", "B", "C"]
          - [1, 2, 3]
          - [4, 5, 6]
        extra:
          table_style: "Light Shading Accent 1"
        position: { x: 20mm, y: 20mm, width: 200mm, height: 50mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_docx_table_style.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


# ============================================================
# 2. XLSX 增强
# ============================================================

def test_xlsx_scatter_chart():
    """XLSX 散点图"""
    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    elements:
      - type: chart
        chart_type: scatter
        extra:
          title: "相关性分析"
          categories: [1, 2, 3, 4, 5]
          series:
            - name: "X值"
              values: [10, 20, 30, 40, 50]
            - name: "Y值"
              values: [15, 25, 35, 45, 55]
        position: { x: 0mm, y: 0mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_xlsx_scatter.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()
    assert out_path.stat().st_size > 3000


def test_xlsx_number_format():
    """XLSX 数字格式"""
    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    elements:
      - type: text
        content: "收入"
        position: { x: 0mm, y: 0mm }
      - type: text
        content: "1234567"
        extra:
          number_format: currency
          column: 2
        position: { x: 0mm, y: 0mm }
      - type: text
        content: "0.85"
        extra:
          number_format: percent
          column: 3
        position: { x: 0mm, y: 0mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_xlsx_numfmt.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


def test_xlsx_freeze_panes():
    """XLSX 冻结窗格"""
    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    extra:
      title: "冻结测试"
      freeze_row: 2
      freeze_col: 1
    elements:
      - type: table
        rows: 10
        cols: 5
        data:
          - ["ID", "名称", "金额", "日期", "状态"]
          - [1, "A", 100, "2024-01-01", "完成"]
          - [2, "B", 200, "2024-01-02", "进行中"]
          - [3, "C", 300, "2024-01-03", "计划"]
        position: { x: 0mm, y: 0mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_xlsx_freeze.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


def test_xlsx_merge_cells():
    """XLSX 单元格合并"""
    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    elements:
      - type: table
        rows: 4
        cols: 3
        data:
          - ["标题", "", ""]
          - ["A", "B", "C"]
          - [1, 2, 3]
          - [4, 5, 6]
        extra:
          merge_cells: ["A1:C1"]
        position: { x: 0mm, y: 0mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_xlsx_merge.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


def test_xlsx_conditional_format_data_bar():
    """XLSX 条件格式 — 数据条"""
    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    elements:
      - type: table
        rows: 6
        cols: 2
        data:
          - ["项目", "得分"]
          - ["A", 85]
          - ["B", 92]
          - ["C", 78]
          - ["D", 95]
          - ["E", 60]
        extra:
          conditional_format: data_bar
        position: { x: 0mm, y: 0mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_xlsx_cond_bar.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


def test_xlsx_conditional_format_color_scale():
    """XLSX 条件格式 — 色阶"""
    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    elements:
      - type: table
        rows: 6
        cols: 2
        data:
          - ["项目", "得分"]
          - ["A", 85]
          - ["B", 92]
          - ["C", 78]
          - ["D", 95]
          - ["E", 60]
        extra:
          conditional_format: color_scale
        position: { x: 0mm, y: 0mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_xlsx_cond_color.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


def test_xlsx_cell_style_fill_and_border():
    """XLSX 单元格样式：填充色 + 边框"""
    dsl = """
version: "4.0"
type: spreadsheet
styles:
  highlight:
    fill: { color: "#FEF3C7" }
    border: { color: "#D97706", width: 2 }
    font: { weight: 700, color: "#92400E" }
slides:
  - layout: blank
    elements:
      - type: text
        content: "重要提示"
        style: highlight
        position: { x: 0mm, y: 0mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_xlsx_style.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


def test_xlsx_chart_data_labels():
    """XLSX 图表数据标签"""
    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    elements:
      - type: chart
        chart_type: pie
        extra:
          title: "市场份额"
          categories: ["产品A", "产品B", "产品C"]
          series:
            - name: "份额"
              values: [45, 30, 25]
          show_data_labels: true
          show_legend: false
        position: { x: 0mm, y: 0mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_xlsx_chart_labels.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()


# ============================================================
# 3. Facade 模块导入验证
# ============================================================

def test_facade_engine_style_cascade():
    """engine/style/cascade.py facade 可导入"""
    from office_suite.engine.style.cascade import cascade_style, cascade_style_by_name, DEFAULT_THEME_STYLES
    assert callable(cascade_style)
    assert callable(cascade_style_by_name)
    assert "default" in DEFAULT_THEME_STYLES


def test_facade_renderer_pptx_modules():
    """PPTX 渲染器子模块可导入"""
    from office_suite.renderer.pptx.slide import render_slide
    from office_suite.renderer.pptx.shape import get_shape_type, SHAPE_TYPE_MAP
    from office_suite.renderer.pptx.transition import apply_transition, TRANSITION_MAP
    from office_suite.renderer.pptx.master import list_master_layouts, get_layout_by_name
    assert callable(render_slide)
    assert callable(get_shape_type)
    assert len(SHAPE_TYPE_MAP) >= 10
    assert callable(apply_transition)
    assert callable(list_master_layouts)


def test_facade_renderer_docx_modules():
    """DOCX 渲染器子模块可导入"""
    from office_suite.renderer.docx.section import render_section
    from office_suite.renderer.docx.block import render_text, render_list_item
    from office_suite.renderer.docx.style import apply_paragraph_style
    assert callable(render_section)
    assert callable(render_text)
    assert callable(render_list_item)


def test_facade_renderer_xlsx_modules():
    """XLSX 渲染器子模块可导入"""
    from office_suite.renderer.xlsx.sheet import render_to_sheet
    from office_suite.renderer.xlsx.chart import render_chart, CHART_CLASS_MAP
    assert callable(render_to_sheet)
    assert callable(render_chart)
    assert "scatter" in CHART_CLASS_MAP


def test_facade_renderer_pdf_font():
    """PDF 字体模块可导入"""
    from office_suite.renderer.pdf.font import resolve_font, FONT_MAP, BUILTIN_FONTS
    assert callable(resolve_font)
    assert resolve_font("Microsoft YaHei UI") == "STSong-Light"
    assert resolve_font("Arial") == "Helvetica"
    assert resolve_font("Arial", bold=True) == "Helvetica-Bold"


def test_facade_renderer_html_css():
    """HTML CSS 模块可导入"""
    from office_suite.renderer.html.css import position_css, text_style_css, shadow_css, background_css
    assert callable(position_css)
    assert callable(text_style_css)
    assert callable(shadow_css)


# ============================================================
# 4. 综合端到端
# ============================================================

def test_e2e_docx_enhanced():
    """DOCX 增强功能综合测试"""
    dsl = """
version: "4.0"
type: document
styles:
  title: { font: { size: 28, weight: 700, color: "#0F172A" } }
  body: { font: { size: 12, color: "#475569" } }
slides:
  - layout: blank
    extra:
      section_break: new_page
      page_size: a4
    elements:
      - type: text
        content: "增强功能演示"
        style: title
        extra: { heading_level: 1 }
        position: { x: 20mm, y: 20mm, width: 200mm, height: 15mm }
      - type: text
        content: "这是居中对齐的段落，段前 12pt，段后 6pt。"
        style: body
        extra:
          align: center
          space_before: 12
          space_after: 6
          line_spacing: 1.5
        position: { x: 20mm, y: 40mm, width: 200mm, height: 10mm }
      - type: text
        content: "要点一"
        extra: { list_type: bullet }
        position: { x: 20mm, y: 55mm, width: 200mm, height: 8mm }
      - type: text
        content: "要点二"
        extra: { list_type: bullet }
        position: { x: 20mm, y: 65mm, width: 200mm, height: 8mm }
      - type: table
        rows: 3
        cols: 2
        data: [["项目", "状态"],["Alpha", "完成"],["Beta", "进行中"]]
        extra: { table_style: "Light Shading Accent 1" }
        position: { x: 20mm, y: 80mm, width: 200mm, height: 40mm }
  - layout: blank
    elements:
      - type: text
        content: "第二页内容"
        style: body
        position: { x: 20mm, y: 20mm, width: 200mm, height: 10mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_e2e_docx.docx"
    renderer = DOCXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()
    assert out_path.stat().st_size > 5000


def test_e2e_xlsx_enhanced():
    """XLSX 增强功能综合测试"""
    dsl = """
version: "4.0"
type: spreadsheet
slides:
  - layout: blank
    extra:
      title: "综合报表"
      freeze_row: 2
    elements:
      - type: table
        rows: 6
        cols: 4
        data:
          - ["产品", "Q1", "Q2", "Q3"]
          - ["产品A", 1200, 1500, 1800]
          - ["产品B", 800, 950, 1100]
          - ["产品C", 600, 700, 850]
          - ["产品D", 400, 500, 650]
          - ["合计", 3000, 3650, 4400]
        extra:
          number_format: currency
          conditional_format: data_bar
        position: { x: 0mm, y: 0mm }
      - type: chart
        chart_type: column
        extra:
          title: "季度对比"
          categories: ["产品A", "产品B", "产品C", "产品D"]
          series:
            - name: "Q1"
              values: [1200, 800, 600, 400]
            - name: "Q2"
              values: [1500, 950, 700, 500]
            - name: "Q3"
              values: [1800, 1100, 850, 650]
          show_data_labels: true
        position: { x: 0mm, y: 60mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "p0_e2e_xlsx.xlsx"
    renderer = XLSXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists()
    assert out_path.stat().st_size > 5000


# ============================================================
# 主函数
# ============================================================

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
