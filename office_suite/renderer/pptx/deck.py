"""PPTX 渲染器 — IRDocument → .pptx 文件

使用 python-pptx 将 IR 渲染为 PowerPoint 文件。
坐标映射：mm → EMU (1mm = 36000 EMU)

架构位置：ir/compiler.py 输出 IRDocument → [本文件] → .pptx 文件

渲染流程：
  1. validate_ir_v2() — 渲染前校验 IR 合法性
  2. Presentation() — 创建空白演示文稿
  3. 遍历 IRDocument.children (SLIDE 节点)
  4. 每张幻灯片：设置背景 → 遍历子元素 → 分派到对应渲染方法
  5. 保存 .pptx 文件

样式处理：
  编译器已完成级联，node.style 是最终合并后的 IRStyle。
  渲染器用 _style_val() 处理 None 值，回退到 _STYLE_DEFAULTS。

降级策略（设计方案第八章）：
  capability 声明了支持的节点类型和效果，
  不支持的特性通过 fallback_map 降级（如 duotone → opacity）。
"""

from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.util import Inches, Pt, Emu, Mm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from ...ir.types import IRDocument, IRNode, IRPosition, IRStyle, NodeType
from ...ir.validator import validate_ir_v2
from ..base import BaseRenderer, RendererCapability

# mm → EMU
MM_TO_EMU = 36000

# 标准 16:9 幻灯片尺寸 (mm)
SLIDE_WIDTH_MM = 254.0   # 10 inches
SLIDE_HEIGHT_MM = 190.5  # 7.5 inches


class PPTXRenderer(BaseRenderer):
    """PowerPoint 渲染器"""

    def __init__(self):
        self._prs: Presentation | None = None

    @property
    def capability(self) -> RendererCapability:
        return RendererCapability(
            supported_node_types={
                NodeType.SLIDE, NodeType.TEXT, NodeType.IMAGE,
                NodeType.SHAPE, NodeType.TABLE, NodeType.CHART,
                NodeType.GROUP, NodeType.VIDEO,
            },
            supported_layout_modes={"absolute", "relative"},
            supported_text_transforms={"arch", "arch_up", "wave", "circle"},
            supported_animations={"slide_up", "fade_in", "scale_in", "fly_in"},
            supported_effects={"shadow", "glow", "gradient_fill", "opacity"},
            fallback_map={
                "duotone": "opacity",  # 滤镜降级为透明度
                "blur": "shadow",      # 模糊降级为阴影
            },
        )

    def render(self, doc: IRDocument, output_path: str | Path) -> Path:
        """渲染 IRDocument 为 .pptx 文件"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 增强版 IR 校验
        validation = validate_ir_v2(doc)
        for issue in validation.issues:
            print(f"[IR {issue.severity.value.upper()}] {issue}")
        if not validation.is_valid:
            print(f"[IR] 校验发现 {len(validation.errors)} 个错误，渲染可能不完整")

        # 创建演示文稿
        self._prs = Presentation()
        self._prs.slide_width = Mm(int(SLIDE_WIDTH_MM))
        self._prs.slide_height = Mm(int(SLIDE_HEIGHT_MM))

        # 渲染每张幻灯片
        for slide_node in doc.children:
            if slide_node.node_type == NodeType.SLIDE:
                self._render_slide(slide_node, doc)

        # 保存
        self._prs.save(str(output_path))
        return output_path

    def _render_slide(self, slide_node: IRNode, doc: IRDocument):
        """渲染单张幻灯片"""
        # 使用空白布局
        slide_layout = self._prs.slide_layouts[6]  # 布局 6 = 空白
        slide = self._prs.slides.add_slide(slide_layout)

        # 设置背景
        bg_data = slide_node.extra.get("background")
        if bg_data:
            self._set_background(slide, bg_data)

        # 渲染元素
        for elem_node in slide_node.children:
            self._render_element(slide, elem_node, doc)

    def _set_background(self, slide, bg_data: dict[str, Any]):
        """设置幻灯片背景"""
        background = slide.background
        fill = background.fill
        fill.solid()

        gradient = bg_data.get("gradient")
        if gradient:
            fill.gradient()
            stops = gradient.get("stops", ["#000000", "#1E293B"])
            if len(stops) >= 2:
                fill.gradient_stops[0].color.rgb = self._hex_to_rgb(stops[0])
                fill.gradient_stops[0].position = 0.0
                fill.gradient_stops[1].color.rgb = self._hex_to_rgb(stops[-1])
                fill.gradient_stops[1].position = 1.0
        elif "color" in bg_data:
            fill.fore_color.rgb = self._hex_to_rgb(bg_data["color"])

    def _render_element(self, slide, node: IRNode, doc: IRDocument):
        """渲染单个元素"""
        if node.node_type == NodeType.TEXT:
            self._render_text(slide, node, doc)
        elif node.node_type == NodeType.SHAPE:
            self._render_shape(slide, node, doc)
        elif node.node_type == NodeType.IMAGE:
            self._render_image(slide, node, doc)
        elif node.node_type == NodeType.TABLE:
            self._render_table(slide, node, doc)
        elif node.node_type == NodeType.GROUP:
            for child in node.children:
                self._render_element(slide, child, doc)
        else:
            # 不支持的节点类型：渲染为占位符
            self._render_placeholder(slide, node)

    def _render_text(self, slide, node: IRNode, doc: IRDocument):
        """渲染文本元素"""
        pos = node.position or IRPosition()
        style = self._resolve_style(node, doc)

        left = Mm(int(pos.x_mm))
        top = Mm(int(pos.y_mm))
        width = Mm(int(pos.width_mm)) if pos.width_mm > 0 else Mm(int(SLIDE_WIDTH_MM - pos.x_mm))
        height = Mm(int(pos.height_mm)) if pos.height_mm > 0 else Mm(int(30))  # 默认高度

        # 居中处理
        if pos.is_center:
            left = Mm(int((SLIDE_WIDTH_MM - (pos.width_mm or 100)) / 2))

        # 添加文本框
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = node.content or ""
        p.alignment = PP_ALIGN.LEFT

        # 应用样式
        if style:
            self._apply_text_style(p, style)

    def _render_shape(self, slide, node: IRNode, doc: IRDocument):
        """渲染形状元素"""
        pos = node.position or IRPosition()
        style = self._resolve_style(node, doc)

        left = Mm(int(pos.x_mm))
        top = Mm(int(pos.y_mm))
        width = Mm(int(pos.width_mm)) if pos.width_mm > 0 else Mm(50)
        height = Mm(int(pos.height_mm)) if pos.height_mm > 0 else Mm(50)

        shape_type = node.extra.get("shape_type", "rectangle")
        mso_shape = self._get_shape_type(shape_type)

        shape = slide.shapes.add_shape(mso_shape, left, top, width, height)

        # 应用填充
        if style and style.fill_color:
            shape.fill.solid()
            shape.fill.fore_color.rgb = self._hex_to_rgb(style.fill_color)
        elif style and style.fill_gradient:
            shape.fill.gradient()
            grad = style.fill_gradient
            stops = grad.get("stops", ["#000000", "#FFFFFF"])
            if len(stops) >= 2:
                shape.fill.gradient_stops[0].color.rgb = self._hex_to_rgb(stops[0])
                shape.fill.gradient_stops[1].color.rgb = self._hex_to_rgb(stops[-1])
        else:
            shape.fill.background()  # 无填充

        # 应用边框
        if node.extra.get("outline"):
            outline = node.extra["outline"]
            shape.line.color.rgb = self._hex_to_rgb(outline.get("color", "#000000"))
            shape.line.width = Pt(outline.get("width", 1))
        else:
            shape.line.fill.background()  # 无边框

        # 文本内容
        if node.content:
            tf = shape.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = node.content
            if style:
                self._apply_text_style(p, style)

    def _render_image(self, slide, node: IRNode, doc: IRDocument):
        """渲染图片元素 — Phase 0 用占位符"""
        pos = node.position or IRPosition()
        left = Mm(int(pos.x_mm))
        top = Mm(int(pos.y_mm))
        width = Mm(int(pos.width_mm)) if pos.width_mm > 0 else Mm(100)
        height = Mm(int(pos.height_mm)) if pos.height_mm > 0 else Mm(75)

        source = node.source
        if isinstance(source, str) and Path(source).exists():
            # 本地文件
            slide.shapes.add_picture(source, left, top, width, height)
        else:
            # 占位符
            self._render_placeholder(slide, node, left, top, width, height)

    def _render_table(self, slide, node: IRNode, doc: IRDocument):
        """渲染表格元素 — Phase 0 基础实现"""
        pos = node.position or IRPosition()
        left = Mm(int(pos.x_mm))
        top = Mm(int(pos.y_mm))
        width = Mm(int(pos.width_mm)) if pos.width_mm > 0 else Mm(200)
        height = Mm(int(pos.height_mm)) if pos.height_mm > 0 else Mm(100)

        # 从 extra 中获取行列数
        rows = node.extra.get("rows", 3)
        cols = node.extra.get("cols", 3)

        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
        table = table_shape.table

        # 填充数据（如果有内联数据）
        inline_data = node.extra.get("data")
        if isinstance(inline_data, list):
            for r, row_data in enumerate(inline_data[:rows]):
                if isinstance(row_data, list):
                    for c, cell_val in enumerate(row_data[:cols]):
                        table.cell(r, c).text = str(cell_val)

    def _render_placeholder(self, slide, node: IRNode, left=None, top=None, width=None, height=None):
        """渲染占位符（不支持的元素类型或缺失资源）"""
        if left is None:
            pos = node.position or IRPosition()
            left = Mm(int(pos.x_mm))
            top = Mm(int(pos.y_mm))
            width = Mm(int(pos.width_mm)) if pos.width_mm > 0 else Mm(100)
            height = Mm(int(pos.height_mm)) if pos.height_mm > 0 else Mm(50)

        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, left, top, width, height
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(0xE0, 0xE0, 0xE0)
        shape.line.color.rgb = RGBColor(0x99, 0x99, 0x99)
        shape.line.dash_style = 2  # 虚线

        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"[{node.node_type.value}]"
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(10)
        p.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    def _resolve_style(self, node: IRNode, doc: IRDocument) -> IRStyle | None:
        """解析节点样式

        编译器已做级联，这里直接使用 node.style。
        回退到 doc.styles 的场景：节点仅设了 style_ref 但未级联（旧代码兼容）。
        """
        if node.style:
            return node.style
        if node.style_ref and node.style_ref in doc.styles:
            return doc.styles[node.style_ref]
        return None

    # 级联后的默认回退值
    _STYLE_DEFAULTS = {
        "font_family": "Microsoft YaHei UI",
        "font_size": 18,
        "font_weight": 400,
        "font_italic": False,
        "font_color": "#000000",
        "fill_opacity": 1.0,
    }

    def _style_val(self, style: IRStyle, field: str):
        """获取样式字段值，None 时回退到默认"""
        val = getattr(style, field, None)
        if val is None:
            return self._STYLE_DEFAULTS.get(field)
        return val

    def _apply_text_style(self, paragraph, style: IRStyle):
        """应用文本样式到段落"""
        font = paragraph.font
        family = self._style_val(style, "font_family")
        size = self._style_val(style, "font_size")
        weight = self._style_val(style, "font_weight")
        italic = self._style_val(style, "font_italic")
        color = self._style_val(style, "font_color")

        if family:
            font.name = family
        if size:
            font.size = Pt(size)
        if weight:
            font.bold = weight >= 700
        if italic is not None:
            font.italic = italic
        if color:
            font.color.rgb = self._hex_to_rgb(color)

    @staticmethod
    def _hex_to_rgb(hex_str: str) -> RGBColor:
        """将 HEX 颜色转为 RGBColor"""
        hex_str = hex_str.lstrip("#")
        # 处理带 alpha 的 HEX（取前 6 位）
        if len(hex_str) == 8:
            hex_str = hex_str[:6]
        if len(hex_str) != 6:
            return RGBColor(0, 0, 0)
        try:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return RGBColor(r, g, b)
        except ValueError:
            return RGBColor(0, 0, 0)

    @staticmethod
    def _get_shape_type(name: str):
        """形状名称 → MSO_SHAPE 枚举"""
        mapping = {
            "rectangle": MSO_SHAPE.RECTANGLE,
            "rounded_rectangle": MSO_SHAPE.ROUNDED_RECTANGLE,
            "circle": MSO_SHAPE.OVAL,
            "oval": MSO_SHAPE.OVAL,
            "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE,
            "diamond": MSO_SHAPE.DIAMOND,
            "arrow": MSO_SHAPE.RIGHT_ARROW,
            "star": MSO_SHAPE.STAR_5_POINT,
        }
        return mapping.get(name, MSO_SHAPE.RECTANGLE)
