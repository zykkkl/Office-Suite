"""设计节点 — 布局编排

将 DSL 文档编译为 IR（中间表示），包含完整的布局信息。
"""

from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext
from office_suite.ir.compiler import compile_document
from office_suite.ir.types import IRDocument


class LayoutNode(NodeExecutor):
    node_type = "layout"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        doc = params.get("doc")

        # 解析变量引用
        if isinstance(doc, str) and doc.startswith("${"):
            ref = doc[2:-1]
            doc = ctx.resolve_ref(ref)

        if doc is None:
            raise ValueError("layout: 缺少 doc 参数（DSL Document 对象）")

        # 如果已经是 IRDocument，直接返回
        if isinstance(doc, IRDocument):
            return doc

        # 编译 DSL → IR
        ir_doc = compile_document(doc)
        ctx.set_output("ir_document", ir_doc)
        return ir_doc
