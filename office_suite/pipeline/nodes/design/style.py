"""设计节点 — 样式级联

对 IR 文档应用样式级联规则。
"""

from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext
from office_suite.ir.cascade import cascade_style_by_name, DEFAULT_THEME_STYLES
from office_suite.ir.types import IRDocument, IRStyle


class StyleNode(NodeExecutor):
    node_type = "style"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        doc = params.get("doc") or ctx.resolve_ref(params.get("doc_ref", ""))

        if doc is None:
            raise ValueError("style: 缺少 doc 参数")

        if not isinstance(doc, IRDocument):
            raise TypeError(f"style: 期望 IRDocument，得到 {type(doc).__name__}")

        # 获取主题样式（可覆盖）
        theme_name = params.get("theme", "default")
        theme_styles = params.get("theme_styles", DEFAULT_THEME_STYLES)

        # 对每个节点的样式重新级联
        self._cascade_document(doc, theme_styles)
        return doc

    @staticmethod
    def _cascade_document(doc: IRDocument, theme_styles: dict[str, IRStyle]):
        """对文档中所有节点应用级联"""
        for slide in doc.slides:
            for child in slide.children:
                if child.style_name:
                    child.style = cascade_style_by_name(
                        style_name=child.style_name,
                        theme_styles=theme_styles,
                        doc_styles={},
                        slide_style=slide.style,
                        element_style=child.style,
                    )
