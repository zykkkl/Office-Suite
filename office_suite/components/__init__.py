"""组件库 — 可复用的多元素组合

设计方案：组件是比元素更高一级的抽象，
接收参数生成一组 IR 节点。

内置组件：
  - chart_card: 图表卡片
  - stat_card: 统计卡片
  - timeline: 时间线
  - comparison: 对比
  - infographic: 信息图

使用方式：
  from office_suite.components import generate_component
  nodes = generate_component("chart_card", {"title": "月度营收", ...})
"""

from .registry import (
    register_component,
    get_component,
    list_components,
    generate_component,
)

# 确保内置组件被注册
from .builtins import chart_card  # noqa: F401
from .builtins import stat_card  # noqa: F401
from .builtins import timeline  # noqa: F401
from .builtins import comparison  # noqa: F401
from .builtins import infographic  # noqa: F401

__all__ = [
    "register_component",
    "get_component",
    "list_components",
    "generate_component",
]
