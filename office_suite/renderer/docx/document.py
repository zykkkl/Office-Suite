"""DOCX 渲染器 — IRDocument → .docx 文件

使用 python-docx 将 IR 渲染为 Word 文档。

架构位置：ir/compiler.py → IRDocument → [本文件] → .docx 文件

渲染流程：
  1. 创建 Document
  2. 遍历 IRDocument.children (SECTION 或 SLIDE 节点)
  3. 每个节：遍历子元素 → 分派到对应渲染方法
  4. 保存 .docx 文件

DOCX 能力限制（设计方案第八章）：
  - 不支持艺术字（降级为普通文本）
  - 不支持动画（跳过）
  - 仅支持基础阴影

增强功能：
  - 段落格式（间距、行距、缩进、对齐）
  - 列表渲染（有序/无序）
  - 节分隔符（分页、连续分节）
  - Word 内置样式（Heading 1-9, List Bullet 等）
"""

from pathlib import Path
from typing import Any

from docx import Document
from docx.shared import Pt, Mm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn

from ...ir.types import IRDocument, IRNode, IRPosition, IRStyle, NodeType
from ...ir.validator import validate_ir_v2
from ..base import BaseRenderer, RendererCapability


# 对齐方式映射
_ALIGN_MAP = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
}


class DOCXRenderer(BaseRenderer):
    """Word 文档渲染器"""

    def __init__(self):
        self._doc: Document | None = None
        self._slide_count: int = 0  # 用于跟踪是否需要分页

    @property
    def capability(self) -> RendererCapability:
        return RendererCapability(
            supported_node_types={
                NodeType.SLIDE, NodeType.SECTION, NodeType.TEXT,
                NodeType.IMAGE, NodeType.TABLE, NodeType.GROUP,
            },
            supported_layout_modes={"absolute", "relative", "grid"},
            supported_text_transforms=set(),  # 不支持艺术字
            supported_animations=set(),       # 不支持动画
            supported_effects={"shadow"},     # 仅基础阴影
            fallback_map={
                "arch": "plain_text",
                "wave": "plain_text",
                "gradient_fill": "solid_fill",
            },
        )

    def render(self, doc: IRDocument, output_path: str | Path) -> Path:
        """渲染 IRDocument 为 .docx 文件"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 校验
        validation = validate_ir_v2(doc)
        for issue in validation.issues:
            print(f"[IR {issue.severity.value.upper()}] {issue}")

        self._doc = Document()
        self._slide_count = len(doc.children)

        # 设置默认字体
        style = self._doc.styles["Normal"]
        style.font.name = "Microsoft YaHei UI"
        style.font.size = Pt(11)

        # 遍历节/幻灯片
        for i, node in enumerate(doc.children):
            is_last = (i == len(doc.children) - 1)
            if node.node_type == NodeType.SECTION:
                self._render_section(node, doc, add_break=not is_last)
            elif node.node_type == NodeType.SLIDE:
                self._render_slide_as_section(node, doc, add_break=not is_last)

        self._doc.save(str(output_path))
        return output_path

    def _render_section(self, node: IRNode, doc: IRDocument, add_break: bool = False):
        """渲染 SECTION 节点

        支持 section_break 属性：
          - "continuous": 连续分节（同页）
          - "new_page" / "next_page": 新页分节
          - "even_page": 偶数页分节
          - "odd_page": 奇数页分节
        """
        # 节属性
        section_break = node.extra.get("section_break", "")
        page_size = node.extra.get("page_size", "")
        orientation = node.extra.get("orientation", "")

        # 设置节属性
        if page_size or orientation:
            self._apply_section_properties(page_size, orientation)

        # 渲染子元素
        for child in node.children:
            self._render_element(child, doc)

        # 节分隔
        if section_break:
            self._add_section_break(section_break)
        elif add_break:
            self._add_page_break()

    def _render_slide_as_section(self, node: IRNode, doc: IRDocument, add_break: bool = False):
        """将 SLIDE 节点作为文档节渲染

        每张幻灯片映射为一个文档节（段落集合）。
        """
        for child in node.children:
            self._render_element(child, doc)

        # 节之间加分页符
        if add_break:
            self._add_page_break()

    def _add_page_break(self):
        """添加分页符"""
        para = self._doc.add_paragraph()
        run = para.add_run()
        run.add_break(WD_BREAK.PAGE)

    def _add_section_break(self, break_type: str):
        """添加分节符"""
        from docx.enum.section import WD_SECTION_START
        break_map = {
            "continuous": WD_SECTION_START.CONTINUOUS,
            "new_page": WD_SECTION_START.NEW_PAGE,
            "next_page": WD_SECTION_START.NEW_PAGE,
            "even_page": WD_SECTION_START.EVEN_PAGE,
            "odd_page": WD_SECTION_START.ODD_PAGE,
        }
        section_start = break_map.get(break_type, WD_SECTION_START.NEW_PAGE)
        new_section = self._doc.add_section(section_start)
        return new_section

    def _apply_section_properties(self, page_size: str, orientation: str):
        """应用节属性（页面大小、方向）"""
        section = self._doc.sections[-1]
        # 页面大小
        size_map = {
            "a4": (Mm(210), Mm(297)),
            "a3": (Mm(297), Mm(420)),
            "letter": (Inches(8.5), Inches(11)),
            "legal": (Inches(8.5), Inches(14)),
        }
        if page_size in size_map:
            w, h = size_map[page_size]
            section.page_width = w
            section.page_height = h

        # 方向
        if orientation == "landscape":
            section.orientation = WD_ORIENT.LANDSCAPE
        elif orientation == "portrait":
            section.orientation = WD_ORIENT.PORTRAIT

    def _render_element(self, node: IRNode, doc: IRDocument):
        """按节点类型分派渲染"""
        if node.node_type == NodeType.TEXT:
            self._render_text(node, doc)
        elif node.node_type == NodeType.TABLE:
            self._render_table(node, doc)
        elif node.node_type == NodeType.IMAGE:
            self._render_image(node, doc)
        elif node.node_type == NodeType.SHAPE:
            self._render_shape(node, doc)
        elif node.node_type == NodeType.GROUP:
            for child in node.children:
                self._render_element(child, doc)
        else:
            # 不支持的类型：添加占位段落
            self._doc.add_paragraph(f"[{node.node_type.value}]")

    def _render_text(self, node: IRNode, doc: IRDocument):
        """渲染文本元素

        支持：
        - 标题级别（extra.heading_level 或 font_size 推断）
        - 列表项（extra.list_type: "bullet" / "numbered"）
        - 段落格式（对齐、间距、行距、缩进）
        """
        style = node.style
        content = node.content or ""

        if not content.strip():
            return

        # 列表渲染
        list_type = node.extra.get("list_type", "")
        if list_type:
            self._render_list_item(node, content, style, list_type)
            return

        # 标题级别
        heading_level = node.extra.get("heading_level", 0)
        if not heading_level:
            heading_level = self._infer_heading_level(style)

        if 1 <= heading_level <= 9:
            heading = self._doc.add_heading(content, level=heading_level)
            self._apply_heading_style(heading, style)
        else:
            para = self._doc.add_paragraph(content)
            self._apply_paragraph_style(para, style)
            self._apply_paragraph_format(para, node)

    def _render_list_item(self, node: IRNode, content: str, style: IRStyle | None, list_type: str):
        """渲染列表项

        list_type: "bullet" → 无序列表, "numbered" → 有序列表
        """
        # 使用 Word 内置列表样式
        if list_type == "numbered":
            para = self._doc.add_paragraph(content, style="List Number")
        else:
            para = self._doc.add_paragraph(content, style="List Bullet")

        self._apply_paragraph_style(para, style)

    def _infer_heading_level(self, style: IRStyle | None) -> int:
        """根据 font_size 推断标题级别"""
        if style is None or style.font_size is None:
            return 0
        fs = style.font_size
        if fs >= 36:
            return 1
        if fs >= 28:
            return 2
        if fs >= 22:
            return 3
        if fs >= 18:
            return 4
        return 0

    def _apply_paragraph_format(self, para, node: IRNode):
        """应用段落格式：对齐、间距、行距、缩进"""
        extra = node.extra
        pf = para.paragraph_format

        # 对齐
        align = extra.get("align", "")
        if align in _ALIGN_MAP:
            pf.alignment = _ALIGN_MAP[align]

        # 段前间距（pt）
        space_before = extra.get("space_before")
        if space_before is not None:
            pf.space_before = Pt(float(space_before))

        # 段后间距（pt）
        space_after = extra.get("space_after")
        if space_after is not None:
            pf.space_after = Pt(float(space_after))

        # 行距
        line_spacing = extra.get("line_spacing")
        if line_spacing is not None:
            pf.line_spacing = float(line_spacing)
            pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE

        # 固定行距（pt）
        line_spacing_pt = extra.get("line_spacing_pt")
        if line_spacing_pt is not None:
            pf.line_spacing = Pt(float(line_spacing_pt))
            pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY

        # 左缩进
        left_indent = extra.get("left_indent")
        if left_indent is not None:
            pf.left_indent = Mm(float(left_indent))

        # 首行缩进
        first_line_indent = extra.get("first_line_indent")
        if first_line_indent is not None:
            pf.first_line_indent = Mm(float(first_line_indent))

    def _render_table(self, node: IRNode, doc: IRDocument):
        """渲染表格元素

        支持 extra 中的 table_style 属性覆盖默认样式。
        """
        rows = node.extra.get("rows", 3)
        cols = node.extra.get("cols", 3)
        data = node.extra.get("data", [])
        table_style = node.extra.get("table_style", "Table Grid")

        table = self._doc.add_table(rows=rows, cols=cols, style=table_style)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # 填充数据
        for r, row_data in enumerate(data[:rows]):
            if isinstance(row_data, list):
                for c, cell_val in enumerate(row_data[:cols]):
                    cell = table.cell(r, c)
                    cell.text = str(cell_val)
                    # 首行加粗
                    if r == 0:
                        for para in cell.paragraphs:
                            for run in para.runs:
                                run.bold = True

    def _render_image(self, node: IRNode, doc: IRDocument):
        """渲染图片元素"""
        source = node.source
        if isinstance(source, str):
            file_path = Path(source.replace("file://", ""))
            if file_path.exists():
                # 计算宽度
                width = None
                if node.position and node.position.width_mm > 0:
                    width = Mm(int(node.position.width_mm))
                self._doc.add_picture(str(file_path), width=width)
                return

        # 降级：占位符
        self._doc.add_paragraph(f"[图片: {source}]")

    def _render_shape(self, node: IRNode, doc: IRDocument):
        """渲染形状 → DOCX 中降级为带样式的段落"""
        content = node.content or f"[{node.extra.get('shape_type', 'shape')}]"
        style = node.style

        para = self._doc.add_paragraph(content)
        if style and style.fill_color:
            # 用背景色模拟形状
            shading = para.paragraph_format.element.get_or_add_pPr()
            shd = shading.makeelement(qn("w:shd"), {
                qn("w:fill"): style.fill_color.lstrip("#"),
                qn("w:val"): "clear",
            })
            shading.append(shd)
        self._apply_paragraph_style(para, style)

    def _apply_paragraph_style(self, para, style: IRStyle | None):
        """应用段落样式（run 级别：字体、大小、粗体、斜体、颜色）"""
        if style is None:
            return
        for run in para.runs:
            if style.font_family:
                run.font.name = style.font_family
            if style.font_size:
                run.font.size = Pt(style.font_size)
            if style.font_weight and style.font_weight >= 700:
                run.bold = True
            if style.font_italic:
                run.italic = True
            if style.font_color:
                run.font.color.rgb = self._hex_to_rgb(style.font_color)

    def _apply_heading_style(self, heading, style: IRStyle | None):
        """应用标题样式"""
        if style is None:
            return
        for run in heading.runs:
            if style.font_color:
                run.font.color.rgb = self._hex_to_rgb(style.font_color)
            if style.font_size:
                run.font.size = Pt(style.font_size)

    @staticmethod
    def _hex_to_rgb(hex_str: str) -> RGBColor:
        hex_str = hex_str.lstrip("#")
        if len(hex_str) == 8:
            hex_str = hex_str[:6]
        if len(hex_str) != 6:
            return RGBColor(0, 0, 0)
        try:
            return RGBColor(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))
        except ValueError:
            return RGBColor(0, 0, 0)
