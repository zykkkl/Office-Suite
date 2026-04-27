"""流水线执行上下文 — 节点间共享数据的传递媒介"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from office_suite.hub.resolver import ResourceResolver


@dataclass
class PipelineContext:
    """流水线执行上下文

    每个节点执行后将结果存入 outputs，
    下游节点通过 node_name.output_key 访问。
    """
    # 变量（DSL 中的 vars）
    variables: dict[str, Any] = field(default_factory=dict)
    # 节点输出
    outputs: dict[str, Any] = field(default_factory=dict)
    # 工作目录
    work_dir: Path = field(default_factory=lambda: Path.cwd())
    # 输出目录
    output_dir: Path = field(default_factory=lambda: Path.cwd() / "output")
    # 运行时日志
    logs: list[str] = field(default_factory=list)
    # 共享资源解析器（跨节点复用 LRU 缓存）
    resource_resolver: Any = field(default=None)

    def get_resource_resolver(self) -> "ResourceResolver":
        """获取（或懒初始化）共享 ResourceResolver"""
        if self.resource_resolver is None:
            from office_suite.hub.resolver import ResourceResolver
            self.resource_resolver = ResourceResolver()
        return self.resource_resolver

    def set_output(self, node_name: str, value: Any):
        """设置节点输出"""
        self.outputs[node_name] = value

    def get_output(self, node_name: str, default: Any = None) -> Any:
        """获取节点输出"""
        return self.outputs.get(node_name, default)

    def resolve_ref(self, ref: str) -> Any:
        """解析引用表达式，如 'fetch_data.output' 或 'vars.topic'"""
        if ref.startswith("vars."):
            key = ref[5:]
            return self.variables.get(key)
        parts = ref.split(".", 1)
        node_name = parts[0]
        output = self.outputs.get(node_name)
        if len(parts) > 1 and isinstance(output, dict):
            return output.get(parts[1])
        return output

    def log(self, message: str):
        """添加日志"""
        self.logs.append(message)
