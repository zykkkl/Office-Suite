"""计算节点 — AI 资源生成

调用 AI 模型生成资源（图片、文案、图表等）。
当前为骨架实现：定义接口和参数解析，实际 AI 调用需要 ai_provider 支持。
"""

from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext


class AIGenerateNode(NodeExecutor):
    node_type = "ai_generate"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        prompt = params.get("prompt", "")
        model = params.get("model", "")
        output_type = params.get("output_type", "text")  # text / image / chart

        # 解析 prompt 中的变量引用
        if isinstance(prompt, str):
            prompt = self._resolve_string(prompt, ctx)

        # AI 生成需要 ai_provider 支持
        ctx.log(f"ai_generate: 生成 '{output_type}' — 需要 ai_provider 连接")
        return {
            "prompt": prompt,
            "model": model,
            "output_type": output_type,
            "status": "pending_provider",
            "note": f"AI '{output_type}' 生成需要 hub/providers/ai_provider 实现",
        }

    @staticmethod
    def _resolve_string(s: str, ctx: PipelineContext) -> str:
        """简单替换字符串中的 ${var} 占位符"""
        import re
        def replacer(match):
            ref = match.group(1)
            val = ctx.resolve_ref(ref)
            return str(val) if val is not None else match.group(0)
        return re.sub(r'\$\{([^}]+)\}', replacer, s)
