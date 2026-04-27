"""流水线 DAG 图结构 — 声明式依赖关系 + 拓扑排序

设计理念（设计方案第六章）：
  不是「脚本按顺序跑」，是「声明式 DAG 编排」。
  声明依赖关系 → 自动拓扑排序 → 并行调度 → 汇聚输出
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class NodeStatus(Enum):
    """节点执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineNode:
    """流水线节点"""
    name: str
    node_type: str = ""            # fetch/transform/skill_invoke/render 等
    depends_on: list[str] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)
    # 运行时状态
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    error: str = ""
    # 执行函数（运行时注入）
    executor: Callable | None = None


@dataclass
class PipelineGraph:
    """流水线 DAG 图

    使用示例：
        graph = PipelineGraph()
        graph.add_node(PipelineNode(name="fetch_data", node_type="fetch"))
        graph.add_node(PipelineNode(name="transform", node_type="transform", depends_on=["fetch_data"]))
        graph.add_node(PipelineNode(name="render", node_type="render", depends_on=["transform"]))
        order = graph.topological_sort()  # ["fetch_data", "transform", "render"]
    """
    name: str = ""
    nodes: dict[str, PipelineNode] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: PipelineNode):
        """添加节点"""
        if node.name in self.nodes:
            raise ValueError(f"节点 '{node.name}' 已存在")
        self.nodes[node.name] = node

    def get_node(self, name: str) -> PipelineNode | None:
        """获取节点"""
        return self.nodes.get(name)

    def topological_sort(self) -> list[str]:
        """拓扑排序 — 返回节点执行顺序

        Kahn 算法：从入度为 0 的节点开始，逐步移除已处理节点。
        """
        # 计算入度
        in_degree: dict[str, int] = {name: 0 for name in self.nodes}
        for name, node in self.nodes.items():
            for dep in node.depends_on:
                if dep in in_degree:
                    in_degree[name] += 1

        # 入度为 0 的节点入队
        queue = [name for name, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            # 同一层级的节点可并行执行
            current = queue.pop(0)
            order.append(current)

            # 移除当前节点的边
            for name, node in self.nodes.items():
                if current in node.depends_on:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)

        if len(order) != len(self.nodes):
            # 存在循环依赖
            remaining = set(self.nodes.keys()) - set(order)
            raise ValueError(f"检测到循环依赖，涉及节点: {remaining}")

        return order

    def get_parallel_levels(self) -> list[list[str]]:
        """获取可并行执行的节点层级

        返回：[[level0_nodes], [level1_nodes], ...]
        同一层级的节点互不依赖，可并行执行。
        """
        in_degree: dict[str, int] = {name: 0 for name in self.nodes}
        for name, node in self.nodes.items():
            for dep in node.depends_on:
                if dep in in_degree:
                    in_degree[name] += 1

        levels = []
        remaining = set(self.nodes.keys())

        while remaining:
            # 找出入度为 0 的节点（当前层级）
            level = [n for n in remaining if in_degree[n] == 0]
            if not level:
                raise ValueError("检测到循环依赖")
            levels.append(level)

            # 移除当前层级
            for n in level:
                remaining.discard(n)
                for name in remaining:
                    if n in self.nodes[name].depends_on:
                        in_degree[name] -= 1

        return levels

    def validate(self) -> list[str]:
        """校验 DAG 合法性"""
        errors = []
        for name, node in self.nodes.items():
            for dep in node.depends_on:
                if dep not in self.nodes:
                    errors.append(f"节点 '{name}' 依赖不存在的节点 '{dep}'")
        return errors
