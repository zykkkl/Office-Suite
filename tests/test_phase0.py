"""Phase 0 技术验证：YAML → IR → PPTX 全流程测试"""

import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.dsl.parser import parse_yaml
from office_suite.ir.compiler import compile_document
from office_suite.ir.types import validate_ir
from office_suite.renderer.pptx.deck import PPTXRenderer


def test_phase0():
    """Phase 0 验收标准：
    1. YAML → IR 解析通过
    2. IR → PPTX 渲染出页面
    3. 打开 PPTX 文件确认内容正确
    """
    test_dir = Path(__file__).parent
    dsl_path = test_dir / "hello_world.yml"
    output_path = test_dir / "output" / "hello_world.pptx"

    print("=" * 60)
    print("Office Suite 4.0 — Phase 0 技术验证")
    print("=" * 60)

    # Step 1: DSL → Document
    print("\n[1/4] 解析 DSL...")
    doc = parse_yaml(dsl_path)
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
    warnings = validate_ir(ir_doc)
    if warnings:
        for w in warnings:
            print(f"  [Warning] {w}")
    else:
        print("  校验通过，无警告")

    # Step 4: IR → PPTX
    print("\n[4/4] 渲染 PPTX...")
    renderer = PPTXRenderer()
    result = renderer.render(ir_doc, output_path)
    print(f"  输出: {result}")
    print(f"  文件大小: {result.stat().st_size:,} bytes")

    print("\n" + "=" * 60)
    print("Phase 0 验证完成!")
    print(f"请打开 {result} 确认内容正确")
    print("=" * 60)

    return result


if __name__ == "__main__":
    test_phase0()
