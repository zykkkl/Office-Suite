"""Phase 0 技术验证：YAML → IR → PPTX 全流程测试

使用内联最小 YAML，不依赖外部文件。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.ir.validator import validate_ir_v2
from office_suite.renderer.pptx.deck import PPTXRenderer


# 最小 YAML 定义 — 仅包含一个文本元素
MINIMAL_YAML = """
version: "4.0"
type: presentation
theme: default

slides:
  - layout: blank
    elements:
      - type: text
        content: "Hello World"
        position: { x: 50mm, y: 80mm, width: 150mm, height: 20mm }
        style:
          font: { family: "Arial", size: 44, weight: 700, color: "#1E293B" }
"""


def test_phase0():
    """Phase 0 验收标准：
    1. YAML → IR 解析通过
    2. IR 校验通过
    3. IR → PPTX 渲染出页面
    """
    test_dir = Path(__file__).parent
    output_dir = test_dir / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "hello_world.pptx"

    print("=" * 60)
    print("Office Suite 4.0 — Phase 0 技术验证")
    print("=" * 60)

    # Step 1: DSL → Document
    print("\n[1/4] 解析 DSL...")
    doc = parse_yaml_string(MINIMAL_YAML)
    print(f"  文档类型: {doc.type.value}")
    print(f"  主题: {doc.theme}")
    print(f"  幻灯片数: {len(doc.slides)}")
    print(f"  全局样式: {list(doc.styles.keys())}")

    # Step 2: Document → IR
    print("\n[2/4] 编译为 IR...")
    ir_doc = compile_document(doc)
    print(f"  IR 版本: {ir_doc.version}")
    print(f"  IR 幻灯片数: {len(ir_doc.children)}")
    for i, slide in enumerate(ir_doc.children):
        print(f"  slide[{i}]: {len(slide.children)} 个元素")
        for j, elem in enumerate(slide.children):
            print(f"    [{j}] {elem.node_type.value}: {elem.content or elem.source or '(shape)'}")

    # Step 3: IR 校验
    print("\n[3/4] 校验 IR...")
    validation = validate_ir_v2(ir_doc)
    for issue in validation.issues:
        print(f"  [{issue.severity.value}] {issue}")
    if validation.is_valid:
        print("  校验通过")
    else:
        print(f"  校验失败: {len(validation.errors)} 个错误")
        assert False, f"IR 校验失败: {validation.errors}"

    # Step 4: IR → PPTX
    print("\n[4/4] 渲染 PPTX...")
    renderer = PPTXRenderer()
    result = renderer.render(ir_doc, output_path)
    print(f"  输出: {result}")
    print(f"  文件大小: {result.stat().st_size:,} bytes")

    # 验证文件生成成功
    assert result.exists(), "PPTX 文件未生成"
    assert result.stat().st_size > 0, "PPTX 文件为空"

    print("\n" + "=" * 60)
    print("Phase 0 验证完成!")
    print("=" * 60)

    return result


if __name__ == "__main__":
    test_phase0()
