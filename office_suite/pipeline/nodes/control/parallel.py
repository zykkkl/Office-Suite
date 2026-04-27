"""控制节点 — 并行扇出

将多个子任务并行执行，汇聚结果。
在 scheduler.run_parallel() 中由调度器自动处理层级并行，
此节点用于显式声明并行扇出/扇入语义。
"""

from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext


class ParallelNode(NodeExecutor):
    node_type = "parallel"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        branches = params.get("branches", [])

        if not branches:
            return {"branches": [], "results": []}

        # 解析分支定义中的变量引用
        resolved_branches = []
        for branch in branches:
            if isinstance(branch, str) and branch.startswith("${"):
                ref = branch[2:-1]
                resolved_branches.append(ctx.resolve_ref(ref))
            else:
                resolved_branches.append(branch)

        # 实际并行执行由 scheduler.run_parallel() 处理
        # 此节点负责声明语义 + 收集下游结果
        ctx.set_output("_parallel_branches", resolved_branches)
        return {
            "branches": resolved_branches,
            "note": "并行执行由 scheduler 的层级并行调度处理",
        }
