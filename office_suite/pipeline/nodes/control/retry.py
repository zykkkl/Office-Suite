"""控制节点 — 重试

对失败的上游操作进行重试，支持指数退避。
"""

import time
from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext


class RetryNode(NodeExecutor):
    node_type = "retry"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        target = params.get("target")
        max_retries = params.get("max_retries", 3)
        backoff = params.get("backoff", "exponential")  # linear / exponential / fixed
        initial_delay = params.get("initial_delay", 1.0)  # 秒
        executor_fn = params.get("executor")  # 可执行函数

        if target is None and executor_fn is None:
            raise ValueError("retry: 缺少 target 或 executor 参数")

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                if executor_fn and callable(executor_fn):
                    result = executor_fn(params.get("params", {}), ctx)
                else:
                    # 对引用的目标重新执行（需要 provider 支持）
                    ctx.log(f"retry: 第 {attempt + 1} 次尝试 '{target}'")
                    result = {"target": target, "attempt": attempt + 1}

                return {
                    "result": result,
                    "attempts": attempt + 1,
                    "success": True,
                }

            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    delay = self._calc_delay(attempt, backoff, initial_delay)
                    ctx.log(f"retry: 第 {attempt + 1} 次失败，{delay:.1f}s 后重试 — {e}")
                    time.sleep(delay)

        return {
            "result": None,
            "attempts": max_retries + 1,
            "success": False,
            "last_error": last_error,
        }

    @staticmethod
    def _calc_delay(attempt: int, backoff: str, initial: float) -> float:
        if backoff == "fixed":
            return initial
        elif backoff == "linear":
            return initial * (attempt + 1)
        else:  # exponential
            return initial * (2 ** attempt)
