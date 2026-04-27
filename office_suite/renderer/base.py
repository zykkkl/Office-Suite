"""渲染器基类 + 能力声明接口

设计方案第八章核心概念：每个渲染器必须声明自己支持的 IR 特性，
不支持的特性通过 fallback_map 优雅降级，而不是直接报错。

示例：
  PPTX 支持动画和艺术字 → 声明 supported_animations, supported_text_transforms
  DOCX 不支持动画和艺术字 → 空集合，渲染时跳过或降级为普通文本

新增渲染器时只需：
  1. 继承 BaseRenderer
  2. 实现 capability 属性声明支持的能力
  3. 实现 render() 方法
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..ir.types import IRDocument, IRNode, NodeType


@dataclass
class RendererCapability:
    """渲染器能力声明 — 每个渲染器必须声明自己支持的 IR 特性"""
    supported_node_types: set[NodeType] = field(default_factory=set)
    supported_layout_modes: set[str] = field(default_factory=lambda: {"absolute", "relative"})
    supported_text_transforms: set[str] = field(default_factory=set)
    supported_animations: set[str] = field(default_factory=set)
    supported_effects: set[str] = field(default_factory=set)
    # 降级映射：不支持的特性 → 降级行为
    fallback_map: dict[str, str] = field(default_factory=dict)

    def supports(self, feature: str, feature_set: str = "effects") -> bool:
        """检查是否支持某特性"""
        target = getattr(self, f"supported_{feature_set}", set())
        return feature in target

    def get_fallback(self, feature: str) -> str | None:
        """获取降级行为"""
        return self.fallback_map.get(feature)


class BaseRenderer(ABC):
    """渲染器基类"""

    @property
    @abstractmethod
    def capability(self) -> RendererCapability:
        """返回此渲染器的能力声明"""
        ...

    @abstractmethod
    def render(self, doc: IRDocument, output_path: str | Path) -> Path:
        """渲染 IRDocument 到目标格式文件，返回输出路径"""
        ...

    def _apply_fallback(self, node: IRNode, feature: str) -> str | None:
        """应用降级策略"""
        fallback = self.capability.get_fallback(feature)
        if fallback:
            return fallback
        return None
