"""流水线 DSL 解析器 — YAML → PipelineGraph"""

from typing import Any
from pathlib import Path

import yaml

from office_suite.dsl.parser import safe_yaml_load
from .core.graph import PipelineGraph, PipelineNode


def parse_pipeline_yaml(raw: dict[str, Any]) -> PipelineGraph:
    """解析流水线 YAML 为 PipelineGraph

    DSL 格式（设计方案第六章）：
        name: "流水线名称"
        config:
          timeout: 600s
          retry: { max: 3, backoff: exponential }
        graph:
          node_name:
            type: fetch | transform | render | ...
            depends_on: [other_node]
            params: { key: value }
    """
    graph = PipelineGraph(
        name=raw.get("name", ""),
        config=raw.get("config", {}),
    )

    nodes_raw = raw.get("graph", {})
    for node_name, node_def in nodes_raw.items():
        if isinstance(node_def, dict):
            node = PipelineNode(
                name=node_name,
                node_type=node_def.get("type", ""),
                depends_on=node_def.get("depends_on", []),
                params=node_def.get("params", {}),
            )
            graph.add_node(node)

    return graph


def parse_pipeline_file(path: str | Path) -> PipelineGraph:
    """从 YAML 文件解析流水线"""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        raw = safe_yaml_load(f.read())
    return parse_pipeline_yaml(raw)


def parse_pipeline_string(yaml_str: str) -> PipelineGraph:
    """从 YAML 字符串解析流水线"""
    raw = safe_yaml_load(yaml_str)
    return parse_pipeline_yaml(raw)
