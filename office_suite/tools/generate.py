"""通用文档生成脚本 — YAML DSL → PPTX + PDF

用法：
  py generate.py <yaml文件名>

示例：
  py generate.py apple_benefits
  py generate.py company_intro

目录结构：
  demo_output/<文件名>/
  ├── <文件名>.yml
  ├── <文件名>.pptx
  └── <文件名>.pdf
"""

import sys
from pathlib import Path
from ..dsl.parser import parse_yaml
from ..ir.compiler import compile_document
from ..renderer.pptx.deck import PPTXRenderer
from ..renderer.pdf.canvas import PDFRenderer

# 根输出目录（向上两级到项目根目录）
DEMO_DIR = Path(__file__).parent.parent.parent / "demo_output"


def generate(yaml_name: str):
    """生成 PPTX 和 PDF"""
    # 每个项目独立文件夹
    project_dir = DEMO_DIR / yaml_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # 1. 解析 DSL
    yaml_path = project_dir / f"{yaml_name}.yml"
    if not yaml_path.exists():
        print(f"错误：找不到 {yaml_path}")
        return

    doc = parse_yaml(yaml_path)

    # 2. 编译为 IR
    ir_doc = compile_document(doc)

    # 3. 渲染 PPTX
    pptx_renderer = PPTXRenderer()
    pptx_path = pptx_renderer.render(ir_doc, project_dir / f"{yaml_name}.pptx")
    print(f"PPTX 生成完成: {pptx_path}")

    # 4. 渲染 PDF
    pdf_renderer = PDFRenderer(page_size="widescreen")
    pdf_path = pdf_renderer.render(ir_doc, project_dir / f"{yaml_name}.pdf")
    print(f"PDF 生成完成: {pdf_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 默认生成 apple_benefits
        generate("apple_benefits")
    else:
        generate(sys.argv[1])
