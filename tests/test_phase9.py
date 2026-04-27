"""Phase 9 — 模板库 + 端到端测试 + 性能基准

测试范围：
  - 模板注册表功能（注册/查询/渲染/分类）
  - 12 个内置模板完整性
  - 模板 → DSL → IR → Renderer 全流程
  - 多格式端到端（PPTX/DOCX/XLSX/PDF/HTML）
  - 性能基准（100 页 PPTX <30s）
"""

import time
from pathlib import Path

import pytest

from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.templates import (
    get_template,
    list_categories,
    list_templates,
    render_template,
)
from office_suite.templates.registry import TemplateInfo, register_template

# ============================================================
# 1. 模板注册表基础功能
# ============================================================


def test_list_templates_count():
    """内置模板数量 >= 12"""
    templates = list_templates()
    assert len(templates) >= 12, f"Expected >= 12 templates, got {len(templates)}"


def test_list_categories():
    """分类包含 business / academic / creative"""
    cats = set(list_categories())
    assert {"business", "academic", "creative"}.issubset(cats)


def test_get_template_exists():
    """可以按名称获取模板"""
    tmpl = get_template("work_report")
    assert tmpl is not None
    assert tmpl.name == "work_report"
    assert tmpl.display_name == "工作汇报"


def test_get_template_not_exists():
    """不存在的模板返回 None"""
    assert get_template("nonexistent_template") is None


def test_list_templates_by_category():
    """按分类筛选模板"""
    biz = list_templates("business")
    assert all(t.category == "business" for t in biz)
    assert len(biz) >= 5


def test_render_template_default():
    """使用默认变量渲染模板"""
    dsl = render_template("work_report")
    assert "2026 Q1 工作汇报" in dsl
    assert "presentation" in dsl


def test_render_template_custom_vars():
    """自定义变量渲染"""
    dsl = render_template("work_report", {"title": "自定义标题"})
    assert "自定义标题" in dsl
    assert "2026 Q1 工作汇报" not in dsl


def test_render_template_not_exists():
    """渲染不存在的模板抛出 ValueError"""
    with pytest.raises(ValueError, match="不存在"):
        render_template("no_such_template")


def test_register_custom_template():
    """可以注册自定义模板"""
    info = TemplateInfo(
        name="_test_custom",
        display_name="测试模板",
        category="test",
        doc_type="presentation",
        description="测试用",
        content='version: "4.0"\ntype: presentation\nslides:\n  - layout: blank\n    elements: []',
    )
    register_template(info)
    assert get_template("_test_custom") is not None
    dsl = render_template("_test_custom")
    assert "presentation" in dsl


# ============================================================
# 2. 12 个内置模板完整性
# ============================================================

BUILTIN_TEMPLATES = [
    "work_report",
    "project_proposal",
    "annual_report",
    "product_launch",
    "weekly_meeting",
    "training_course",
    "business_plan",
    "resume",
    "academic_defense",
    "marketing_plan",
    "quarterly_review",
    "startup_pitch",
]


@pytest.mark.parametrize("name", BUILTIN_TEMPLATES)
def test_template_has_content(name):
    """每个内置模板都有非空 content"""
    tmpl = get_template(name)
    assert tmpl is not None
    assert len(tmpl.content) > 50, f"Template '{name}' content too short"


@pytest.mark.parametrize("name", BUILTIN_TEMPLATES)
def test_template_has_variables(name):
    """每个内置模板都定义了变量"""
    tmpl = get_template(name)
    assert len(tmpl.variables) >= 3, f"Template '{name}' has too few variables"


@pytest.mark.parametrize("name", BUILTIN_TEMPLATES)
def test_template_renders_to_valid_yaml(name):
    """模板渲染后是合法 YAML"""
    dsl = render_template(name)
    doc = parse_yaml_string(dsl)
    assert doc is not None
    assert doc.version == "4.0"


# ============================================================
# 3. 模板 → IR → Renderer 全流程
# ============================================================


@pytest.mark.parametrize("name", BUILTIN_TEMPLATES)
def test_template_to_pptx(name, tmp_path):
    """模板 → PPTX 渲染全流程"""
    from office_suite.renderer.pptx.deck import PPTXRenderer

    dsl = render_template(name)
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    out = PPTXRenderer().render(ir, tmp_path / f"{name}.pptx")
    assert out.exists()
    assert out.stat().st_size > 1000


# ============================================================
# 4. 多格式端到端
# ============================================================


def test_end_to_end_pptx(tmp_path):
    """端到端：PPTX"""
    from office_suite.renderer.pptx.deck import PPTXRenderer

    dsl = render_template("work_report")
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    out = PPTXRenderer().render(ir, tmp_path / "e2e.pptx")
    assert out.exists()
    assert out.stat().st_size > 5000


def test_end_to_end_docx(tmp_path):
    """端到端：DOCX"""
    from office_suite.renderer.docx.document import DOCXRenderer

    dsl = render_template("work_report")
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    out = DOCXRenderer().render(ir, tmp_path / "e2e.docx")
    assert out.exists()
    assert out.stat().st_size > 1000


def test_end_to_end_xlsx(tmp_path):
    """端到端：XLSX"""
    from office_suite.renderer.xlsx.workbook import XLSXRenderer

    dsl = render_template("quarterly_review")
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    out = XLSXRenderer().render(ir, tmp_path / "e2e.xlsx")
    assert out.exists()
    assert out.stat().st_size > 1000


def test_end_to_end_pdf(tmp_path):
    """端到端：PDF"""
    from office_suite.renderer.pdf.canvas import PDFRenderer

    dsl = render_template("work_report")
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    out = PDFRenderer().render(ir, tmp_path / "e2e.pdf")
    assert out.exists()
    assert out.stat().st_size > 1000


def test_end_to_end_html(tmp_path):
    """端到端：HTML"""
    from office_suite.renderer.html.dom import HTMLRenderer

    dsl = render_template("work_report")
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    out = HTMLRenderer().render(ir, tmp_path / "e2e.html")
    assert out.exists()
    assert out.stat().st_size > 1000


# ============================================================
# 5. 性能基准
# ============================================================


def test_perf_100_slide_pptx(tmp_path):
    """性能：100 页 PPTX < 30 秒"""
    from office_suite.renderer.pptx.deck import PPTXRenderer

    # 构造 100 页 DSL
    slide_yaml = """
  - layout: blank
    elements:
      - type: text
        content: "Page {{n}}"
        style: { font: { size: 24, weight: 700 } }
        position: { x: 20mm, y: 20mm, width: 200mm, height: 20mm }
      - type: text
        content: "Content for page {{n}}"
        style: { font: { size: 14 } }
        position: { x: 20mm, y: 50mm, width: 200mm, height: 100mm }
"""
    slides = ""
    for i in range(100):
        slides += slide_yaml.replace("{{n}}", str(i + 1))

    dsl = f'''version: "4.0"
type: presentation
styles:
  title: {{ font: {{ size: 24, weight: 700 }} }}
  body: {{ font: {{ size: 14 }} }}
slides:
{slides}'''

    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    start = time.perf_counter()
    out = PPTXRenderer().render(ir, tmp_path / "perf_100.pptx")
    elapsed = time.perf_counter() - start

    assert out.exists()
    assert elapsed < 30, f"100-slide PPTX took {elapsed:.1f}s (>30s limit)"
    print(f"\n  [PERF] 100-slide PPTX: {elapsed:.2f}s, {out.stat().st_size:,} bytes")


def test_perf_template_render_speed():
    """性能：模板渲染 + 解析 < 1s per template"""
    for name in BUILTIN_TEMPLATES:
        start = time.perf_counter()
        dsl = render_template(name)
        doc = parse_yaml_string(dsl)
        ir = compile_document(doc)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"Template '{name}' took {elapsed:.2f}s"
