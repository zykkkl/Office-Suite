"""Phase 5 测试套件：AI 意图解析 + 设计建议 + 质量评审

验收标准：
1. 自然语言 → DesignBrief 解析正确
2. 设计建议引擎输出配色/布局/排版
3. 质量评审检出对比度/层次/一致性问题
4. 端到端: 自然语言 → 建议 → DSL 编译 → 渲染
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.ai.intent import DesignBrief, parse_intent
from office_suite.ai.suggest import (
    ColorScheme, DesignSuggestion, suggest_color_scheme,
    suggest_design, suggest_layout,
)
from office_suite.ai.critique import (
    CritiqueReport, CritiqueSeverity, critique_document,
)
from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.ir.types import IRDocument, IRNode, NodeType, IRStyle, IRPosition


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
# 测试 1-8: 意图解析 — 文档类型
# ============================================================

def test_intent_doc_type():
    section("1. 意图解析 — 文档类型")

    b1 = parse_intent("做一个季度汇报 PPT")
    check("PPT → presentation", b1.doc_type == "presentation", f"got {b1.doc_type}")

    b2 = parse_intent("写一份项目文档 Word")
    check("Word → document", b2.doc_type == "document", f"got {b2.doc_type}")

    b3 = parse_intent("做一个 Excel 数据表")
    check("Excel → spreadsheet", b3.doc_type == "spreadsheet", f"got {b3.doc_type}")

    b4 = parse_intent("做一个产品展示")
    check("默认 → presentation", b4.doc_type == "presentation", f"got {b4.doc_type}")


# ============================================================
# 测试 9-14: 意图解析 — 风格 + 情绪
# ============================================================

def test_intent_style_mood():
    section("2. 意图解析 — 风格 + 情绪")

    b1 = parse_intent("科技感的深色主题 PPT")
    check("科技深色 → tech_dark", b1.style == "tech_dark", f"got {b1.style}")
    check("深色背景", b1.background == "dark", f"got {b1.background}")

    b2 = parse_intent("极简风格的演示文稿")
    check("极简 → minimal", b2.style == "minimal", f"got {b2.style}")

    b3 = parse_intent("创意活泼的彩色 PPT")
    check("创意 → creative", b3.style == "creative", f"got {b3.style}")

    b4 = parse_intent("学术论文报告")
    check("学术 → academic", b4.style == "academic", f"got {b4.style}")

    b5 = parse_intent("专业商务汇报")
    check("商务情绪", "professional" in b5.mood, f"got {b5.mood}")

    b6 = parse_intent("现代科技感的演示")
    check("现代情绪", "modern" in b6.mood, f"got {b6.mood}")


# ============================================================
# 测试 15-18: 意图解析 — 强调点 + 颜色
# ============================================================

def test_intent_emphasis_color():
    section("3. 意图解析 — 强调点 + 颜色")

    b1 = parse_intent("突出数据图表的汇报 PPT")
    check("强调图表", "charts" in b1.emphasis or "data_visualization" in b1.emphasis,
          f"got {b1.emphasis}")

    b2 = parse_intent("用图片为主的展示")
    check("强调图片", "images" in b2.emphasis, f"got {b2.emphasis}")

    b3 = parse_intent("颜色 #FF5733 的主题")
    check("提取颜色", b3.primary_color == "#FF5733", f"got {b3.primary_color}")

    b4 = parse_intent("5 页的 PPT")
    check("提取页数", b4.page_count == 5, f"got {b4.page_count}")


# ============================================================
# 测试 19-23: 设计建议 — 配色方案
# ============================================================

def test_suggest_color():
    section("4. 设计建议 — 配色方案")

    scheme = suggest_color_scheme("tech_dark")
    check("科技深色有主色", scheme.primary != "")
    check("科技深色背景深色", scheme.background == "#0F172A", f"got {scheme.background}")
    check("科技深色文本浅色", scheme.text_primary == "#F1F5F9", f"got {scheme.text_primary}")

    scheme2 = suggest_color_scheme("business_light")
    check("商务浅色背景白色", scheme2.background == "#FFFFFF")

    scheme3 = suggest_color_scheme("unknown_style")
    check("未知风格降级到商务", scheme3.name == "商务浅色")


# ============================================================
# 测试 24-28: 设计建议 — 布局 + 排版
# ============================================================

def test_suggest_layout():
    section("5. 设计建议 — 布局 + 排版")

    layout = suggest_layout("presentation", "cover")
    check("封面布局有标题位置", "title" in layout.positions)
    check("封面布局有副标题位置", "subtitle" in layout.positions)

    layout2 = suggest_layout("presentation", "chart")
    check("图表页有图表位置", "chart" in layout2.positions)

    layout3 = suggest_layout("document", "standard")
    check("文档布局有正文位置", "body" in layout3.positions)

    layout4 = suggest_layout("unknown_type")
    check("未知类型降级", layout4 is not None)


# ============================================================
# 测试 29-33: 综合设计建议
# ============================================================

def test_suggest_design():
    section("6. 综合设计建议")

    brief = parse_intent("科技感深色 PPT，突出数据图表")
    suggestion = suggest_design(brief)

    check("有配色方案", suggestion.color_scheme is not None)
    check("有布局建议", suggestion.layout is not None)
    check("有排版建议", suggestion.typography is not None)
    check("配色主色非空", suggestion.color_scheme.primary != "")
    check("排版标题字号合理", suggestion.typography.heading_size_range[0] >= 20)


# ============================================================
# 测试 34-38: 质量评审 — 对比度
# ============================================================

def test_critique_contrast():
    section("7. 质量评审 — 对比度")

    # 低对比度: 深灰文本 + 黑色背景
    doc = _make_ir_doc_with_text(
        content="看不清的文字",
        font_color="#333333",
        fill_color="#222222",
    )
    report = critique_document(doc)
    contrast_issues = [i for i in report.issues if i.category == "contrast"]
    check("低对比度检出", len(contrast_issues) > 0, f"got {len(contrast_issues)} issues")
    check("对比度问题为 WARNING", contrast_issues[0].severity == CritiqueSeverity.WARNING)

    # 高对比度: 黑文本 + 白背景
    doc2 = _make_ir_doc_with_text(
        content="清晰的文字",
        font_color="#000000",
        fill_color="#FFFFFF",
    )
    report2 = critique_document(doc2)
    contrast_issues2 = [i for i in report2.issues if i.category == "contrast"]
    check("高对比度无 WARNING", all(i.severity != CritiqueSeverity.WARNING for i in contrast_issues2))


# ============================================================
# 测试 39-42: 质量评审 — 层次 + 一致性
# ============================================================

def test_critique_hierarchy_consistency():
    section("8. 质量评审 — 层次 + 一致性")

    # 字号层次不够分明
    doc = _make_ir_doc_with_texts([
        ("标题", 16),
        ("正文", 14),
    ])
    report = critique_document(doc)
    hierarchy_issues = [i for i in report.issues if i.category == "hierarchy"]
    check("层次不够检出", len(hierarchy_issues) > 0)

    # 字号太多
    doc2 = _make_ir_doc_with_texts([
        ("标题", 32),
        ("子标题", 24),
        ("正文", 14),
        ("注释", 10),
        ("标签", 12),
        ("备注", 11),
    ])
    report2 = critique_document(doc2)
    consistency_issues = [i for i in report2.issues if i.category == "consistency"]
    check("一致性问题检出", len(consistency_issues) > 0)


# ============================================================
# 测试 43-45: 质量评审 — 质量分
# ============================================================

def test_critique_score():
    section("9. 质量评审 — 质量分")

    # 完美文档
    doc = _make_ir_doc_with_text(
        content="完美",
        font_color="#000000",
        fill_color="#FFFFFF",
    )
    report = critique_document(doc)
    check("质量分 100", report.score == 100.0, f"got {report.score}")
    check("is_passing", report.is_passing)

    # 有问题的文档
    doc2 = _make_ir_doc_with_texts([
        ("标题", 16),
        ("正文", 14),
    ])
    report2 = critique_document(doc2)
    check("有问题文档分 < 100", report2.score < 100.0, f"got {report2.score}")


# ============================================================
# 测试 46-48: 端到端 意图 → 建议 → DSL
# ============================================================

def test_e2e_intent_to_dsl():
    section("10. 端到端: 意图 → 建议 → DSL 编译")

    brief = parse_intent("商务风格的季度汇报 PPT，突出数据图表")
    suggestion = suggest_design(brief)

    # 用建议生成 DSL
    dsl = f"""
version: "4.0"
type: presentation
styles:
  title:
    font: {{ size: {suggestion.typography.heading_size_range[1]}, weight: 700, color: "{suggestion.color_scheme.text_primary}" }}
    fill: {{ color: "{suggestion.color_scheme.background}" }}
  body:
    font: {{ size: {suggestion.typography.body_size}, color: "{suggestion.color_scheme.text_secondary}" }}
slides:
  - layout: blank
    elements:
      - type: text
        content: "季度汇报"
        style: title
        position: {{ x: 20mm, y: 30mm, width: 200mm, height: 20mm }}
      - type: text
        content: "由 Office Suite 4.0 AI 引擎生成"
        style: body
        position: {{ x: 20mm, y: 60mm, width: 200mm, height: 10mm }}
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)
    check("DSL 编译成功", ir is not None)
    check("有幻灯片", len(ir.children) > 0)

    # 评审
    report = critique_document(ir)
    check("质量评审完成", report is not None)
    check("质量分有效", 0 <= report.score <= 100)


# ============================================================
# 辅助函数
# ============================================================

def _make_ir_doc_with_text(content: str, font_color: str = "", fill_color: str = "") -> IRDocument:
    """创建带单个文本节点的 IRDocument"""
    style = IRStyle(font_color=font_color or None, fill_color=fill_color or None)
    node = IRNode(
        node_type=NodeType.TEXT,
        content=content,
        style=style,
        position=IRPosition(x_mm=20, y_mm=20, width_mm=200, height_mm=10),
    )
    slide = IRNode(
        node_type=NodeType.SLIDE,
        children=[node],
    )
    return IRDocument(children=[slide])


def _make_ir_doc_with_texts(items: list[tuple[str, int]]) -> IRDocument:
    """创建带多个文本节点的 IRDocument"""
    nodes = []
    for content, font_size in items:
        style = IRStyle(font_size=font_size)
        node = IRNode(
            node_type=NodeType.TEXT,
            content=content,
            style=style,
            position=IRPosition(x_mm=20, y_mm=20, width_mm=200, height_mm=10),
        )
        nodes.append(node)
    slide = IRNode(
        node_type=NodeType.SLIDE,
        children=nodes,
    )
    return IRDocument(children=[slide])


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("  Office Suite 4.0 — Phase 5 测试套件")
    print("=" * 60)

    test_intent_doc_type()
    test_intent_style_mood()
    test_intent_emphasis_color()
    test_suggest_color()
    test_suggest_layout()
    test_suggest_design()
    test_critique_contrast()
    test_critique_hierarchy_consistency()
    test_critique_score()
    test_e2e_intent_to_dsl()

    print(f"\n{'=' * 60}")
    print(f"  结果:  PASS={_pass_count}  FAIL={_fail_count}")
    print(f"{'=' * 60}")

    return _fail_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
