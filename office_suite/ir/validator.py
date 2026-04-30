"""IR validation for Office Suite documents."""

from dataclasses import dataclass, field
from enum import Enum

from .types import (
    CONTAINMENT_RULES,
    IRDocument,
    IRNode,
    LEAF_NODES,
    NodeType,
    REQUIRED_PROPS,
)


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    severity: Severity
    message: str
    path: str = ""
    node_type: str = ""
    rule: str = ""

    def __str__(self):
        prefix = f"[{self.severity.value.upper()}]"
        path_part = f" {self.path}" if self.path else ""
        return f"{prefix}{path_part}: {self.message}"


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == Severity.WARNING]

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def add(self, severity: Severity, message: str, **kwargs):
        self.issues.append(ValidationIssue(severity=severity, message=message, **kwargs))

    def __str__(self):
        lines = [f"Validation: {'PASS' if self.is_valid else 'FAIL'}"]
        lines.append(f"  Errors: {len(self.errors)}, Warnings: {len(self.warnings)}")
        for issue in self.issues:
            lines.append(f"  {issue}")
        return "\n".join(lines)


class IRValidator:
    def __init__(self, doc: IRDocument):
        self.doc = doc
        self.result = ValidationResult()

    def validate(self) -> ValidationResult:
        self._validate_structure()
        self._validate_styles()
        for index, slide in enumerate(self.doc.children):
            self._validate_node(slide, NodeType.DOCUMENT, f"slide[{index}]")
        return self.result

    def _validate_structure(self):
        if not self.doc.children:
            self.result.add(Severity.WARNING, "Document has no slides or sections", rule="structure")
        if not self.doc.version:
            self.result.add(Severity.WARNING, "Document is missing version", rule="structure")

    def _validate_styles(self):
        for name, style in self.doc.styles.items():
            if style.font_size is not None and style.font_size < 0:
                self.result.add(Severity.ERROR, f"Style '{name}' has negative font_size", rule="style")
            if style.font_weight is not None and (style.font_weight < 100 or style.font_weight > 900):
                self.result.add(
                    Severity.WARNING,
                    f"Style '{name}' font_weight is outside 100-900",
                    rule="style",
                )

    def _validate_node(self, node: IRNode, parent_type: NodeType | None, path: str):
        self._check_containment(node, parent_type, path)
        self._check_required_props(node, path)
        self._check_semantic_icon(node, path)
        self._check_position(node, path)
        self._check_style(node, path)
        self._check_leaf_constraint(node, path)

        for index, child in enumerate(node.children):
            child_path = f"{path}/{child.node_type.value}[{index}]"
            self._validate_node(child, node.node_type, child_path)

    def _check_containment(self, node: IRNode, parent_type: NodeType | None, path: str):
        if parent_type is None:
            return
        allowed = CONTAINMENT_RULES.get(parent_type)
        if allowed is None:
            self.result.add(
                Severity.ERROR,
                f"{parent_type.value} cannot contain child nodes, found {node.node_type.value}",
                path=path,
                node_type=node.node_type.value,
                rule="containment",
            )
        elif node.node_type not in allowed:
            self.result.add(
                Severity.ERROR,
                f"{parent_type.value} cannot contain {node.node_type.value}",
                path=path,
                node_type=node.node_type.value,
                rule="containment",
            )

    def _check_required_props(self, node: IRNode, path: str):
        required = REQUIRED_PROPS.get(node.node_type, [])
        for prop in required:
            if prop == "content" and (not node.content or node.content.strip() == ""):
                self.result.add(
                    Severity.ERROR,
                    f"{node.node_type.value} is missing required property 'content'",
                    path=path,
                    node_type=node.node_type.value,
                    rule="required_props",
                )
            elif prop == "source" and not node.source:
                self.result.add(
                    Severity.ERROR,
                    f"{node.node_type.value} is missing required property 'source'",
                    path=path,
                    node_type=node.node_type.value,
                    rule="required_props",
                )
            elif prop == "chart_type" and not node.chart_type:
                self.result.add(
                    Severity.ERROR,
                    f"{node.node_type.value} is missing required property 'chart_type'",
                    path=path,
                    node_type=node.node_type.value,
                    rule="required_props",
                )

    def _check_semantic_icon(self, node: IRNode, path: str):
        if node.node_type != NodeType.GROUP:
            return
        if "semantic_icon" not in node.extra:
            return
        if not node.children:
            self.result.add(
                Severity.ERROR,
                "semantic_icon must compile to at least one native primitive",
                path=path,
                node_type=node.node_type.value,
                rule="semantic_icon_empty",
            )

    def _check_position(self, node: IRNode, path: str):
        if node.position is None:
            return
        pos = node.position
        if pos.width_mm < 0:
            self.result.add(Severity.ERROR, f"Width is negative ({pos.width_mm}mm)", path=path, rule="position")
        if pos.height_mm < 0:
            self.result.add(Severity.ERROR, f"Height is negative ({pos.height_mm}mm)", path=path, rule="position")
        if pos.x_mm < -50:
            self.result.add(Severity.WARNING, f"x coordinate is far left ({pos.x_mm}mm)", path=path, rule="position")
        if pos.y_mm < -50:
            self.result.add(Severity.WARNING, f"y coordinate is far above ({pos.y_mm}mm)", path=path, rule="position")
        if pos.x_mm + pos.width_mm > 300:
            self.result.add(Severity.WARNING, "Element may exceed right boundary", path=path, rule="position")
        if pos.y_mm + pos.height_mm > 250:
            self.result.add(Severity.WARNING, "Element may exceed bottom boundary", path=path, rule="position")

    def _check_style(self, node: IRNode, path: str):
        if node.style is None:
            return
        style = node.style
        if style.font_size is not None and style.font_size <= 0:
            self.result.add(Severity.ERROR, f"font_size must be > 0 ({style.font_size})", path=path, rule="style")
        if style.font_size is not None and style.font_size > 200:
            self.result.add(Severity.WARNING, f"font_size is unusually large ({style.font_size}pt)", path=path, rule="style")
        if style.fill_opacity is not None and (style.fill_opacity < 0 or style.fill_opacity > 1):
            self.result.add(
                Severity.ERROR,
                f"fill_opacity must be between 0 and 1 ({style.fill_opacity})",
                path=path,
                rule="style",
            )

    def _check_leaf_constraint(self, node: IRNode, path: str):
        if node.node_type in LEAF_NODES and node.children:
            self.result.add(
                Severity.ERROR,
                f"{node.node_type.value} is a leaf node but has {len(node.children)} children",
                path=path,
                node_type=node.node_type.value,
                rule="leaf_constraint",
            )


def validate_ir_v2(doc: IRDocument) -> ValidationResult:
    validator = IRValidator(doc)
    return validator.validate()
