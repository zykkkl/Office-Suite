"""AI 生成资源提供者 — 通过 AI 模型生成资源

设计方案第五章：资源中枢。

AI 提供者通过 AI 模型生成：
  - 图片：DALL-E 3, Stable Diffusion, MiniMax
  - 文案：Claude, GPT
  - 图表：智能图表生成
  - 图标：AI 图标生成

source 格式：
  ai__generate         — 通用 AI 生成
  ai__image            — 图片生成
  ai__text             — 文案生成

注意：实际 AI 调用需要 API key 和外部服务。
本模块提供接口定义和调用适配。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from ..registry import ResourceProvider, ResourceResult


class AIModel(Enum):
    """支持的 AI 模型"""
    CLAUDE_SONNET = "claude-sonnet"
    CLAUDE_HAIKU = "claude-haiku"
    GPT4O = "gpt-4o"
    DALLE3 = "dall-e-3"
    STABLE_DIFFUSION = "stable-diffusion"
    MINIMAX = "minimax"


@dataclass
class AIRequest:
    """AI 生成请求"""
    prompt: str
    model: str = "auto"
    output_type: str = "text"    # text, image, chart, icon
    params: dict[str, Any] | None = None


class AIProvider:
    """AI 生成资源提供者

    使用方式：
        provider = AIProvider()
        provider.set_caller("image", my_image_caller)
        result = provider.fetch({"ai": "image", "prompt": "abstract cover"})
    """

    name = "ai"
    prefixes = ["ai__", "ai:"]

    def __init__(self):
        self._callers: dict[str, Callable] = {}

    def set_caller(self, capability: str, caller: Callable) -> None:
        """设置 AI 调用函数

        Args:
            capability: 能力类型（image, text, chart, icon）
            caller: 调用函数，签名 (request: AIRequest) -> ResourceResult
        """
        self._callers[capability] = caller

    def can_handle(self, source: str | dict) -> bool:
        if isinstance(source, dict):
            return "ai" in source or "ai_generate" in source
        if isinstance(source, str):
            return source.startswith("ai__") or source.startswith("ai:")
        return False

    def fetch(self, source: str | dict, **kwargs) -> ResourceResult:
        """获取 AI 生成资源

        Args:
            source: 资源引用
                - "ai__image" 或 {"ai": "image", "prompt": "..."}
                - {"ai_generate": True, "prompt": "..."}

        Returns:
            ResourceResult
        """
        capability, request = self._parse_source(source, kwargs)

        if not capability:
            # 默认根据 prompt 推断
            capability = self._infer_capability(request)

        caller = self._callers.get(capability)
        if not caller:
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason=f"AI 能力 {capability} 未配置 caller",
                error=f"No caller for AI capability: {capability}",
            )

        try:
            result = caller(request)
            if isinstance(result, ResourceResult):
                return result
            return ResourceResult(
                success=True,
                data=result,
                source_used=f"ai__{capability}",
            )
        except Exception as e:
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason=f"AI 生成异常: {e}",
                error=str(e),
            )

    def _parse_source(self, source: str | dict, kwargs: dict) -> tuple[str, AIRequest]:
        """解析 source"""
        if isinstance(source, dict):
            capability = source.get("ai", source.get("ai_generate", ""))
            prompt = source.get("prompt", kwargs.get("prompt", ""))
            model = source.get("model", kwargs.get("model", "auto"))
            output_type = source.get("output_type", kwargs.get("output_type", "text"))
            params = {k: v for k, v in source.items()
                      if k not in ("ai", "ai_generate", "prompt", "model", "output_type")}
            params.update({k: v for k, v in kwargs.items()
                           if k not in ("prompt", "model", "output_type")})

            return str(capability), AIRequest(
                prompt=prompt,
                model=model,
                output_type=output_type,
                params=params,
            )

        if isinstance(source, str):
            if source.startswith("ai__"):
                cap = source[4:]
            elif source.startswith("ai:"):
                cap = source[3:]
            else:
                cap = ""
            return cap, AIRequest(
                prompt=kwargs.get("prompt", ""),
                model=kwargs.get("model", "auto"),
                output_type=kwargs.get("output_type", "text"),
                params={k: v for k, v in kwargs.items()
                        if k not in ("prompt", "model", "output_type")},
            )

        return "", AIRequest(prompt="")

    def _infer_capability(self, request: AIRequest) -> str:
        """从请求推断能力类型"""
        prompt_lower = request.prompt.lower()
        if any(kw in prompt_lower for kw in ("image", "picture", "photo", "illustration", "cover")):
            return "image"
        if any(kw in prompt_lower for kw in ("chart", "graph", "diagram", "visualization")):
            return "chart"
        if any(kw in prompt_lower for kw in ("icon", "logo", "symbol")):
            return "icon"
        return "text"

    def list_capabilities(self) -> list[str]:
        """列出已配置的 AI 能力"""
        return list(self._callers.keys())
