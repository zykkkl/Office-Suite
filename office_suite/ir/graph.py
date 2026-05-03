"""IR 依赖图 — 文档结构的图表示

设计方案第四章：中间表示。

IR 图将文档结构表示为有向无环图（DAG），
用于：
  - 元素依赖分析（数据绑定 → 图表 → 渲染）
  - 拓扑排序（确定渲染顺序）
  - 变更传播（修改数据源时确定需要重新渲染的元素）

注意：pipeline/core/graph.py 是流水线 DAG，
本模块是 IR 文档结构图，层级不同。
"""

from dataclasses import dataclass, field
from typing import Any
from enum import Enum

from .types import IRNode, IRDocument, NodeType


class EdgeType(Enum):
    """依赖边类型"""
    CONTAINS = "contains"       # 包含关系（父→子）
    REFERENCES = "references"   # 引用关系（数据绑定）
    DEPENDS_ON = "depends_on"   # 依赖关系（渲染顺序）
    STYLE_OF = "style_of"      # 样式关联


@dataclass
class GraphNode:
    """图节点"""
    node_id: str
    ir_node: IRNode
    children: list[str] = field(default_factory=list)    # 子节点 ID
    dependencies: list[str] = field(default_factory=list)  # 依赖的节点 ID
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """图边"""
    source: str       # 源节点 ID
    target: str       # 目标节点 ID
    edge_type: EdgeType
    metadata: dict[str, Any] = field(default_factory=dict)


class IRGraph:
    """IR 文档结构图

    用法：
        graph = IRGraph.from_document(ir_doc)
        order = graph.topological_sort()
        descendants = graph.get_descendants("slide_1")
    """

    def __init__(self):
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []
        self._adjacency: dict[str, list[str]] = {}  # source → [targets]
        self._reverse_adj: dict[str, list[str]] = {} # target → [sources]
        self._id_counter: int = 0

    @classmethod
    def from_document(cls, doc: IRDocument) -> "IRGraph":
        """从 IRDocument 构建依赖图

        Args:
            doc: IR 文档

        Returns:
            IRGraph 实例
        """
        graph = cls()
        graph._build_from_node(doc.root, parent_id=None)
        return graph

    def _build_from_node(self, node: IRNode, parent_id: str | None) -> str:
        """递归构建图"""
        self._id_counter += 1
        node_id = f"{node.node_type.value}_{self._id_counter}"
        graph_node = GraphNode(node_id=node_id, ir_node=node)
        self._nodes[node_id] = graph_node

        # 建立包含边
        if parent_id:
            self._add_edge(parent_id, node_id, EdgeType.CONTAINS)
            self._nodes[parent_id].children.append(node_id)

        # 递归处理子节点
        for child in node.children:
            child_id = self._build_from_node(child, node_id)
            graph_node.children.append(child_id)

        return node_id

    def _add_edge(self, source: str, target: str, edge_type: EdgeType,
                  metadata: dict | None = None) -> None:
        """添加边"""
        edge = GraphEdge(source=source, target=target, edge_type=edge_type,
                         metadata=metadata or {})
        self._edges.append(edge)
        self._adjacency.setdefault(source, []).append(target)
        self._reverse_adj.setdefault(target, []).append(source)

    def get_node(self, node_id: str) -> GraphNode | None:
        """获取节点"""
        return self._nodes.get(node_id)

    def get_children(self, node_id: str) -> list[GraphNode]:
        """获取子节点"""
        return [self._nodes[cid] for cid in self._adjacency.get(node_id, [])
                if cid in self._nodes]

    def get_parents(self, node_id: str) -> list[GraphNode]:
        """获取父节点"""
        return [self._nodes[pid] for pid in self._reverse_adj.get(node_id, [])
                if pid in self._nodes]

    def get_descendants(self, node_id: str) -> list[GraphNode]:
        """获取所有后代节点（BFS）"""
        visited = set()
        queue = [node_id]
        result = []
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            if current != node_id and current in self._nodes:
                result.append(self._nodes[current])
            queue.extend(self._adjacency.get(current, []))
        return result

    def get_ancestors(self, node_id: str) -> list[GraphNode]:
        """获取所有祖先节点"""
        visited = set()
        queue = [node_id]
        result = []
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            if current != node_id and current in self._nodes:
                result.append(self._nodes[current])
            queue.extend(self._reverse_adj.get(current, []))
        return result

    def topological_sort(self) -> list[str]:
        """拓扑排序（Kahn 算法）

        Returns:
            节点 ID 列表（依赖序）
        """
        in_degree: dict[str, int] = {nid: 0 for nid in self._nodes}
        for edge in self._edges:
            if edge.edge_type == EdgeType.DEPENDS_ON:
                in_degree[edge.target] = in_degree.get(edge.target, 0) + 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        result = []
        while queue:
            nid = queue.pop(0)
            result.append(nid)
            for target in self._adjacency.get(nid, []):
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)

        return result

    def find_cycles(self) -> list[list[str]]:
        """检测环（DFS）

        Returns:
            环列表，每个环为节点 ID 列表
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {nid: WHITE for nid in self._nodes}
        cycles = []

        def dfs(node: str, path: list[str]) -> None:
            color[node] = GRAY
            path.append(node)
            for neighbor in self._adjacency.get(node, []):
                if neighbor not in self._nodes:
                    continue
                if color[neighbor] == GRAY:
                    # 找到环
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                elif color[neighbor] == WHITE:
                    dfs(neighbor, path)
            path.pop()
            color[node] = BLACK

        for nid in self._nodes:
            if color[nid] == WHITE:
                dfs(nid, [])

        return cycles

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)
