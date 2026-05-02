"""渲染蚂蚁故事 PPT"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.renderer.pptx.deck import PPTXRenderer

yaml_path = Path(__file__).parent / "ant_story.pptd.yaml"
output_path = Path(__file__).parent / "ant_story.pptx"

print("解析 DSL...")
doc = parse_yaml_string(yaml_path.read_text(encoding="utf-8"))
print(f"  幻灯片数: {len(doc.slides)}")

print("编译 IR...")
ir_doc = compile_document(doc)
print(f"  IR 幻灯片数: {len(ir_doc.children)}")

print("渲染 PPTX...")
renderer = PPTXRenderer()
result = renderer.render(ir_doc, output_path)
print(f"  输出: {result}")
print(f"  大小: {result.stat().st_size:,} bytes")
print("完成!")
