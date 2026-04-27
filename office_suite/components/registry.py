"""组件注册表 — 可复用组件的注册和调用

设计方案：组件化是比元素更高一级的抽象。
组件接收参数，生成一组 IR 节点。

组件 vs 元素:
  - 元素: text, image, shape, table, chart — 单一内容
  - 组件: chart_card, stat_card, timeline — 多元素组合

数据流：
  DSL 中 type: "component" + component: "chart_card"
  → ComponentRegistry.get("chart_card")
  → component.generate(params) → list[IRNode]
  → 插入 IR 树

组件可在渲染器间复用（同一组件生成不同格式的 IR）。
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from ..ir.types import IRNode, NodeType, IRPosition, IRStyle


class Component(Protocol):
    """组件协议"""
    name: str
    description: str

    def generate(self, params: dict[str, Any]) -> list[IRNode]:
        """根据参数生成 IR 节点列表"""
        ...


@dataclass
class ComponentDef:
    """组件定义"""
    name: str
    description: str
    # 参数 schema (名称 → 类型 + 默认值)
    param_schema: dict[str, dict] = field(default_factory=dict)
    # 生成函数
    generator: Callable[[dict[str, Any]], list[IRNode]] | None = None


# ============================================================
# 注册表
# ============================================================

_COMPONENT_REGISTRY: dict[str, ComponentDef] = {}


def register_component(name: str, description: str,
                       generator: Callable[[dict[str, Any]], list[IRNode]],
                       param_schema: dict[str, dict] | None = None):
    """注册组件

    Args:
        name: 组件名
        description: 组件描述
        generator: 生成函数 (params → list[IRNode])
        param_schema: 参数定义
    """
    _COMPONENT_REGISTRY[name] = ComponentDef(
        name=name,
        description=description,
        param_schema=param_schema or {},
        generator=generator,
    )


def get_component(name: str) -> ComponentDef | None:
    """获取组件定义"""
    return _COMPONENT_REGISTRY.get(name)


def list_components() -> list[str]:
    """列出所有已注册组件名"""
    return list(_COMPONENT_REGISTRY.keys())


def generate_component(name: str, params: dict[str, Any]) -> list[IRNode]:
    """生成组件 IR 节点

    Args:
        name: 组件名
        params: 组件参数

    Returns:
        IR 节点列表

    Raises:
        ValueError: 组件不存在
    """
    comp = _COMPONENT_REGISTRY.get(name)
    if comp is None:
        raise ValueError(f"组件 '{name}' 未注册。可用组件: {list_components()}")
    if comp.generator is None:
        raise ValueError(f"组件 '{name}' 未实现生成函数")
    return comp.generator(params)


# ============================================================
# 辅助: 位置构造
# ============================================================

def _pos(x: int | str = 0, y: int | str = 0,
         w: int | str = 200, h: int | str = 50) -> IRPosition:
    """快速构造 IRPosition (mm)"""
    return IRPosition(
        x_mm=float(x) if isinstance(x, (int, float)) else 0,
        y_mm=float(y) if isinstance(y, (int, float)) else 0,
        width_mm=float(w) if isinstance(w, (int, float)) else 200,
        height_mm=float(h) if isinstance(h, (int, float)) else 50,
    )
