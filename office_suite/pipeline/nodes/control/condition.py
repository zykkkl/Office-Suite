"""控制节点 — 条件分支

根据条件决定是否执行下游节点。
支持引用上游输出结果的变量。
"""

from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext


class ConditionNode(NodeExecutor):
    node_type = "condition"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        condition = params.get("condition", True)

        # 解析变量引用
        if isinstance(condition, str) and condition.startswith("${"):
            ref = condition[2:-1]
            condition = ctx.resolve_ref(ref)

        # 支持简单的比较表达式
        if isinstance(condition, str):
            condition = self._eval_expression(condition, ctx)

        result = bool(condition)
        ctx.set_output("_last_condition", result)
        return {"condition": result, "branch": "then" if result else "else"}

    @staticmethod
    def _eval_expression(expr: str, ctx: PipelineContext) -> bool:
        """解析简单比较表达式: field op value

        支持: ==, !=, >, <, >=, <=
        例如: "${fetch_data.count} > 0"
        """
        import re
        match = re.match(r'(.+?)\s*(==|!=|>=|<=|>|<)\s*(.+)', expr.strip())
        if not match:
            return bool(expr)

        left_str, op, right_str = match.groups()

        # 解析左右值
        left = left_str.strip()
        right = right_str.strip()

        if left.startswith("${") and left.endswith("}"):
            left = ctx.resolve_ref(left[2:-1])
        if right.startswith("${") and right.endswith("}"):
            right = ctx.resolve_ref(right[2:-1])

        # 尝试数值比较
        try:
            left = float(left)
            right = float(right)
        except (ValueError, TypeError):
            pass

        ops = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
        }

        return ops.get(op, lambda a, b: False)(left, right)
