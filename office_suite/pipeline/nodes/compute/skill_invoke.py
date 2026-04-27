"""计算节点 — Skill 调用

调用其他 Skill（如 deep-research、chart-gen 等）的能力。
当前为骨架实现：定义接口和参数解析，实际 Skill 调用需要 MCP 或 Skill runtime 支持。
"""

from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext


class SkillInvokeNode(NodeExecutor):
    node_type = "skill_invoke"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        skill = params.get("skill")
        if not skill:
            raise ValueError("skill_invoke: 缺少 skill 参数")

        skill_params = params.get("params", {})

        # 解析参数中的变量引用
        resolved_params = self._resolve_params(skill_params, ctx)

        # Skill 调用需要对应的 provider 支持
        # 当前返回参数回显 + 未连接标记
        ctx.log(f"skill_invoke: 调用 '{skill}' — 需要 skill_provider 连接")
        return {
            "skill": skill,
            "params": resolved_params,
            "status": "pending_provider",
            "note": f"Skill '{skill}' 调用需要 hub/providers/skill_provider 实现",
        }

    @staticmethod
    def _resolve_params(params: dict, ctx: PipelineContext) -> dict:
        """递归解析参数中的 ${var} 引用"""
        resolved = {}
        for key, val in params.items():
            if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
                ref = val[2:-1]
                resolved[key] = ctx.resolve_ref(ref)
            elif isinstance(val, dict):
                resolved[key] = SkillInvokeNode._resolve_params(val, ctx)
            elif isinstance(val, list):
                resolved[key] = [
                    ctx.resolve_ref(v[2:-1]) if isinstance(v, str) and v.startswith("${") and v.endswith("}") else v
                    for v in val
                ]
            else:
                resolved[key] = val
        return resolved
