"""渲染节点 — 输出 XLSX"""

from pathlib import Path
from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext
from office_suite.ir.types import IRDocument
from office_suite.renderer.xlsx.workbook import XLSXRenderer


class RenderXLSXNode(NodeExecutor):
    node_type = "render_xlsx"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        doc = params.get("doc") or ctx.resolve_ref(params.get("doc_ref", ""))
        output = params.get("output_path", "output.xlsx")

        if doc is None:
            raise ValueError("render_xlsx: 缺少 doc 参数")

        if not isinstance(doc, IRDocument):
            raise TypeError(f"render_xlsx: 期望 IRDocument，得到 {type(doc).__name__}")

        renderer = XLSXRenderer()
        result_path = renderer.render(doc, output)
        ctx.set_output("last_render_path", str(result_path))
        return {"path": str(result_path), "format": "xlsx"}
