"""计算节点 — MCP 服务器调用

通过 MCP 协议调用外部工具服务器（如 unsplash 图片搜索、数据库查询等）。
当前为骨架实现：定义接口和参数解析，实际 MCP 调用需要 mcp_provider 支持。
"""

from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext


class MCPCallNode(NodeExecutor):
    node_type = "mcp_call"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        server = params.get("server")
        if not server:
            raise ValueError("mcp_call: 缺少 server 参数")

        method = params.get("method", "")
        call_params = params.get("params", {})

        # 解析参数中的变量引用
        resolved_params = {}
        for key, val in call_params.items():
            if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
                ref = val[2:-1]
                resolved_params[key] = ctx.resolve_ref(ref)
            else:
                resolved_params[key] = val

        # MCP 调用需要 mcp_provider 支持
        ctx.log(f"mcp_call: 调用 '{server}.{method}' — 需要 mcp_provider 连接")
        return {
            "server": server,
            "method": method,
            "params": resolved_params,
            "status": "pending_provider",
            "note": f"MCP '{server}' 调用需要 hub/providers/mcp_provider 实现",
        }
