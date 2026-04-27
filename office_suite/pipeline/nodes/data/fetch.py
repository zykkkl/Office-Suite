"""数据节点 — 资源获取

对接 hub/resolver 从任意来源获取资源：
  - file:// 本地文件
  - mcp__xxx MCP 服务器（需 mcp_provider）
  - ai__generate AI 生成（需 ai_provider）
  - 内联 data: URI
"""

from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext
from office_suite.hub.resolver import ResourceResolver


class FetchNode(NodeExecutor):
    node_type = "fetch"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        source = params.get("source")
        if source is None:
            raise ValueError("fetch: 缺少 source 参数")

        # 解析变量引用
        if isinstance(source, str) and source.startswith("${"):
            ref = source[2:-1]
            source = ctx.resolve_ref(ref)

        # 使用 hub resolver 获取资源
        resolver = ResourceResolver()
        result = resolver.resolve(source)

        if result.success:
            return {
                "source": source,
                "data": result.data,
                "mime_type": result.mime_type,
                "fallback_used": result.fallback_used,
            }
        else:
            return {
                "source": source,
                "data": None,
                "fallback_used": True,
                "fallback_reason": result.fallback_reason or result.error or "unknown",
            }
