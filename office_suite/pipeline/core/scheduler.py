"""流水线调度器 — 拓扑排序 + 顺序/并行执行

设计方案第六章：
  声明依赖关系 → 自动拓扑排序 → 并行调度 → 汇聚输出
"""

import threading
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
        self._lock = threading.Lock()

    def run(self) -> dict[str, Any]:
        """执行整个流水线

        流程：
        1. 校验 DAG
        2. 拓扑排序
        3. 按层执行（同层可并行）
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

    def run_parallel(self) -> dict[str, Any]:
        """并行执行流水线

        同层级节点并发执行，跨层级顺序执行。
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        errors = self.graph.validate()
        if errors:
            raise ValueError(f"DAG 校验失败: {errors}")

        levels = self.graph.get_parallel_levels()
        self.context.log(f"并行层级: {len(levels)} 层")

        max_workers = self.graph.config.get("parallelism", 4)

        for level_idx, level in enumerate(levels):
            self.context.log(f"[Layer {level_idx}] 节点: {level}")

            if len(level) == 1:
                self._run_single_node(level[0])
            else:
                with ThreadPoolExecutor(max_workers=max_workers) as pool:
                    futures = {
                        pool.submit(self._run_single_node, name): name
                        for name in level
                    }
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as exc:
                            node_name = futures[future]
                            with self._lock:
                                node = self.graph.get_node(node_name)
                                if node:
                                    node.error = str(exc)
                                    node.status = NodeStatus.FAILED
                                self.context.log(f"[FAIL] {node_name}: {exc}")

            if self._should_stop():
                break

        return self._collect_results()

    def _run_single_node(self, node_name: str):
        """执行单个节点（供并行调度使用）"""
        node = self.graph.get_node(node_name)
        if node is None:
            return

        if not self._deps_satisfied(node):
            with self._lock:
                node.status = NodeStatus.SKIPPED
                self.context.log(f"[SKIP] {node_name}: 依赖未满足")
            return

        with self._lock:
            node.status = NodeStatus.RUNNING
            self.context.log(f"[RUN]  {node_name} ({node.node_type})")

        try:
            result = self._execute_node(node)
            with self._lock:
                node.result = result
                node.status = NodeStatus.SUCCESS
                self.context.set_output(node_name, result)
                self.context.log(f"[OK]   {node_name}")
        except Exception as e:
            with self._lock:
                node.error = str(e)
                node.status = NodeStatus.FAILED
                self.context.log(f"[FAIL] {node_name}: {e}")

    def _should_stop(self) -> bool:
        """检查是否需要停止执行"""
        if self.graph.config.get("fail_fast"):
            with self._lock:
                return any(
                    n.status == NodeStatus.FAILED
                    for n in self.graph.nodes.values()
                )
        return False

    def _deps_satisfied(self, node: PipelineNode) -> bool:
        """检查节点的所有依赖是否都已成功"""
        for dep_name in node.depends_on:
            dep_node = self.graph.get_node(dep_name)
            if dep_node is None or dep_node.status != NodeStatus.SUCCESS:
                return False
        return True

    def _execute_node(self, node: PipelineNode) -> Any:
        """执行单个节点

        优先级：
        1. 节点自带的 executor 函数（向后兼容）
        2. 注册表中的 NodeExecutor
        3. 兜底：简单变量解析
        """
        if node.executor:
            return node.executor(node.params, self.context)

        # 从注册表查找
        from ..nodes.base import get_handler
        handler = get_handler(node.node_type)
        if handler:
            return handler.execute(node.params, self.context)

        raise ValueError(f"未知节点类型 '{node.node_type}' 且无 executor")

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
