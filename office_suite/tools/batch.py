"""批量生成工具 — 从模板/DSL 批量生成多份文档

典型场景：
  - 从模板 + 数据列表生成个性化文档
  - 从多个 DSL 文件批量渲染
  - 数据驱动的批量报告生成
"""

from pathlib import Path
from typing import Any

from ..dsl.parser import parse_yaml_string
from ..ir.compiler import compile_document
from ..renderer.pptx.deck import PPTXRenderer
from ..renderer.docx.document import DOCXRenderer
from ..renderer.xlsx.workbook import XLSXRenderer
from ..renderer.pdf.canvas import PDFRenderer
from ..renderer.html.dom import HTMLRenderer
from ..templates import render_template


_RENDERERS = {
    "pptx": PPTXRenderer,
    "docx": DOCXRenderer,
    "xlsx": XLSXRenderer,
    "pdf": PDFRenderer,
    "html": HTMLRenderer,
}


def batch_from_template(
    template_name: str,
    data_list: list[dict[str, str]],
    output_dir: Path | str,
    output_format: str = "pptx",
    name_key: str = "",
) -> list[Path]:
    """从模板 + 数据列表批量生成

    Args:
        template_name: 模板名称
        data_list: 数据列表，每个 dict 是一组模板变量
        output_dir: 输出目录
        output_format: 输出格式
        name_key: 用于命名输出文件的变量名（默认用序号）

    Returns:
        输出文件路径列表
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fmt = output_format.lower().lstrip(".")
    if fmt not in _RENDERERS:
        raise ValueError(f"不支持的格式: {fmt}")

    results = []
    renderer = _RENDERERS[fmt]()

    for i, variables in enumerate(data_list):
        dsl = render_template(template_name, variables)
        doc = parse_yaml_string(dsl)
        ir = compile_document(doc)

        if name_key and name_key in variables:
            filename = f"{variables[name_key]}.{fmt}"
        else:
            filename = f"{template_name}_{i + 1:03d}.{fmt}"

        out_path = renderer.render(ir, output_dir / filename)
        results.append(out_path)

    return results


def batch_from_dsl_files(
    dsl_paths: list[Path | str],
    output_dir: Path | str,
    output_format: str = "pptx",
) -> list[Path]:
    """从多个 DSL 文件批量渲染

    Args:
        dsl_paths: DSL 文件路径列表
        output_dir: 输出目录
        output_format: 输出格式

    Returns:
        输出文件路径列表
    """
    from ..dsl.parser import parse_yaml

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fmt = output_format.lower().lstrip(".")
    if fmt not in _RENDERERS:
        raise ValueError(f"不支持的格式: {fmt}")

    results = []
    renderer = _RENDERERS[fmt]()

    for dsl_path in dsl_paths:
        dsl_path = Path(dsl_path)
        doc = parse_yaml(dsl_path)
        ir = compile_document(doc)
        out_path = renderer.render(ir, output_dir / f"{dsl_path.stem}.{fmt}")
        results.append(out_path)

    return results
