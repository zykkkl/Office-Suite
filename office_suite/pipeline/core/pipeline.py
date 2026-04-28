"""流水线 Facade — 统一入口

将 parser + scheduler + history_store 三层胶合为一个对象，
调用方只需：

    pipe = Pipeline.from_yaml(yaml_str)
    result = pipe.run(variables={"topic": "Q4报告"})

或从文件加载：

    pipe = Pipeline.from_file("pipelines/report.yaml")
    result = pipe.run(parallel=True)

设计方案第六章：声明式 DAG 编排的顶层入口。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .graph import PipelineGraph, NodeStatus
from .context import PipelineContext
from .scheduler import PipelineScheduler
from ..parser import parse_pipeline_string, parse_pipeline_file


# ---------------------------------------------------------------------------
# 结果数据类
# ---------------------------------------------------------------------------

@dataclass
class NodeResult:
    """单个节点的执行结果"""
    name: str
    status: str          # pending / running / success / failed / skipped
    result: Any = None
    error: str = ""
    duration: float = 0.0


@dataclass
class PipelineResult:
    """流水线整体执行结果

    属性：
        pipeline_name   流水线名称
        success         是否全部节点成功（无 failed 节点）
        nodes           各节点结果列表
        outputs         节点输出字典（node_name → result）
        logs            执行日志列表
        duration        总耗时（秒）
        failed_nodes    失败节点名称列表
    """
    pipeline_name: str
    success: bool
    nodes: list[NodeResult] = field(default_factory=list)
    outputs: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)
    duration: float = 0.0
    failed_nodes: list[str] = field(default_factory=list)

    def get(self, node_name: str, key: str | None = None, default: Any = None) -> Any:
        """快捷访问节点输出

        用法：
            result.get("fetch_data")              # 获取整个输出
            result.get("fetch_data", "rows")      # 获取输出中的 rows 字段
        """
        output = self.outputs.get(node_name, default)
        if key is not None and isinstance(output, dict):
            return output.get(key, default)
        return output

    def raise_on_failure(self) -> "PipelineResult":
        """如果有节点失败则抛出异常，否则返回 self（支持链式调用）"""
        if not self.success:
            errors = [
                f"  {n.name}: {n.error}"
                for n in self.nodes
                if n.status == "failed"
            ]
            raise RuntimeError(
                f"流水线 '{self.pipeline_name}' 执行失败，"
                f"失败节点:\n" + "\n".join(errors)
            )
        return self


# ---------------------------------------------------------------------------
# Pipeline Facade
# ---------------------------------------------------------------------------

class Pipeline:
    """流水线 Facade

    统一入口，封装 parser → scheduler → history_store 三层。

    使用示例：
        # 从 YAML 字符串
        pipe = Pipeline.from_yaml(yaml_str)
        result = pipe.run(variables={"topic": "Q4报告"})

        # 从文件
        pipe = Pipeline.from_file("pipelines/report.yaml")
        result = pipe.run(parallel=True)

        # 链式调用（失败时抛异常）
        outputs = Pipeline.from_yaml(yaml_str).run().raise_on_failure().outputs
    """

    def __init__(self, graph: PipelineGraph):
        self._graph = graph

    # ------------------------------------------------------------------
    # 工厂方法
    # ------------------------------------------------------------------

    @classmethod
    def from_yaml(
        cls,
        yaml_str: str,
        variables: dict[str, Any] | None = None,
    ) -> "Pipeline":
        """从 YAML 字符串构建流水线

        Args:
            yaml_str:   DSL YAML 字符串
            variables:  运行时变量（覆盖 DSL 中的 vars）
        """
        graph = parse_pipeline_string(yaml_str)
        pipe = cls(graph)
        if variables:
            pipe._default_variables = variables
        return pipe

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        variables: dict[str, Any] | None = None,
    ) -> "Pipeline":
        """从 YAML 文件构建流水线

        Args:
            path:       YAML 文件路径
            variables:  运行时变量（覆盖 DSL 中的 vars）
        """
        graph = parse_pipeline_file(path)
        pipe = cls(graph)
        if variables:
            pipe._default_variables = variables
        return pipe

    # ------------------------------------------------------------------
    # 执行
    # ------------------------------------------------------------------

    def run(
        self,
        *,
        parallel: bool = False,
        variables: dict[str, Any] | None = None,
        work_dir: str | Path | None = None,
        output_dir: str | Path | None = None,
        history_dir: str | Path | None = None,
        record_history: bool = True,
    ) -> PipelineResult:
        """执行流水线

        Args:
            parallel:       True 则按层并行执行，False 则顺序执行
            variables:      运行时变量（合并到 context.variables）
            work_dir:       工作目录（默认 cwd）
            output_dir:     输出目录（默认 cwd/output）
            history_dir:    历史记录目录（默认 ./history，None 则不记录）
            record_history: 是否写入历史记录（默认 True）

        Returns:
            PipelineResult
        """
        # 合并变量：DSL 默认变量 < 调用时传入变量
        merged_vars: dict[str, Any] = {}
        merged_vars.update(getattr(self, "_default_variables", {}))
        if variables:
            merged_vars.update(variables)

        # 构建上下文
        ctx_kwargs: dict[str, Any] = {"variables": merged_vars}
        if work_dir is not None:
            ctx_kwargs["work_dir"] = Path(work_dir)
        if output_dir is not None:
            ctx_kwargs["output_dir"] = Path(output_dir)
        context = PipelineContext(**ctx_kwargs)

        # 调度器
        scheduler = PipelineScheduler(self._graph, context)

        # 历史记录
        history = None
        if record_history:
            try:
                from ..store.history_store import HistoryStore
                _hdir = history_dir or "./history"
                history = HistoryStore(base_dir=_hdir)
                history.record_start(
                    self._graph.name or "unnamed",
                    config=self._graph.config,
                )
            except Exception:
                # 历史记录失败不应阻断主流程
                history = None

        # 执行
        t0 = time.monotonic()
        try:
            if parallel:
                raw_results = scheduler.run_parallel()
            else:
                raw_results = scheduler.run()
        finally:
            duration = time.monotonic() - t0

        # 整理结果
        node_results: list[NodeResult] = []
        failed_nodes: list[str] = []

        for name, info in raw_results.items():
            status = info.get("status", "pending")
            nr = NodeResult(
                name=name,
                status=status,
                result=info.get("result"),
                error=info.get("error", ""),
            )
            node_results.append(nr)
            if status == "failed":
                failed_nodes.append(name)

            # 写入历史
            if history is not None:
                try:
                    history.record_node(
                        node_name=name,
                        status=status,
                        duration=0.0,   # 单节点耗时暂未追踪
                        error=info.get("error") or None,
                    )
                except Exception:
                    pass

        success = len(failed_nodes) == 0

        # 完成历史记录
        if history is not None:
            try:
                history.record_finish(status="completed" if success else "failed")
            except Exception:
                pass

        return PipelineResult(
            pipeline_name=self._graph.name or "unnamed",
            success=success,
            nodes=node_results,
            outputs=dict(context.outputs),
            logs=list(context.logs),
            duration=duration,
            failed_nodes=failed_nodes,
        )

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._graph.name

    @property
    def graph(self) -> PipelineGraph:
        return self._graph

    def validate(self) -> list[str]:
        """校验 DAG 合法性，返回错误列表（空列表表示合法）"""
        return self._graph.validate()

    def node_names(self) -> list[str]:
        """返回所有节点名称（拓扑排序）"""
        return self._graph.topological_sort()

    def __repr__(self) -> str:
        n = len(self._graph.nodes)
        return f"Pipeline(name={self._graph.name!r}, nodes={n})"
