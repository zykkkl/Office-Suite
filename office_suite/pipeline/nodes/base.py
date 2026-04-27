"""节点执行器基类 + 注册机制"""

from abc import ABC, abstractmethod
from typing import Any

from ..core.context import PipelineContext

_REGISTRY: dict[str, type["NodeExecutor"]] = {}


class NodeExecutor(ABC):
    """节点执行器基类

    子类只需定义 node_type 和 execute()。
    类定义完成后自动注册到全局注册表。
    """

    node_type: str = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.node_type:
            _REGISTRY[cls.node_type] = cls

    @abstractmethod
    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        ...


def get_handler(node_type: str) -> NodeExecutor | None:
    """根据节点类型获取已注册的执行器实例"""
    cls = _REGISTRY.get(node_type)
    return cls() if cls else None


def list_registered() -> list[str]:
    """列出所有已注册的节点类型"""
    return sorted(_REGISTRY.keys())
