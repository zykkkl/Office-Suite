"""自由贝塞尔形状端到端渲染测试"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.ir.compiler import compile_document
from office_suite.dsl.parser import parse_yaml_string
from office_suite.renderer.pptx.deck import PPTXRenderer
from office_suite.design import blob_shape, wave_edge, ink_splash, cloud_shape, leaf_shape

YAML_CONTENT = """
title: Freeform Demo
style_preset: corporate
slides:
  - title: 自由形状演示
    background: { color: "#F8FAFC" }
    elements:
      - type: shape
        shape_type: freeform
        freeform_path: "M 20,30 C 20,60 80,60 80,30 C 80,10 50,5 20,30 Z"
        position: { x: 10, y: 20, width: 60, height: 40 }
        style:
          fill: { color: "#3B82F6" }
          opacity: 0.15
      - type: shape
        shape_type: freeform
        freeform_path: "M 10,10 L 40,10 Q 50,30 40,40 L 10,40 Z"
        position: { x: 80, y: 50, width: 40, height: 30 }
        style:
          fill: { color: "#10B981" }
          border: { color: "#059669", width: 0.5 }
          opacity: 0.2
      - type: text
        content: "自由贝塞尔形状 + 二次贝塞尔"
        position: { x: 20, y: 80, width: 160, height: 15 }
        style:
          font: { size: 16, weight: 700, color: "#1E293B" }
        align: center
  - title: Blob 装饰
    elements:
      - type: shape
        shape_type: freeform
        freeform_path: "M 50,30 C 50,60 80,60 80,30 C 80,10 50,10 50,30 Z"
        position: { x: 50, y: 30, width: 60, height: 50 }
        style:
          fill: { color: "#8B5CF6" }
          opacity: 0.1
"""

output_path = Path(__file__).parent / "freeform_demo.pptx"

print("解析 DSL...")
doc = parse_yaml_string(YAML_CONTENT)
print(f"  幻灯片数: {len(doc.slides)}")

print("编译 IR...")
ir_doc = compile_document(doc)
print(f"  IR 幻灯片数: {len(ir_doc.children)}")

print("渲染 PPTX...")
renderer = PPTXRenderer()
result = renderer.render(ir_doc, output_path)
print(f"  输出: {result}")
print(f"  大小: {result.stat().st_size:,} bytes")

print("\n预设形状路径示例:")
print(f"  blob_shape:     {blob_shape(seed=42)[:60]}...")
print(f"  wave_edge:      {wave_edge()[:60]}...")
print(f"  ink_splash:     {ink_splash(seed=5)[:60]}...")
print(f"  cloud_shape:    {cloud_shape()[:60]}...")
print(f"  leaf_shape:     {leaf_shape()[:60]}...")
print("\n完成!")
