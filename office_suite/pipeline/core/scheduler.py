"""流水线调度器 — 拓扑排序 + 顺序执行

设计方案第六章：
  声明依赖关系 → 自动拓扑排序 → 并行调度 → 汇聚输出

当前实现为顺序执行（单线程），
并行调度留给后续迭代（concurrent.futures）。
"""

from typing import Any
from .graph import PipelineGraph, PipelineNode, NodeStatus
from .context import PipelineContext


class PipelineScheduler:
    """流水线调度器

    使用示例：
        scheduler = PipelineScheduler(graph, context)
        results = scheduler.run()
    """

    def __init__(self, graph: PipelineGraph, context: PipelineContext | None = None):
        self.graph = graph
        self.context = context or PipelineContext()

    def run(self) -> dict[str, Any]:
        """执行整个流水线

        流程：
        1. 校验 DAG
        2. 拓扑排序
        3. 按顺序执行每个节点
        4. 收集结果
        """
        # 校验
        errors = self.graph.validate()
        if errors:
            raise ValueError(f"DAG 校验失败: {errors}")

        # 拓扑排序
        order = self.graph.topological_sort()
        self.context.log(f"执行顺序: {order}")

        # 逐节点执行
        for node_name in order:
            node = self.graph.get_node(node_name)
            if node is None:
                continue

            # 检查依赖是否都成功
            if not self._deps_satisfied(node):
                node.status = NodeStatus.SKIPPED
                self.context.log(f"[SKIP] {node_name}: 依赖未满足")
                continue

            # 执行节点
            node.status = NodeStatus.RUNNING
            self.context.log(f"[RUN]  {node_name} ({node.node_type})")

            try:
                result = self._execute_node(node)
                node.result = result
                node.status = NodeStatus.SUCCESS
                self.context.set_output(node_name, result)
                self.context.log(f"[OK]   {node_name}")
            except Exception as e:
                node.error = str(e)
                node.status = NodeStatus.FAILED
                self.context.log(f"[FAIL] {node_name}: {e}")

            # 如果有节点失败且配置了 fail_fast，则停止
            if node.status == NodeStatus.FAILED and self.graph.config.get("fail_fast"):
                self.context.log("fail_fast=True，停止执行")
                break

        return self._collect_results()

    def _deps_satisfied(self, node: PipelineNode) -> bool:
        """检查节点的所有依赖是否都已成功"""
        for dep_name in node.depends_on:
            dep_node = self.graph.get_node(dep_name)
            if dep_node is None or dep_node.status != NodeStatus.SUCCESS:
                return False
        return True

    def _execute_node(self, node: PipelineNode) -> Any:
        """执行单个节点

        如果节点有 executor 函数，调用它。
        否则使用内置的节点类型处理器。
        """
        if node.executor:
            return node.executor(node.params, self.context)

        # 内置处理器
        handler = self._get_handler(node.node_type)
        if handler:
            return handler(node, self.context)

        raise ValueError(f"未知节点类型 '{node.node_type}' 且无 executor")

    def _get_handler(self, node_type: str):
        """获取节点类型对应的内置处理器"""
        handlers = {
            "fetch": self._handle_fetch,
            "transform": self._handle_transform,
            "condition": self._handle_condition,
        }
        return handlers.get(node_type)

    def _handle_fetch(self, node: PipelineNode, ctx: PipelineContext) -> Any:
        """处理 fetch 节点 — 从数据源获取数据"""
        source = node.params.get("source", "")
        # 解析变量引用
        if isinstance(source, str) and source.startswith("${"):
            ref = source[2:-1]
            source = ctx.resolve_ref(ref)
        return {"source": source, "status": "fetched"}

    def _handle_transform(self, node: PipelineNode, ctx: PipelineContext) -> Any:
        """处理 transform 节点 — 数据转换"""
        input_ref = node.params.get("input", "")
        if isinstance(input_ref, str) and input_ref.startswith("${"):
            ref = input_ref[2:-1]
            data = ctx.resolve_ref(ref)
        else:
            data = input_ref
        return {"transformed": data}

    def _handle_condition(self, node: PipelineNode, ctx: PipelineContext) -> Any:
        """处理 condition 节点 — 条件分支"""
        condition = node.params.get("condition", True)
        if isinstance(condition, str) and condition.startswith("${"):
            ref = condition[2:-1]
            condition = bool(ctx.resolve_ref(ref))
        return {"condition": bool(condition)}

    def _collect_results(self) -> dict[str, Any]:
        """收集所有节点的结果"""
        results = {}
        for name, node in self.graph.nodes.items():
            results[name] = {
                "status": node.status.value,
                "result": node.result,
                "error": node.error,
            }
        return results
