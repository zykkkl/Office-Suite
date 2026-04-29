"""设计规范检查器 — 对 IR 文档进行设计质量审查

检查规则：
  - 布局重叠检测
  - 对比度不足（WCAG AA）
  - 字号层次混乱
  - 对齐不一致
  - 颜色数量过多
  - 留白不足

输入：IRDocument
输出：LintReport（问题列表 + 评分）
"""

from dataclasses import dataclass, field
import re
from typing import Any

from ..ir.types import IRDocument, IRNode, NodeType


class LintSeverity:
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintIssue:
    severity: str
    rule: str
    message: str
    node_path: str = ""
    suggestion: str = ""


@dataclass
class LintReport:
    issues: list[LintIssue] = field(default_factory=list)
    score: float = 100.0

    @property
    def errors(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == LintSeverity.ERROR]

    @property
    def warnings(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == LintSeverity.WARNING]

    def summary(self) -> str:
        if not self.issues:
            return f"Score: {self.score:.0f}/100 — No issues found."
        lines = [f"Score: {self.score:.0f}/100"]
        for i in self.issues:
            prefix = {"error": "E", "warning": "W", "info": "I"}.get(i.severity, "?")
            lines.append(f"  [{prefix}] {i.rule}: {i.message}")
            if i.suggestion:
                lines.append(f"       -> {i.suggestion}")
        return "\n".join(lines)


def _node_type(node: IRNode):
    return getattr(node, "node_type", getattr(node, "type", None))


def _node_label(node: IRNode) -> str:
    node_type = _node_type(node)
    type_label = node_type.value if hasattr(node_type, "value") else str(node_type)
    return str(getattr(node, "content", "") or type_label)


def _pos_attr(pos, name: str) -> float:
    modern = {
        "x": "x_mm",
        "y": "y_mm",
        "width": "width_mm",
        "height": "height_mm",
    }[name]
    return float(getattr(pos, modern, getattr(pos, name, 0)) or 0)


def _style_attr(style, name: str):
    return getattr(style, name, None)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _luminance(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    rs, gs, bs = r / 255, g / 255, b / 255
    rl = rs / 12.92 if rs <= 0.03928 else ((rs + 0.055) / 1.055) ** 2.4
    gl = gs / 12.92 if gs <= 0.03928 else ((gs + 0.055) / 1.055) ** 2.4
    bl = bs / 12.92 if bs <= 0.03928 else ((bs + 0.055) / 1.055) ** 2.4
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl


def _contrast_ratio(c1: str, c2: str) -> float:
    l1, l2 = _luminance(c1), _luminance(c2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def _check_overlap(nodes: list[IRNode], report: LintReport):
    """检测元素重叠"""
    positioned = []
    for n in nodes:
        if (
            _node_type(n) == NodeType.TEXT
            and n.position
            and _pos_attr(n.position, "width") > 0
            and _pos_attr(n.position, "height") > 0
        ):
            positioned.append(n)

    for i in range(len(positioned)):
        for j in range(i + 1, len(positioned)):
            a, b = positioned[i], positioned[j]
            pa, pb = a.position, b.position
            # AABB 重叠检测
            ax, ay = _pos_attr(pa, "x"), _pos_attr(pa, "y")
            aw, ah = _pos_attr(pa, "width"), _pos_attr(pa, "height")
            bx, by = _pos_attr(pb, "x"), _pos_attr(pb, "y")
            bw, bh = _pos_attr(pb, "width"), _pos_attr(pb, "height")
            if (ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by):
                overlap_x = min(ax + aw, bx + bw) - max(ax, bx)
                overlap_y = min(ay + ah, by + bh) - max(ay, by)
                overlap_area = overlap_x * overlap_y
                min_area = min(aw * ah, bw * bh)
                if min_area > 0 and overlap_area / min_area > 0.1:
                    report.issues.append(LintIssue(
                        LintSeverity.WARNING, "overlap",
                        f"'{_node_label(a)}' 与 '{_node_label(b)}' 重叠 "
                        f"({overlap_area:.0f}mm^2)",
                        suggestion="调整位置或尺寸避免重叠"))


def _check_contrast(nodes: list[IRNode], report: LintReport):
    """检查文本与背景对比度"""
    for n in nodes:
        if _node_type(n) != NodeType.TEXT or not n.style:
            continue
        text_color = _style_attr(n.style, "font_color")
        bg_color = _style_attr(n.style, "fill_color")
        if not text_color or not bg_color:
            continue
        if not text_color.startswith("#") or not bg_color.startswith("#"):
            continue
        ratio = _contrast_ratio(text_color, bg_color)
        if ratio < 3.0:
            report.issues.append(LintIssue(
                LintSeverity.ERROR, "contrast",
                f"对比度严重不足 ({ratio:.1f}:1)，WCAG AA 要求 >= 4.5:1",
                suggestion="增加文字与背景的明暗差异"))
        elif ratio < 4.5:
            report.issues.append(LintIssue(
                LintSeverity.WARNING, "contrast",
                f"对比度偏低 ({ratio:.1f}:1)，WCAG AA 要求 >= 4.5:1",
                suggestion="建议增加对比度以提高可读性"))


def _check_font_hierarchy(nodes: list[IRNode], report: LintReport):
    """检查字号层次是否合理"""
    sizes = []
    for n in nodes:
        if _node_type(n) == NodeType.TEXT and n.style and _style_attr(n.style, "font_size"):
            sizes.append(_style_attr(n.style, "font_size"))
    if len(sizes) < 2:
        return
    unique_sizes = sorted(set(sizes), reverse=True)
    if len(unique_sizes) > 6:
        report.issues.append(LintIssue(
            LintSeverity.WARNING, "font_hierarchy",
            f"使用了 {len(unique_sizes)} 种不同字号，建议控制在 4-5 种以内",
            suggestion="统一字号，建立清晰的视觉层次"))
    # 检查相邻字号差异
    for i in range(len(unique_sizes) - 1):
        diff = unique_sizes[i] - unique_sizes[i + 1]
        if diff < 2:
            report.issues.append(LintIssue(
                LintSeverity.INFO, "font_hierarchy",
                f"字号 {unique_sizes[i]}pt 和 {unique_sizes[i+1]}pt 差异过小，"
                "视觉层次不明显",
                suggestion="增大字号差异以强化层次感"))


def _check_color_count(nodes: list[IRNode], report: LintReport):
    """检查颜色数量"""
    colors = set()
    for n in nodes:
        if n.style and _style_attr(n.style, "font_color"):
            colors.add(_style_attr(n.style, "font_color"))
        if n.style and _style_attr(n.style, "fill_color"):
            colors.add(_style_attr(n.style, "fill_color"))
    if len(colors) > 8:
        report.issues.append(LintIssue(
            LintSeverity.WARNING, "color_count",
            f"使用了 {len(colors)} 种颜色，过多的颜色会显得杂乱",
            suggestion="限制在 5-6 种颜色内，使用主题色系"))


def _check_spacing(nodes: list[IRNode], report: LintReport):
    """检查元素间距是否充足"""
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            a, b = nodes[i], nodes[j]
            if not a.position or not b.position:
                continue
            pa, pb = a.position, b.position
            ax, ay = _pos_attr(pa, "x"), _pos_attr(pa, "y")
            aw, ah = _pos_attr(pa, "width"), _pos_attr(pa, "height")
            bx, by = _pos_attr(pb, "x"), _pos_attr(pb, "y")
            bw, bh = _pos_attr(pb, "width"), _pos_attr(pb, "height")
            # 检查水平或垂直间距
            h_gap = max(0, bx - (ax + aw), ax - (bx + bw))
            v_gap = max(0, by - (ay + ah), ay - (by + bh))
            # 如果两元素在相近的行/列且间距太小
            if (abs(ay - by) < 5 and 0 < h_gap < 3):
                report.issues.append(LintIssue(
                    LintSeverity.INFO, "spacing",
                    f"'{_node_label(a)}' 与 '{_node_label(b)}' 水平间距仅 {h_gap:.1f}mm",
                    suggestion="建议间距 >= 5mm"))
            if (abs(ax - bx) < 5 and 0 < v_gap < 3):
                report.issues.append(LintIssue(
                    LintSeverity.INFO, "spacing",
                    f"'{_node_label(a)}' 与 '{_node_label(b)}' 垂直间距仅 {v_gap:.1f}mm",
                    suggestion="建议间距 >= 5mm"))


def _same_bounds(a: IRNode, b: IRNode, tolerance_mm: float = 1.0) -> bool:
    if not a.position or not b.position:
        return False
    return (
        abs(_pos_attr(a.position, "x") - _pos_attr(b.position, "x")) <= tolerance_mm
        and abs(_pos_attr(a.position, "y") - _pos_attr(b.position, "y")) <= tolerance_mm
        and abs(_pos_attr(a.position, "width") - _pos_attr(b.position, "width")) <= tolerance_mm
        and abs(_pos_attr(a.position, "height") - _pos_attr(b.position, "height")) <= tolerance_mm
    )


def _contains_bounds(container: IRNode, child: IRNode) -> bool:
    if not container.position or not child.position:
        return False
    cx, cy = _pos_attr(container.position, "x"), _pos_attr(container.position, "y")
    cw, ch = _pos_attr(container.position, "width"), _pos_attr(container.position, "height")
    tx, ty = _pos_attr(child.position, "x"), _pos_attr(child.position, "y")
    tw, th = _pos_attr(child.position, "width"), _pos_attr(child.position, "height")
    return tx >= cx and ty >= cy and tx + tw <= cx + cw and ty + th <= cy + ch


def _check_centered_shape_labels(nodes: list[IRNode], report: LintReport):
    """Centered text inside round badges should use the full shape bounds."""
    round_shapes = [
        node for node in nodes
        if _node_type(node) == NodeType.SHAPE
        and node.position
        and str(node.extra.get("shape_type", "")).lower() in {"circle", "ellipse", "oval"}
    ]
    centered_texts = [
        node for node in nodes
        if _node_type(node) == NodeType.TEXT
        and node.position
        and str(node.extra.get("align", node.extra.get("text_align", ""))).lower() == "center"
        and str(node.extra.get(
            "vertical_align",
            node.extra.get("verticalAlign", node.extra.get("valign", "")),
        )).lower() in {"middle", "center"}
    ]

    for shape in round_shapes:
        for text in centered_texts:
            if _contains_bounds(shape, text) and not _same_bounds(shape, text):
                report.issues.append(LintIssue(
                    LintSeverity.WARNING,
                    "centered_shape_label",
                    f"'{_node_label(text)}' is centered inside a round shape but does not use the full shape bounds",
                    suggestion="Set the text position equal to the circle/ellipse position and use align:center, vertical_align:middle, margin:0",
                ))


def _check_sequence_completeness(nodes: list[IRNode], report: LintReport):
    """Warn when an obvious numeric text sequence has missing middle items."""
    numeric_values: list[int] = []
    day_values: list[int] = []

    for node in nodes:
        if _node_type(node) != NodeType.TEXT:
            continue
        content = str(getattr(node, "content", "") or "").strip()
        if re.fullmatch(r"\d{1,2}", content):
            numeric_values.append(int(content))
            continue
        match = re.match(r"^[Dd](\d{1,2})(?:\s|\\n|$)", content)
        if match:
            day_values.append(int(match.group(1)))

    for rule, values, label in (
        ("number_sequence", numeric_values, "numbered sequence"),
        ("day_sequence", day_values, "day sequence"),
    ):
        if len(values) < 2:
            continue
        unique_values = sorted(set(values))
        expected = set(range(unique_values[0], unique_values[-1] + 1))
        missing = sorted(expected - set(unique_values))
        if missing:
            report.issues.append(LintIssue(
                LintSeverity.WARNING,
                rule,
                f"Missing {label} item(s): {', '.join(str(v) for v in missing)}",
                suggestion="Keep visible numbered steps/cards continuous unless the gap is intentional.",
            ))


def _check_page_marker_layout(nodes: list[IRNode], report: LintReport):
    """Page markers such as 02 / 10 must be wide enough and non-wrapping."""
    for node in nodes:
        if _node_type(node) != NodeType.TEXT or not node.position:
            continue
        content = str(getattr(node, "content", "") or "").strip()
        if not re.fullmatch(r"\d{1,2}\s*/\s*\d{1,2}", content):
            continue

        width = _pos_attr(node.position, "width")
        wrap_value = node.extra.get("wrap", node.extra.get("word_wrap", True))
        wrap_disabled = (
            wrap_value is False
            or (isinstance(wrap_value, str) and wrap_value.lower() in {"false", "no", "0", "nowrap", "none"})
        )
        align = str(node.extra.get("align", node.extra.get("text_align", ""))).lower()
        if width < 30 or not wrap_disabled or align != "right":
            report.issues.append(LintIssue(
                LintSeverity.WARNING,
                "page_marker_layout",
                f"Page marker '{content}' may wrap or drift because its box is narrow or not right-aligned",
                suggestion="Use width >= 30mm, align:right, vertical_align:middle, margin:0, and wrap:false.",
            ))


def lint_ir(ir_doc: IRDocument) -> LintReport:
    """对 IR 文档执行设计规范检查

    Args:
        ir_doc: 编译后的 IR 文档

    Returns:
        LintReport
    """
    report = LintReport()

    # 收集所有节点
    all_nodes = []
    slides = getattr(ir_doc, "slides", None) or getattr(ir_doc, "children", [])
    for slide in slides:
        all_nodes.extend(slide.children)

    _check_contrast(all_nodes, report)
    _check_font_hierarchy(all_nodes, report)
    _check_color_count(all_nodes, report)

    slides = getattr(ir_doc, "slides", None) or getattr(ir_doc, "children", [])
    for slide in slides:
        _check_overlap(slide.children, report)
        _check_spacing(slide.children, report)
        _check_centered_shape_labels(slide.children, report)
        _check_sequence_completeness(slide.children, report)
        _check_page_marker_layout(slide.children, report)

    # 计算评分
    for issue in report.issues:
        if issue.severity == LintSeverity.ERROR:
            report.score -= 10
        elif issue.severity == LintSeverity.WARNING:
            report.score -= 5
        else:
            report.score -= 1
    report.score = max(0, report.score)

    return report
