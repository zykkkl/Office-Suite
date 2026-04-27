"""IR 引用解析器 — 解析数据绑定和资源引用

设计方案第四章：中间表示。

IR 中的元素可以引用：
  - 数据源：${data.revenue.Q1} → 绑定到 data 节中的值
  - 样式：style: "title" → 解析到 styles 节中的定义
  - 资源：source: "mcp__unsplash" → 交给 Hub 解析

本模块负责在渲染前将所有引用解析为具体值。
"""

from dataclasses import dataclass
from typing import Any
import re

from .types import IRNode, IRDocument, NodeType


@dataclass
class ResolutionResult:
    """解析结果"""
    value: Any
    resolved: bool = True
    source: str = ""       # 引用来源描述
    error: str = ""        # 解析失败原因


class ReferenceResolver:
    """引用解析器

    用法：
        resolver = ReferenceResolver(ir_doc)
        resolver.add_data_context({"revenue": {"Q1": 320, "Q2": 380}})
        result = resolver.resolve_expression("${data.revenue.Q1}")
    """

    def __init__(self, document: IRDocument | None = None):
        self._document = document
        self._data_context: dict[str, Any] = {}
        self._style_map: dict[str, Any] = {}
        self._variables: dict[str, Any] = {}

    def set_document(self, doc: IRDocument) -> None:
        """设置当前文档"""
        self._document = doc
        self._rebuild_style_map()

    def add_data_context(self, data: dict[str, Any]) -> None:
        """添加数据上下文"""
        self._data_context.update(data)

    def set_variable(self, name: str, value: Any) -> None:
        """设置变量"""
        self._variables[name] = value

    def _rebuild_style_map(self) -> None:
        """重建样式映射"""
        if not self._document:
            return
        self._style_map = dict(self._document.styles) if self._document.styles else {}

    def resolve_expression(self, expr: str) -> ResolutionResult:
        """解析表达式

        支持的语法：
          ${data.path.to.value}  — 数据引用
          ${var.name}            — 变量引用
          ${style.name}          — 样式引用

        Args:
            expr: 表达式字符串

        Returns:
            ResolutionResult 实例
        """
        if not expr or not expr.startswith("${"):
            return ResolutionResult(value=expr, resolved=False)

        # 提取路径
        path_match = re.match(r'^\$\{(.+?)\}$', expr)
        if not path_match:
            return ResolutionResult(value=expr, resolved=False, error="无效表达式格式")

        path = path_match.group(1)
        parts = path.split(".")

        if not parts:
            return ResolutionResult(value=expr, resolved=False, error="空路径")

        # 数据引用
        if parts[0] == "data":
            result = self._resolve_data(parts[1:])
            if result is not None:
                return ResolutionResult(value=result, source=f"data.{'.'.join(parts[1:])}")
            return ResolutionResult(value=None, resolved=False,
                                    error=f"数据路径不存在: {path}")

        # 变量引用
        if parts[0] == "var":
            var_name = parts[1] if len(parts) > 1 else ""
            if var_name in self._variables:
                return ResolutionResult(
                    value=self._variables[var_name],
                    source=f"var.{var_name}",
                )
            return ResolutionResult(value=None, resolved=False,
                                    error=f"变量不存在: {var_name}")

        # 样式引用
        if parts[0] == "style":
            style_name = parts[1] if len(parts) > 1 else ""
            if style_name in self._style_map:
                return ResolutionResult(
                    value=self._style_map[style_name],
                    source=f"style.{style_name}",
                )
            return ResolutionResult(value=None, resolved=False,
                                    error=f"样式不存在: {style_name}")

        return ResolutionResult(value=expr, resolved=False, error=f"未知引用类型: {parts[0]}")

    def _resolve_data(self, path: list[str]) -> Any:
        """解析数据路径"""
        current = self._data_context
        for part in path:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def resolve_node_references(self, node: IRNode) -> dict[str, ResolutionResult]:
        """解析节点中的所有引用

        Args:
            node: IR 节点

        Returns:
            属性名 → 解析结果 的映射
        """
        results = {}

        # 解析文本内容中的引用
        if node.content and isinstance(node.content, str):
            if "${" in node.content:
                results["content"] = self.resolve_expression(node.content)

        # 解析样式引用
        if node.style_ref:
            results["style_ref"] = self.resolve_expression(f"${{style.{node.style_ref}}}")

        # 解析数据源引用
        if node.data_ref:
            results["data_ref"] = self.resolve_expression(f"${{data.{node.data_ref}}}")

        return results

    def resolve_all(self, doc: IRDocument | None = None) -> dict[str, list[ResolutionResult]]:
        """解析文档中的所有引用

        Returns:
            节点路径 → 解析结果列表
        """
        if doc:
            self.set_document(doc)
        if not self._document:
            return {}

        all_results: dict[str, list[ResolutionResult]] = {}
        self._walk_and_resolve(self._document.root, "", all_results)
        return all_results

    def _walk_and_resolve(
        self, node: IRNode, path: str,
        results: dict[str, list[ResolutionResult]],
    ) -> None:
        """递归遍历并解析"""
        current_path = f"{path}/{node.node_type.value}"
        node_results = self.resolve_node_references(node)
        if node_results:
            results[current_path] = list(node_results.values())

        for child in node.children:
            self._walk_and_resolve(child, current_path, results)
