"""格式互转工具 — 在不同输出格式之间转换

转换路径：
  PPTX -> PDF  (通过 PDF 渲染器重新渲染 IR)
  PPTX -> HTML (通过 HTML 渲染器重新渲染 IR)
  DOCX -> PDF
  HTML -> PDF

注意：转换通过 IR 中间层完成，不是文件格式级别的转换。
输入可以是 IRDocument 或原始 DSL 文件。
"""

from pathlib import Path
from typing import Any

from ..dsl.parser import parse_yaml, parse_yaml_string
from ..ir.compiler import compile_document
from ..ir.types import IRDocument
from ..renderer.pptx.deck import PPTXRenderer
from ..renderer.docx.document import DOCXRenderer
from ..renderer.xlsx.workbook import XLSXRenderer
from ..renderer.pdf.canvas import PDFRenderer
from ..renderer.html.dom import HTMLRenderer


_RENDERERS = {
    "pptx": PPTXRenderer,
    "docx": DOCXRenderer,
    "xlsx": XLSXRenderer,
    "pdf": PDFRenderer,
    "html": HTMLRenderer,
}


def convert_ir(ir_doc: IRDocument, output_path: Path | str, target_format: str) -> Path:
    """将 IR 文档渲染为目标格式

    Args:
        ir_doc: IR 文档
        output_path: 输出路径（不含扩展名也可以）
        target_format: 目标格式（pptx/docx/xlsx/pdf/html）

    Returns:
        输出文件路径
    """
    target_format = target_format.lower().lstrip(".")
    if target_format not in _RENDERERS:
        raise ValueError(f"不支持的目标格式: {target_format}，可选: {list(_RENDERERS.keys())}")

    output_path = Path(output_path)
    if output_path.suffix != f".{target_format}":
        output_path = output_path.with_suffix(f".{target_format}")

    renderer = _RENDERERS[target_format]()
    return renderer.render(ir_doc, output_path)


def convert_dsl_file(dsl_path: Path | str, output_path: Path | str, target_format: str) -> Path:
    """从 DSL 文件转换为目标格式

    Args:
        dsl_path: DSL YAML 文件路径
        output_path: 输出路径
        target_format: 目标格式

    Returns:
        输出文件路径
    """
    doc = parse_yaml(Path(dsl_path))
    ir = compile_document(doc)
    return convert_ir(ir, output_path, target_format)


def convert_dsl_string(yaml_str: str, output_path: Path | str, target_format: str) -> Path:
    """从 DSL 字符串转换为目标格式

    Args:
        yaml_str: DSL YAML 字符串
        output_path: 输出路径
        target_format: 目标格式

    Returns:
        输出文件路径
    """
    doc = parse_yaml_string(yaml_str)
    ir = compile_document(doc)
    return convert_ir(ir, output_path, target_format)


def batch_convert(ir_doc: IRDocument, output_dir: Path | str, formats: list[str]) -> dict[str, Path]:
    """将 IR 文档批量渲染为多种格式

    Args:
        ir_doc: IR 文档
        output_dir: 输出目录
        formats: 目标格式列表

    Returns:
        {格式: 输出路径} 映射
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for fmt in formats:
        out_path = output_dir / f"output.{fmt}"
        results[fmt] = convert_ir(ir_doc, out_path, fmt)
    return results
