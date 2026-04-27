"""IR 增强校验器 — 包含约束、属性约束、坐标合理性检查

校验规则分类（共 6 类）：
  1. structure  — 文档结构（幻灯片数量、版本号）
  2. containment — 父子节点包含约束（CONTAINMENT_RULES）
  3. required_props — 必需属性（TEXT 需 content, IMAGE 需 source 等）
  4. position — 坐标合理性（负宽高、超出边界）
  5. style — 样式合理性（font_size 范围、opacity 0-1）
  6. leaf_constraint — 叶子节点不应有子节点

严重级别：
  ERROR   — 必须修复，否则渲染结果不正确
  WARNING — 建议修复，渲染可能有问题
  INFO    — 仅供参考

架构位置：renderer/pptx/deck.py 在渲染前调用 validate_ir_v2()
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .types import (
    CONTAINMENT_RULES,
    IRDocument,
    IRNode,
    IRPosition,
    IRStyle,
    LEAF_NODES,
    NodeType,
    REQUIRED_PROPS,
)


class Severity(Enum):
    """校验结果严重级别"""
    ERROR = "error"      # 必须修复
    WARNING = "warning"  # 建议修复
    INFO = "info"        # 仅供参考


@dataclass
class ValidationIssue:
    """单条校验问题"""
    severity: Severity
    message: str
    path: str = ""       # 节点路径
    node_type: str = ""  # 节点类型名
    rule: str = ""       # 规则名称

    def __str__(self):
        prefix = f"[{self.severity.value.upper()}]"
        path_part = f" {self.path}" if self.path else ""
        return f"{prefix}{path_part}: {self.message}"


@dataclass
class ValidationResult:
    """校验结果汇总"""
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add(self, severity: Severity, message: str, **kwargs):
        self.issues.append(ValidationIssue(severity=severity, message=message, **kwargs))

    def __str__(self):
        lines = [f"Validation: {'PASS' if self.is_valid else 'FAIL'}"]
        lines.append(f"  Errors: {len(self.errors)}, Warnings: {len(self.warnings)}")
        for issue in self.issues:
            lines.append(f"  {issue}")
        return "\n".join(lines)


class IRValidator:
    """IR 文档校验器"""

    def __init__(self, doc: IRDocument):
        self.doc = doc
        self.result = ValidationResult()

    def validate(self) -> ValidationResult:
        """执行全部校验"""
        self._validate_structure()
        self._validate_styles()
        for i, slide in enumerate(self.doc.children):
            self._validate_node(slide, NodeType.DOCUMENT, f"slide[{i}]")
        return self.result

    def _validate_structure(self):
        """校验文档结构"""
        if not self.doc.children:
            self.result.add(Severity.WARNING, "文档无幻灯片/节", rule="structure")
        if not self.doc.version:
            self.result.add(Severity.WARNING, "缺少版本号", rule="structure")

    def _validate_styles(self):
        """校验全局样式表"""
        for name, style in self.doc.styles.items():
            if style.font_size is not None and style.font_size < 0:
                self.result.add(Severity.ERROR, f"样式 '{name}' font_size 为负值", rule="style")
            if style.font_weight is not None and (style.font_weight < 100 or style.font_weight > 900):
                self.result.add(Severity.WARNING, f"样式 '{name}' font_weight 超出 100-900 范围", rule="style")

    def _validate_node(self, node: IRNode, parent_type: NodeType | None, path: str):
        """校验单个节点"""
        self._check_containment(node, parent_type, path)
        self._check_required_props(node, path)
        self._check_position(node, path)
        self._check_style(node, path)
        self._check_leaf_constraint(node, path)

        for i, child in enumerate(node.children):
            child_path = f"{path}/{child.node_type.value}[{i}]"
            self._validate_node(child, node.node_type, child_path)

    def _check_containment(self, node: IRNode, parent_type: NodeType | None, path: str):
        """校验包含约束"""
        if parent_type is None:
            return
        allowed = CONTAINMENT_RULES.get(parent_type)
        if allowed is None:
            self.result.add(
                Severity.ERROR,
                f"{parent_type.value} 不可包含任何子节点，但发现了 {node.node_type.value}",
                path=path, node_type=node.node_type.value, rule="containment",
            )
        elif node.node_type not in allowed:
            self.result.add(
                Severity.ERROR,
                f"{parent_type.value} 不可包含 {node.node_type.value}",
                path=path, node_type=node.node_type.value, rule="containment",
            )

    def _check_required_props(self, node: IRNode, path: str):
        """校验必需属性"""
        required = REQUIRED_PROPS.get(node.node_type, [])
        for prop in required:
            if prop == "content" and (not node.content or node.content.strip() == ""):
                self.result.add(
                    Severity.ERROR,
                    f"{node.node_type.value} 缺少必需属性 'content'",
                    path=path, node_type=node.node_type.value, rule="required_props",
                )
            elif prop == "source" and not node.source:
                self.result.add(
                    Severity.ERROR,
                    f"{node.node_type.value} 缺少必需属性 'source'",
                    path=path, node_type=node.node_type.value, rule="required_props",
                )
            elif prop == "chart_type" and not node.chart_type:
                self.result.add(
                    Severity.ERROR,
                    f"{node.node_type.value} 缺少必需属性 'chart_type'",
                    path=path, node_type=node.node_type.value, rule="required_props",
                )

    def _check_position(self, node: IRNode, path: str):
        """校验位置合理性"""
        if node.position is None:
            return
        pos = node.position
        if pos.width_mm < 0:
            self.result.add(Severity.ERROR, f"宽度为负值 ({pos.width_mm}mm)", path=path, rule="position")
        if pos.height_mm < 0:
            self.result.add(Severity.ERROR, f"高度为负值 ({pos.height_mm}mm)", path=path, rule="position")
        if pos.x_mm < -50:  # 允许少量负偏移
            self.result.add(Severity.WARNING, f"x 坐标严重偏左 ({pos.x_mm}mm)", path=path, rule="position")
        if pos.y_mm < -50:
            self.result.add(Severity.WARNING, f"y 坐标严重偏上 ({pos.y_mm}mm)", path=path, rule="position")
        # 检查是否超出幻灯片边界（16:9 标准）
        if pos.x_mm + pos.width_mm > 300:  # 留些余量
            self.result.add(Severity.WARNING, f"元素可能超出右边界", path=path, rule="position")
        if pos.y_mm + pos.height_mm > 250:
            self.result.add(Severity.WARNING, f"元素可能超出下边界", path=path, rule="position")

    def _check_style(self, node: IRNode, path: str):
        """校验样式合理性"""
        if node.style is None:
            return
        s = node.style
        if s.font_size is not None and s.font_size <= 0:
            self.result.add(Severity.ERROR, f"font_size 必须 > 0 (当前: {s.font_size})", path=path, rule="style")
        if s.font_size is not None and s.font_size > 200:
            self.result.add(Severity.WARNING, f"font_size 过大 ({s.font_size}pt)", path=path, rule="style")
        if s.fill_opacity is not None and (s.fill_opacity < 0 or s.fill_opacity > 1):
            self.result.add(Severity.ERROR, f"fill_opacity 必须在 0-1 之间 (当前: {s.fill_opacity})", path=path, rule="style")

    def _check_leaf_constraint(self, node: IRNode, path: str):
        """叶子节点不应有子节点"""
        if node.node_type in LEAF_NODES and node.children:
            self.result.add(
                Severity.ERROR,
                f"{node.node_type.value} 是叶子节点，不应有 {len(node.children)} 个子节点",
                path=path, node_type=node.node_type.value, rule="leaf_constraint",
            )


def validate_ir_v2(doc: IRDocument) -> ValidationResult:
    """增强版 IR 校验入口"""
    validator = IRValidator(doc)
    return validator.validate()
