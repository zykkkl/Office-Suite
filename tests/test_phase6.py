"""Phase 6 测试套件：主题 + 组件库

验收标准：
1. Fluent 主题完整可用（light + dark）
2. 通用主题完整可用（light + dark）
3. 内置 5+ 组件可用
4. 组件注册/调用正确
5. 主题继承/混合正确
6. 主题 → DSL 风格导出正确
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.themes.engine import (
    Theme, ThemeColors, ThemeTypography,
    register_theme, get_theme, get_theme_or_default,
    list_themes, inherit_theme, blend_themes,
)
from office_suite.themes.fluent import create_fluent_light, create_fluent_dark
from office_suite.themes.universal import create_universal_light, create_universal_dark
from office_suite.components.registry import (
    register_component, get_component, list_components, generate_component,
)
from office_suite.ir.types import IRNode, NodeType
from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.renderer.pptx.deck import PPTXRenderer


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
# 测试 1-6: 主题引擎 — 注册 + 获取
# ============================================================

def test_theme_registry():
    section("1. 主题注册表")

    themes = list_themes()
    check("有已注册主题", len(themes) > 0, f"got {themes}")
    check("fluent 已注册", "fluent" in themes)
    check("fluent_dark 已注册", "fluent_dark" in themes)
    check("universal 已注册", "universal" in themes)
    check("universal_dark 已注册", "universal_dark" in themes)

    # 获取
    fluent = get_theme("fluent")
    check("fluent 主题非 None", fluent is not None)
    check("fluent 名称正确", fluent.name == "fluent")


# ============================================================
# 测试 7-12: Fluent 主题
# ============================================================

def test_fluent_theme():
    section("2. Fluent 主题")

    theme = create_fluent_light()
    check("Fluent 浅色名称", theme.display_name == "Microsoft Fluent Design")
    check("Fluent 浅色模式", theme.mode == "light")
    check("Fluent 主色 #0078D4", theme.colors.primary == "#0078D4")
    check("Fluent 标题字体 Segoe UI", theme.typography.heading_font == "Segoe UI")
    check("Fluent 有预设", len(theme.presets) > 0)
    check("Fluent 有元数据", "reference" in theme.metadata)

    # 深色
    dark = create_fluent_dark()
    check("Fluent 深色模式", dark.mode == "dark")
    check("Fluent 深色主色", dark.colors.primary == "#60CDFF")


# ============================================================
# 测试 13-18: 通用主题
# ============================================================

def test_universal_theme():
    section("3. 通用主题")

    theme = create_universal_light()
    check("通用浅色名称", theme.display_name == "Universal")
    check("通用浅色模式", theme.mode == "light")
    check("通用主色 #1E3A5F", theme.colors.primary == "#1E3A5F")
    check("通用标题字体", theme.typography.heading_font == "Microsoft YaHei UI")
    check("通用有预设", len(theme.presets) > 0)

    dark = create_universal_dark()
    check("通用深色模式", dark.mode == "dark")


# ============================================================
# 测试 19-23: 主题继承 + 混合
# ============================================================

def test_theme_inherit():
    section("4. 主题继承 + 混合")

    fluent = get_theme("fluent")

    # 继承
    custom = inherit_theme(fluent, {
        "name": "custom_corp",
        "colors": {"primary": "#FF0000"},
    })
    check("继承自定义名称", custom.name == "custom_corp")
    check("继承覆盖主色", custom.colors.primary == "#FF0000")
    check("继承保留字体", custom.typography.heading_font == "Segoe UI")

    # 混合
    universal = get_theme("universal")
    blended = blend_themes(fluent, universal, ratio=0.3)
    check("混合名称包含两个主题", "x" in blended.name)
    check("混合显示名包含 ×", "×" in blended.display_name)


# ============================================================
# 测试 24-27: 主题 → DSL 风格导出
# ============================================================

def test_theme_to_style():
    section("5. 主题 → DSL 风格导出")

    theme = get_theme("fluent")
    style_dict = theme.to_style_dict()

    check("导出有 heading", "heading" in style_dict)
    check("导出有 body", "body" in style_dict)
    check("导出有 caption", "caption" in style_dict)
    check("heading 有 font", "font" in style_dict["heading"])


# ============================================================
# 测试 28-33: 组件注册表
# ============================================================

def test_component_registry():
    section("6. 组件注册表")

    comps = list_components()
    check("有已注册组件", len(comps) > 0, f"got {comps}")
    check("chart_card 已注册", "chart_card" in comps)
    check("stat_card 已注册", "stat_card" in comps)
    check("timeline 已注册", "timeline" in comps)
    check("comparison 已注册", "comparison" in comps)
    check("infographic 已注册", "infographic" in comps)


# ============================================================
# 测试 34-38: chart_card 组件
# ============================================================

def test_chart_card():
    section("7. chart_card 组件")

    nodes = generate_component("chart_card", {
        "title": "月度营收",
        "chart_type": "bar",
        "categories": ["1月", "2月", "3月"],
        "series": [{"name": "营收", "values": [100, 120, 150]}],
        "caption": "数据来源: 财务部",
    })

    check("生成 3 个节点", len(nodes) == 3, f"got {len(nodes)}")
    check("标题节点 TEXT", nodes[0].node_type == NodeType.TEXT)
    check("标题内容", nodes[0].content == "月度营收")
    check("图表节点 CHART", nodes[1].node_type == NodeType.CHART)
    check("注释节点", nodes[2].content == "数据来源: 财务部")


# ============================================================
# 测试 39-42: stat_card 组件
# ============================================================

def test_stat_card():
    section("8. stat_card 组件")

    nodes = generate_component("stat_card", {
        "value": "¥128K",
        "label": "月营收",
        "trend": "up",
        "trend_value": "+12%",
    })

    check("生成 3 个节点", len(nodes) == 3)
    check("大数字", nodes[0].content == "¥128K")
    check("标签", nodes[1].content == "月营收")
    check("趋势含箭头", "↑" in nodes[2].content)


# ============================================================
# 测试 43-46: timeline 组件
# ============================================================

def test_timeline():
    section("9. timeline 组件")

    nodes = generate_component("timeline", {
        "events": [
            {"date": "2024-01", "title": "项目启动", "description": "确定需求"},
            {"date": "2024-03", "title": "完成设计", "description": "UI 定稿"},
            {"date": "2024-06", "title": "上线发布", "description": "正式上线"},
        ],
    })

    check("生成多个节点", len(nodes) >= 5)
    check("有日期文本", any("2024-01" in (n.content or "") for n in nodes))
    check("有事件标题", any("项目启动" in (n.content or "") for n in nodes))
    check("有描述文本", any("确定需求" in (n.content or "") for n in nodes))


# ============================================================
# 测试 47-49: comparison 组件
# ============================================================

def test_comparison():
    section("10. comparison 组件")

    nodes = generate_component("comparison", {
        "left_title": "传统方案",
        "left_items": ["手动排版", "单一格式", "无 AI"],
        "right_title": "Office Suite 4.0",
        "right_items": ["声明式 DSL", "多格式输出", "AI 辅助"],
    })

    check("生成 4 个节点", len(nodes) == 4)
    check("左栏标题", nodes[0].content == "传统方案")
    check("右栏标题", nodes[2].content == "Office Suite 4.0")


# ============================================================
# 测试 50-52: infographic 组件
# ============================================================

def test_infographic():
    section("11. infographic 组件")

    nodes = generate_component("infographic", {
        "title": "关键指标",
        "metrics": [
            {"value": "1,234", "label": "用户数"},
            {"value": "95%", "label": "满意度"},
            {"value": "¥50K", "label": "营收"},
            {"value": "12", "label": "新功能"},
        ],
        "columns": 2,
    })

    check("生成 9 个节点", len(nodes) == 9, f"got {len(nodes)}")
    check("有标题", nodes[0].content == "关键指标")
    check("有指标值", any("1,234" in (n.content or "") for n in nodes))


# ============================================================
# 测试 53-55: 组件 → PPTX 端到端
# ============================================================

def test_e2e_component_to_pptx():
    section("12. 端到端: 组件 → PPTX")

    # 用主题样式 + 组件生成 DSL
    theme = get_theme("fluent")
    style_dict = theme.to_style_dict()

    # 生成组件节点
    chart_nodes = generate_component("chart_card", {
        "title": "季度趋势",
        "chart_type": "line",
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "series": [
            {"name": "营收", "values": [100, 130, 160, 200]},
            {"name": "成本", "values": [80, 90, 95, 100]},
        ],
    })

    stat_nodes = generate_component("stat_card", {
        "value": "¥2.4M",
        "label": "年度总营收",
        "trend": "up",
        "trend_value": "+28%",
    })

    # 用 DSL 渲染 PPTX 验证
    dsl = f"""
version: "4.0"
type: presentation
styles:
  heading:
    font: {{ size: 28, weight: 700, color: "{theme.colors.text_primary}" }}
  body:
    font: {{ size: 14, color: "{theme.colors.text_secondary}" }}
slides:
  - layout: blank
    elements:
      - type: text
        content: "季度趋势"
        style: heading
        position: {{ x: 20mm, y: 10mm, width: 200mm, height: 12mm }}
      - type: chart
        chart_type: line
        position: {{ x: 20mm, y: 30mm, width: 200mm, height: 100mm }}
        extra:
          title: "季度趋势"
          categories: ["Q1", "Q2", "Q3", "Q4"]
          series:
            - name: "营收"
              values: [100, 130, 160, 200]
            - name: "成本"
              values: [80, 90, 95, 100]
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    output = PROJECT_ROOT / "tests" / "output" / "phase6_themed.pptx"
    renderer = PPTXRenderer()
    out_path = renderer.render(ir, output)
    check("PPTX 生成", out_path.exists())
    check("PPTX > 10KB", out_path.stat().st_size > 10000,
          f"{out_path.stat().st_size} bytes")


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("  Office Suite 4.0 — Phase 6 测试套件")
    print("=" * 60)

    test_theme_registry()
    test_fluent_theme()
    test_universal_theme()
    test_theme_inherit()
    test_theme_to_style()
    test_component_registry()
    test_chart_card()
    test_stat_card()
    test_timeline()
    test_comparison()
    test_infographic()
    test_e2e_component_to_pptx()

    print(f"\n{'=' * 60}")
    print(f"  结果:  PASS={_pass_count}  FAIL={_fail_count}")
    print(f"{'=' * 60}")

    return _fail_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
