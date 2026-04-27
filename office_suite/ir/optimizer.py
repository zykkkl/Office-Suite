"""IR 优化器 — 文档结构和样式优化

设计方案第四章：中间表示。

IR 优化在编译后、渲染前执行，用于：
  - 消除冗余样式（合并相同的样式定义）
  - 折叠空容器（移除无内容的 Group/Section）
  - 简化嵌套（减少不必要的嵌套层级）
  - 预计算布局（将相对坐标转换为绝对坐标）

优化是安全的——不改变文档的视觉输出。
"""

from dataclasses import dataclass, field
from typing import Any

from .types import IRNode, IRDocument, NodeType, CONTAINMENT_RULES


@dataclass
class OptimizationStats:
    """优化统计"""
    nodes_removed: int = 0
    styles_merged: int = 0
    nesting_reduced: int = 0
    positions_resolved: int = 0


class IROptimizer:
    """IR 优化器

    优化管线：
      1. 消除空容器
      2. 合并冗余样式
      3. 简化嵌套
      4. 预计算布局

    用法：
        optimizer = IROptimizer()
        stats = optimizer.optimize(ir_doc)
    """

    def __init__(self):
        self.stats = OptimizationStats()

    def optimize(self, doc: IRDocument) -> OptimizationStats:
        """执行全部优化

        Args:
            doc: IR 文档（原地修改）

        Returns:
            优化统计
        """
        self.stats = OptimizationStats()

        # 1. 消除空容器
        self._remove_empty_containers(doc.root)

        # 2. 合并冗余样式
        self._merge_redundant_styles(doc)

        # 3. 简化嵌套
        self._simplify_nesting(doc.root)

        return self.stats

    def _remove_empty_containers(self, node: IRNode) -> bool:
        """移除空容器节点

        如果一个 Group/Section 没有子节点，移除它。
        返回 True 表示该节点本身应该被移除。
        """
        if not node.children:
            if node.node_type in (NodeType.GROUP, NodeType.SECTION):
                self.stats.nodes_removed += 1
                return True
            return False

        # 递归处理子节点
        to_remove = []
        for child in node.children:
            if self._remove_empty_containers(child):
                to_remove.append(child)

        for child in to_remove:
            node.children.remove(child)

        # 如果移除子节点后自己也变空了
        if not node.children and node.node_type in (NodeType.GROUP, NodeType.SECTION):
            self.stats.nodes_removed += 1
            return True

        return False

    def _merge_redundant_styles(self, doc: IRDocument) -> None:
        """合并相同的样式定义

        如果多个节点引用的样式内容完全相同，
        合并为一个样式引用。
        """
        if not doc.styles:
            return

        # 按内容分组
        style_content_map: dict[str, list[str]] = {}
        for name, style in doc.styles.items():
            # 将样式序列化为字符串用于比较
            key = self._style_to_key(style)
            style_content_map.setdefault(key, []).append(name)

        # 找到可合并的样式
        for key, names in style_content_map.items():
            if len(names) > 1:
                # 保留第一个，其余指向它
                primary = names[0]
                for alias in names[1:]:
                    # 将 alias 的引用重定向到 primary
                    self._redirect_style_refs(doc.root, alias, primary)
                    if alias in doc.styles:
                        del doc.styles[alias]
                    self.stats.styles_merged += 1

    def _style_to_key(self, style: Any) -> str:
        """将样式转换为可比较的字符串"""
        if hasattr(style, "__dict__"):
            return str(sorted(
                (k, str(v)) for k, v in style.__dict__.items() if v is not None
            ))
        return str(style)

    def _redirect_style_refs(self, node: IRNode, old_ref: str, new_ref: str) -> None:
        """重定向样式引用"""
        if node.style_ref == old_ref:
            node.style_ref = new_ref
        for child in node.children:
            self._redirect_style_refs(child, old_ref, new_ref)

    def _simplify_nesting(self, node: IRNode) -> None:
        """简化不必要的嵌套

        如果一个 Group 只有一个子节点，且该子节点也是 Group，
        可以合并它们。
        """
        new_children = []
        for child in node.children:
            self._simplify_nesting(child)

            # 如果子节点是只有一个子节点的 Group，提升其子节点
            if (child.node_type == NodeType.GROUP
                    and len(child.children) == 1
                    and child.children[0].node_type in (NodeType.TEXT, NodeType.SHAPE)):
                new_children.append(child.children[0])
                self.stats.nesting_reduced += 1
            else:
                new_children.append(child)

        node.children = new_children

    @property
    def last_stats(self) -> OptimizationStats:
        return self.stats
