"""IR 节点类型系统 — 核心中间表示层

类比 LLVM IR：所有设计意图最终编译为 IR 节点，再由渲染器后端输出。

架构位置：dsl/parser.py → ir/compiler.py → [本文件] → renderer/*/deck.py
数据流：YAML DSL → Document 对象 → IRDocument 树 → 各格式渲染器

核心设计决策：
- NodeType 枚举定义了所有合法节点，分为容器节点和叶子节点
- CONTAINMENT_RULES 定义父子包含关系，渲染前校验防止非法嵌套
- IRStyle 所有字段 Optional(None)，级联时只覆盖非 None 字段
- IRNode.source_path 保留 DSL 原始路径，便于调试和错误定位
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class NodeType(Enum):
    """IR 节点类型枚举"""
    # 容器节点
    DOCUMENT = "document"
    SLIDE = "slide"
    SECTION = "section"
    GROUP = "group"

    # 内容节点（P0）
    TEXT = "text"
    IMAGE = "image"
    SHAPE = "shape"
    TABLE = "table"
    CHART = "chart"

    # 内容节点（P1+）
    VIDEO = "video"
    AUDIO = "audio"
    DIAGRAM = "diagram"
    CODE = "code"

    # 内容节点（P2/P3）
    MODEL_3D = "3d_model"
    MAP = "map"


# 包含约束：哪些节点可以包含哪些子节点
# 设计意图：在 IR 层面就拦截非法嵌套（如 TEXT 内包含 SLIDE），
# 而不是等到渲染器报错。这和 TypeScript 的类型系统思路一致。
CONTAINMENT_RULES: dict[NodeType, set[NodeType]] = {
    NodeType.DOCUMENT: {NodeType.SLIDE, NodeType.SECTION},
    NodeType.SECTION: {NodeType.SLIDE},
    NodeType.SLIDE: {
        NodeType.SHAPE, NodeType.TEXT, NodeType.IMAGE,
        NodeType.CHART, NodeType.TABLE, NodeType.GROUP,
        NodeType.VIDEO, NodeType.DIAGRAM, NodeType.CODE,
    },
    NodeType.GROUP: {
        NodeType.SHAPE, NodeType.TEXT, NodeType.IMAGE,
        NodeType.CHART, NodeType.TABLE, NodeType.DIAGRAM,
    },
}

# 叶子节点：不可包含子节点
LEAF_NODES = {
    NodeType.TEXT, NodeType.IMAGE, NodeType.SHAPE,
    NodeType.TABLE, NodeType.CHART, NodeType.VIDEO,
    NodeType.AUDIO, NodeType.DIAGRAM, NodeType.CODE,
    NodeType.MODEL_3D, NodeType.MAP,
}

# 必需属性约束
REQUIRED_PROPS: dict[NodeType, list[str]] = {
    NodeType.TEXT: ["content"],
    NodeType.IMAGE: ["source"],
    NodeType.CHART: ["chart_type"],
    NodeType.TABLE: [],  # data_ref 或 inline data 均可
    NodeType.SLIDE: ["layout"],
}


class ValidationError(Exception):
    """IR 校验错误"""
    pass


def validate_containment(parent_type: NodeType, child_type: NodeType) -> bool:
    """校验父子节点的包含关系是否合法"""
    allowed = CONTAINMENT_RULES.get(parent_type)
    if allowed is None:
        return False  # 该节点类型不可包含任何子节点
    return child_type in allowed


def validate_node_type(node_type_str: str) -> NodeType:
    """将字符串转换为 NodeType，无效则抛出 ValidationError"""
    try:
        return NodeType(node_type_str)
    except ValueError:
        valid = [e.value for e in NodeType]
        raise ValidationError(
            f"未知节点类型 '{node_type_str}'，合法类型: {valid}"
        )


# ============================================================
# IR 节点数据结构
# ============================================================


@dataclass
class IRPosition:
    """IR 位置 — 绝对坐标（mm）"""
    x_mm: float = 0.0
    y_mm: float = 0.0
    width_mm: float = 0.0
    height_mm: float = 0.0
    # 标记
    is_relative: bool = False  # 原始值是否为百分比
    is_center: bool = False
    is_auto: bool = False  # 尺寸自动计算


@dataclass
class IRStyle:
    """IR 样式 — 渲染器无关的样式描述

    所有字段默认 None 表示"未设置"，级联时只覆盖非 None 字段。
    最终渲染前需由渲染器或级联引擎填入实际值。
    """
    font_family: str | None = None
    font_size: int | None = None  # pt
    font_weight: int | None = None
    font_italic: bool | None = None
    font_color: str | None = None
    fill_color: str | None = None
    fill_gradient: dict[str, Any] | None = None
    fill_opacity: float | None = None
    shadow: dict[str, Any] | None = None
    border: dict[str, Any] | None = None
    text_effect: dict[str, Any] | None = None
    # 主题引用
    theme_ref: str | None = None


@dataclass
class IRNode:
    """IR 基础节点"""
    node_type: NodeType
    id: str = ""
    # 内容
    content: str | None = None
    source: str | dict | None = None
    # 布局
    position: IRPosition | None = None
    # 样式
    style: IRStyle | None = None
    style_ref: str | None = None  # 引用全局样式名
    # 子节点
    children: list["IRNode"] = field(default_factory=list)
    # 数据绑定
    data_ref: str | None = None
    chart_type: str | None = None
    # 额外属性
    extra: dict[str, Any] = field(default_factory=dict)
    # 原始 DSL 路径（调试用）
    source_path: str = ""


@dataclass
class IRDocument:
    """IR 文档根节点"""
    version: str = "4.0"
    doc_type: str = "presentation"
    theme: str = "default"
    title: str = ""
    # 全局样式表
    styles: dict[str, IRStyle] = field(default_factory=dict)
    # 全局数据
    data: dict[str, Any] = field(default_factory=dict)
    # 子节点（slides / sections）
    children: list[IRNode] = field(default_factory=list)
    # 原始 DSL
    raw_dsl: dict[str, Any] = field(default_factory=dict)


def validate_ir(doc: IRDocument) -> list[str]:
    """校验 IR 文档，返回警告列表（空表示无问题）"""
    warnings = []

    def _validate_node(node: IRNode, parent_type: NodeType | None, path: str):
        # 校验包含约束
        if parent_type is not None:
            if not validate_containment(parent_type, node.node_type):
                warnings.append(
                    f"{path}: {parent_type.value} 不可包含 {node.node_type.value}"
                )
        # 校验必需属性
        required = REQUIRED_PROPS.get(node.node_type, [])
        for prop in required:
            if prop == "content" and not node.content:
                warnings.append(f"{path}: {node.node_type.value} 缺少必需属性 'content'")
            elif prop == "source" and not node.source:
                warnings.append(f"{path}: {node.node_type.value} 缺少必需属性 'source'")
            elif prop == "chart_type" and not node.chart_type:
                warnings.append(f"{path}: {node.node_type.value} 缺少必需属性 'chart_type'")
        # 递归子节点
        for i, child in enumerate(node.children):
            _validate_node(child, node.node_type, f"{path}/{child.node_type.value}[{i}]")

    for i, slide in enumerate(doc.children):
        _validate_node(slide, NodeType.DOCUMENT, f"slide[{i}]")

    return warnings
