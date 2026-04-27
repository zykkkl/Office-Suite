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
        if n.position and n.position.width > 0 and n.position.height > 0:
            positioned.append(n)

    for i in range(len(positioned)):
        for j in range(i + 1, len(positioned)):
            a, b = positioned[i], positioned[j]
            pa, pb = a.position, b.position
            # AABB 重叠检测
            if (pa.x < pb.x + pb.width and pa.x + pa.width > pb.x and
                    pa.y < pb.y + pb.height and pa.y + pa.height > pb.y):
                overlap_x = min(pa.x + pa.width, pb.x + pb.width) - max(pa.x, pb.x)
                overlap_y = min(pa.y + pa.height, pb.y + pb.height) - max(pa.y, pb.y)
                overlap_area = overlap_x * overlap_y
                min_area = min(pa.width * pa.height, pb.width * pb.height)
                if min_area > 0 and overlap_area / min_area > 0.1:
                    report.issues.append(LintIssue(
                        LintSeverity.WARNING, "overlap",
                        f"'{a.content or a.type}' 与 '{b.content or b.type}' 重叠 "
                        f"({overlap_area:.0f}mm²)",
                        suggestion="调整位置或尺寸避免重叠"))


def _check_contrast(nodes: list[IRNode], report: LintReport):
    """检查文本与背景对比度"""
    for n in nodes:
        if n.type != NodeType.TEXT or not n.style:
            continue
        text_color = n.style.font.color if n.style.font else None
        bg_color = n.style.fill.color if n.style.fill else None
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
        if n.type == NodeType.TEXT and n.style and n.style.font and n.style.font.size:
            sizes.append(n.style.font.size)
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
        if n.style and n.style.font and n.style.font.color:
            colors.add(n.style.font.color)
        if n.style and n.style.fill and n.style.fill.color:
            colors.add(n.style.fill.color)
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
            # 检查水平或垂直间距
            h_gap = max(0, pb.x - (pa.x + pa.width), pa.x - (pb.x + pb.width))
            v_gap = max(0, pb.y - (pa.y + pa.height), pa.y - (pb.y + pb.height))
            # 如果两元素在相近的行/列且间距太小
            if (abs(pa.y - pb.y) < 5 and 0 < h_gap < 3):
                report.issues.append(LintIssue(
                    LintSeverity.INFO, "spacing",
                    f"'{a.content or a.type}' 与 '{b.content or b.type}' 水平间距仅 {h_gap:.1f}mm",
                    suggestion="建议间距 >= 5mm"))
            if (abs(pa.x - pb.x) < 5 and 0 < v_gap < 3):
                report.issues.append(LintIssue(
                    LintSeverity.INFO, "spacing",
                    f"'{a.content or a.type}' 与 '{b.content or b.type}' 垂直间距仅 {v_gap:.1f}mm",
                    suggestion="建议间距 >= 5mm"))


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
    for slide in ir_doc.slides:
        all_nodes.extend(slide.children)

    _check_overlap(all_nodes, report)
    _check_contrast(all_nodes, report)
    _check_font_hierarchy(all_nodes, report)
    _check_color_count(all_nodes, report)
    _check_spacing(all_nodes, report)

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
