"""PDF 渲染器 — IRDocument → .pdf 文件

使用 reportlab 将 IR 渲染为 PDF。

架构位置：ir/compiler.py → IRDocument → [本文件] → .pdf 文件

渲染流程：
  1. 创建 Canvas (A4 / 自定义尺寸)
  2. 遍历 IRDocument.children (SECTION 或 SLIDE)
  3. 每个节映射为一页
  4. 元素按类型渲染到画布
  5. 保存 .pdf 文件

坐标映射：
  IRPosition (mm) → PDF 点 (1mm = 2.835pt)
  PDF 坐标原点在左下角，IR 在左上角 → y 轴翻转

PDF 能力：
  - 矢量文字 + 精确布局
  - 表格渲染
  - 基础形状
  - 不支持动画、艺术字、图表（降级为占位符）
"""

from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 注册 CID 中文字体（reportlab 内置，无需外部文件）
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

from ...ir.types import IRDocument, IRNode, IRPosition, IRStyle, NodeType
from ...ir.validator import validate_ir_v2
from ..base import BaseRenderer, RendererCapability

# 页面尺寸
PAGE_WIDTH_MM = 254   # 10 inches ≈ 254mm (widescreen)
PAGE_HEIGHT_MM = 142.875  # 5.625 inches ≈ 142.875mm (widescreen 16:9)

# reportlab 内置字体
_BUILTIN_FONTS = {
    "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
    "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
    "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
}

# 外部字体名 → reportlab 字体映射
# 中文字体映射到 CID 字体 STSong-Light（支持简体中文）
_FONT_MAP = {
    "microsoft yahei ui": "STSong-Light",
    "microsoft yahei": "STSong-Light",
    "simhei": "STSong-Light",
    "simsun": "STSong-Light",
    "nsimsun": "STSong-Light",
    "fangsong": "STSong-Light",
    "kaiti": "STSong-Light",
    "segoe ui": "Helvetica",
    "arial": "Helvetica",
    "helvetica neue": "Helvetica",
    "impact": "Helvetica-Bold",
    "times new roman": "Times-Roman",
    "consolas": "Courier",
    "cascadia code": "Courier",
}


def _resolve_font(font_name: str | None, bold: bool = False) -> str:
    """将字体名映射到 reportlab 可用的字体"""
    if font_name is None:
        return "Helvetica-Bold" if bold else "Helvetica"

    # 直接可用
    if font_name in _BUILTIN_FONTS:
        return font_name

    # 映射
    mapped = _FONT_MAP.get(font_name.lower(), "Helvetica")

    # CID 中文字体没有 Bold 变体，直接返回
    if mapped == "STSong-Light":
        return mapped

    # 西文字体添加 Bold 后缀
    if bold and not mapped.endswith("-Bold"):
        if mapped == "Helvetica":
            return "Helvetica-Bold"
        elif mapped == "Times-Roman":
            return "Times-Bold"
        elif mapped == "Courier":
            return "Courier-Bold"
    return mapped


class PDFRenderer(BaseRenderer):
    """PDF 渲染器"""

    def __init__(self, page_size: str = "widescreen"):
        """
        Args:
            page_size: "a4", "a4_landscape", "widescreen"
        """
        self._page_size = page_size
        self._c: canvas.Canvas | None = None
        self._page_w = PAGE_WIDTH_MM * mm
        self._page_h = PAGE_HEIGHT_MM * mm

    @property
    def capability(self) -> RendererCapability:
        return RendererCapability(
            supported_node_types={
                NodeType.SLIDE, NodeType.SECTION, NodeType.TEXT,
                NodeType.TABLE, NodeType.SHAPE, NodeType.GROUP,
            },
            supported_layout_modes={"absolute"},
            supported_text_transforms=set(),
            supported_animations=set(),
            supported_effects={"shadow"},
            fallback_map={
                "gradient_fill": "solid_fill",
                "arch": "plain_text",
                "wave": "plain_text",
                "image": "placeholder",
            },
        )

    def render(self, doc: IRDocument, output_path: str | Path) -> Path:
        """渲染 IRDocument 为 .pdf 文件"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 校验
        validation = validate_ir_v2(doc)
        for issue in validation.issues:
            print(f"[IR {issue.severity.value.upper()}] {issue}")

        # 页面尺寸
        if self._page_size == "a4":
            self._page_w, self._page_h = A4
        elif self._page_size == "a4_landscape":
            self._page_w, self._page_h = landscape(A4)
        else:  # widescreen
            self._page_w = PAGE_WIDTH_MM * mm
            self._page_h = PAGE_HEIGHT_MM * mm

        self._c = canvas.Canvas(str(output_path), pagesize=(self._page_w, self._page_h))

        for i, node in enumerate(doc.children):
            if i > 0:
                self._c.showPage()
            if node.node_type in (NodeType.SECTION, NodeType.SLIDE):
                self._render_slide(node, doc)

        self._c.save()
        return output_path

    def _render_slide(self, node: IRNode, doc: IRDocument):
        """渲染一张幻灯片/节"""
        # 先渲染背景
        self._render_background(node)
        for child in node.children:
            self._render_element(child, doc)

    def _render_background(self, node: IRNode):
        """渲染幻灯片背景（纯色或渐变）"""
        bg = (node.extra or {}).get("background", {})
        if not bg:
            return

        self._c.saveState()

        # 渐变背景
        gradient = bg.get("gradient")
        if gradient:
            stops = gradient.get("stops", [])
            if len(stops) >= 2:
                try:
                    c1 = HexColor(stops[0])
                    c2 = HexColor(stops[1])
                    # 用多个矩形条近似渐变
                    steps = 40
                    for s in range(steps):
                        ratio = s / steps
                        r = c1.red + (c2.red - c1.red) * ratio
                        g = c1.green + (c2.green - c1.green) * ratio
                        b = c1.blue + (c2.blue - c1.blue) * ratio
                        color = Color(r, g, b)
                        self._c.setFillColor(color)
                        bar_h = self._page_h / steps
                        self._c.rect(0, s * bar_h, self._page_w, bar_h + 0.5, fill=1, stroke=0)
                except Exception:
                    pass  # 渐变失败时回退到纯色
        else:
            # 纯色背景
            color = bg.get("color")
            if color:
                try:
                    self._c.setFillColor(HexColor(color))
                    self._c.rect(0, 0, self._page_w, self._page_h, fill=1, stroke=0)
                except (ValueError, TypeError):
                    pass

        self._c.restoreState()

    def _render_element(self, node: IRNode, doc: IRDocument):
        """按节点类型分派"""
        if node.node_type == NodeType.TEXT:
            self._render_text(node)
        elif node.node_type == NodeType.TABLE:
            self._render_table(node)
        elif node.node_type == NodeType.SHAPE:
            self._render_shape(node)
        elif node.node_type == NodeType.IMAGE:
            self._render_image_placeholder(node)
        elif node.node_type == NodeType.CHART:
            self._render_chart_placeholder(node)
        elif node.node_type == NodeType.GROUP:
            for child in node.children:
                self._render_element(child, doc)

    def _wrap_text(self, text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
        """将文本按宽度折行

        中文字符约 0.5 * font_size 宽度，英文约 0.55 * font_size 宽度。
        """
        if not text:
            return [""]
        lines: list[str] = []
        current: list[str] = []
        current_w = 0.0
        char_w_factor = font_size * 0.55  # 英文字符宽度基准

        for ch in text:
            # 估算字符宽度
            if ord(ch) > 127:
                ch_w = font_size * 0.5
            else:
                ch_w = font_size * 0.55

            if current_w + ch_w > max_width and current:
                lines.append("".join(current))
                current = []
                current_w = 0.0
            current.append(ch)
            current_w += ch_w

        if current:
            lines.append("".join(current))
        return lines if lines else [""]

    def _render_text(self, node: IRNode):
        """渲染文本（支持自动折行）"""
        style = node.style
        content = node.content or ""
        if not content.strip():
            return

        pos = node.position
        x, y, w, h = self._get_coords(pos)

        font_size = 14
        font_color = black
        bold = False
        font_family = None

        if style:
            if style.font_family:
                font_family = style.font_family
            if style.font_size:
                font_size = style.font_size
            if style.font_color:
                try:
                    font_color = HexColor(style.font_color)
                except (ValueError, TypeError):
                    font_color = black
            if style.font_weight and style.font_weight >= 700:
                bold = True

        font_name = _resolve_font(font_family, bold)

        self._c.saveState()
        self._c.setFillColor(font_color)
        self._c.setFont(font_name, font_size)

        line_height = font_size * 1.4

        # 先按 \n 分段，再对每段按宽度折行
        paragraphs = content.split("\n")
        all_lines: list[str] = []
        for para in paragraphs:
            if para:
                # 减去左边距 (2pt)
                wrapped = self._wrap_text(para, font_name, font_size, w - 4)
                all_lines.extend(wrapped)
            else:
                all_lines.append("")  # 保留空行

        # 检查是否有 center 标志
        center_flag = (node.extra or {}).get("center", False)

        for i, line in enumerate(all_lines):
            text_y = y + h - font_size - i * line_height
            if text_y < y:
                break
            if center_flag:
                # 居中：计算文本宽度
                text_w = self._c.stringWidth(line, font_name, font_size)
                self._c.drawString(x + (w - text_w) / 2, text_y, line)
            else:
                self._c.drawString(x + 2, text_y, line)

        self._c.restoreState()

    def _render_table(self, node: IRNode):
        """渲染表格"""
        data = node.extra.get("data", [])
        rows = node.extra.get("rows", len(data))
        # 安全计算列数：确保 data[0] 是列表
        if data and isinstance(data[0], list):
            cols = node.extra.get("cols", len(data[0]))
        else:
            cols = node.extra.get("cols", 0)

        if not data or cols == 0:
            return

        pos = node.position
        x, y, w, h = self._get_coords(pos)

        # 准备表格数据
        table_data = []
        for row in data[:rows]:
            if isinstance(row, list):
                table_data.append([str(c) for c in row[:cols]])

        if not table_data:
            return

        # 计算列宽
        col_width = w / cols if cols else w

        table = Table(table_data, colWidths=[col_width] * cols)

        # 表格样式
        style_cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E293B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]

        # 交替行背景
        for r in range(1, len(table_data)):
            if r % 2 == 0:
                style_cmds.append(("BACKGROUND", (0, r), (-1, r), HexColor("#F1F5F9")))

        table.setStyle(TableStyle(style_cmds))

        # 渲染到画布
        table_w, table_h = table.wrap(0, 0)
        # PDF 坐标: 左下角为原点，表格从上往下画
        table.drawOn(self._c, x, y + h - table_h)

    def _render_shape(self, node: IRNode):
        """渲染形状 → 基础矩形/圆形"""
        pos = node.position
        if not pos:
            return
        x, y, w, h = self._get_coords(pos)

        style = node.style
        fill_color = None
        if style and style.fill_color:
            try:
                fill_color = HexColor(style.fill_color)
            except (ValueError, TypeError):
                fill_color = None  # 无效颜色不填充

        self._c.saveState()
        if fill_color:
            self._c.setFillColor(fill_color)

        shape_type = node.extra.get("shape_type", "rectangle")
        if shape_type in ("circle", "ellipse"):
            self._c.ellipse(x, y, x + w, y + h, fill=1 if fill_color else 0)
        elif shape_type == "rounded_rectangle":
            self._c.roundRect(x, y, w, h, 4, fill=1 if fill_color else 0)
        else:
            self._c.rect(x, y, w, h, fill=1 if fill_color else 0)

        self._c.restoreState()

    def _render_image_placeholder(self, node: IRNode):
        """渲染图片占位符"""
        pos = node.position
        if not pos:
            return
        x, y, w, h = self._get_coords(pos)

        self._c.saveState()
        self._c.setStrokeColor(HexColor("#CBD5E1"))
        self._c.setFillColor(HexColor("#F1F5F9"))
        self._c.rect(x, y, w, h, fill=1)
        self._c.setFillColor(HexColor("#94A3B8"))
        self._c.setFont("Helvetica", 10)
        self._c.drawCentredString(x + w / 2, y + h / 2, f"[Image: {node.source or ''}]")
        self._c.restoreState()

    def _render_chart_placeholder(self, node: IRNode):
        """渲染图表占位符"""
        pos = node.position
        if not pos:
            return
        x, y, w, h = self._get_coords(pos)

        self._c.saveState()
        self._c.setStrokeColor(HexColor("#CBD5E1"))
        self._c.setFillColor(HexColor("#EFF6FF"))
        self._c.rect(x, y, w, h, fill=1)
        self._c.setFillColor(HexColor("#3B82F6"))
        self._c.setFont("Helvetica", 10)
        title = node.extra.get("title", node.chart_type or "chart")
        self._c.drawCentredString(x + w / 2, y + h / 2, f"[Chart: {title}]")
        self._c.restoreState()

    def _get_coords(self, pos: IRPosition | None) -> tuple[float, float, float, float]:
        """将 IRPosition (mm, 左上角原点) 转换为 PDF 坐标 (pt, 左下角原点)

        Returns:
            (x_pt, y_pt, w_pt, h_pt)
        """
        if pos is None:
            return (0, 0, 100 * mm, 50 * mm)

        x = pos.x_mm * mm
        w = pos.width_mm * mm
        h = pos.height_mm * mm
        # 翻转 y 轴: IR y=0 在顶部, PDF y=0 在底部
        y = self._page_h - (pos.y_mm * mm) - h

        return (x, y, w, h)
