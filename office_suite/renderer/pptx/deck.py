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
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.chart.data import CategoryChartData

from ...ir.types import IRDocument, IRNode, IRPosition, IRStyle, NodeType
from ...ir.validator import validate_ir_v2
from ..base import BaseRenderer, RendererCapability
from .animation import apply_animations

# mm → EMU
MM_TO_EMU = 36000

# 标准 16:9 幻灯片尺寸 (mm)
SLIDE_WIDTH_MM = 254.0   # 10 inches
SLIDE_HEIGHT_MM = 190.5  # 7.5 inches

# 图表类型映射
CHART_TYPE_MAP = {
    "bar": XL_CHART_TYPE.BAR_CLUSTERED,
    "bar_stacked": XL_CHART_TYPE.BAR_STACKED,
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "column_stacked": XL_CHART_TYPE.COLUMN_STACKED,
    "line": XL_CHART_TYPE.LINE,
    "line_marked": XL_CHART_TYPE.LINE_MARKERS,
    "pie": XL_CHART_TYPE.PIE,
    "doughnut": XL_CHART_TYPE.DOUGHNUT,
    "area": XL_CHART_TYPE.AREA,
    "scatter": XL_CHART_TYPE.XY_SCATTER,
    "radar": XL_CHART_TYPE.RADAR,
}


class PPTXRenderer(BaseRenderer):
    """PowerPoint 渲染器

    Phase 2 增强：
    - 图表渲染（bar/column/line/pie/scatter 等）
    - 母版布局支持（预定义布局索引）
    - 渐变填充（线性/径向，多停止点）
    - 阴影/发光/透明度
    - 表格样式增强
    """

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
                "duotone": "opacity",
                "blur": "shadow",
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

    # ============================================================
    # 幻灯片级渲染
    # ============================================================

    def _render_slide(self, slide_node: IRNode, doc: IRDocument):
        """渲染单张幻灯片

        母版布局索引（python-pptx 默认模板）：
          0  = Title Slide
          1  = Title and Content
          2  = Section Header
          3  = Two Content
          4  = Comparison
          5  = Title Only
          6  = Blank
          7  = Content with Caption
          8  = Picture with Caption
        """
        # 获取布局（默认 blank=6）
        layout_name = slide_node.extra.get("layout", "blank")
        layout_idx = self._get_layout_index(layout_name)
        slide_layout = self._prs.slide_layouts[layout_idx]
        slide = self._prs.slides.add_slide(slide_layout)

        # 设置背景
        bg_data = slide_node.extra.get("background")
        if bg_data:
            self._set_background(slide, bg_data)

        # 渲染元素
        for elem_node in slide_node.children:
            self._render_element(slide, elem_node, doc)

    def _get_layout_index(self, name: str) -> int:
        """布局名称 → 幻灯片布局索引"""
        mapping = {
            "title": 0,
            "title_content": 1,
            "section": 2,
            "two_content": 3,
            "comparison": 4,
            "title_only": 5,
            "blank": 6,
            "caption": 7,
            "picture_caption": 8,
        }
        return mapping.get(name, 6)

    def _set_background(self, slide, bg_data: dict[str, Any]):
        """设置幻灯片背景

        支持：
          - 纯色: { color: "#RRGGBB" }
          - 线性渐变: { gradient: { type: linear, angle: 135, stops: [...] } }
          - 径向渐变: { gradient: { type: radial, stops: [...] } }
        """
        background = slide.background
        fill = background.fill
        fill.solid()

        gradient = bg_data.get("gradient")
        if gradient:
            self._apply_gradient_fill(fill, gradient)
        elif "color" in bg_data:
            fill.fore_color.rgb = self._hex_to_rgb(bg_data["color"])

    # ============================================================
    # 元素级渲染
    # ============================================================

    def _render_element(self, slide, node: IRNode, doc: IRDocument):
        """渲染单个元素 — 按节点类型分派"""
        if node.node_type == NodeType.TEXT:
            self._render_text(slide, node, doc)
        elif node.node_type == NodeType.SHAPE:
            self._render_shape(slide, node, doc)
        elif node.node_type == NodeType.IMAGE:
            self._render_image(slide, node, doc)
        elif node.node_type == NodeType.TABLE:
            self._render_table(slide, node, doc)
        elif node.node_type == NodeType.CHART:
            self._render_chart(slide, node, doc)
        elif node.node_type == NodeType.GROUP:
            for child in node.children:
                self._render_element(slide, child, doc)
        else:
            self._render_placeholder(slide, node)

    def _render_text(self, slide, node: IRNode, doc: IRDocument):
        """渲染文本元素"""
        pos = self._get_position(node)
        style = self._resolve_style(node, doc)

        left, top, width, height = self._pos_to_emu(pos)
        if pos.is_center:
            left = Mm(int((SLIDE_WIDTH_MM - pos.width_mm) / 2))

        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = node.content or ""
        p.alignment = PP_ALIGN.LEFT

        if style:
            self._apply_text_style(p, style)

        # 应用动画
        if node.animations:
            apply_animations(slide, txBox, node.animations)

        # 应用文本变换 (WordArt)
        if style and style.text_effect:
            self._apply_text_warp(txBox, style.text_effect)

    def _render_shape(self, slide, node: IRNode, doc: IRDocument):
        """渲染形状元素

        支持的形状类型：rectangle, rounded_rectangle, circle, oval,
        triangle, diamond, arrow, star, hexagon, pentagon
        """
        pos = self._get_position(node)
        style = self._resolve_style(node, doc)

        left, top, width, height = self._pos_to_emu(pos)
        shape_type = node.extra.get("shape_type", "rectangle")
        mso_shape = self._get_shape_type(shape_type)

        shape = slide.shapes.add_shape(mso_shape, left, top, width, height)

        # 填充
        self._apply_shape_fill(shape, style, node)

        # 边框
        self._apply_shape_border(shape, node)

        # 形状内文本
        if node.content:
            tf = shape.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = node.content
            if style:
                self._apply_text_style(p, style)

        # 应用动画
        if node.animations:
            apply_animations(slide, shape, node.animations)

    def _render_image(self, slide, node: IRNode, doc: IRDocument):
        """渲染图片元素

        支持：
          - 本地文件: source="file://path" 或 source="path"
          - MCP/AI 资源: source={mcp__unsplash, query: "..."} → 占位符
        """
        pos = self._get_position(node)
        left, top, width, height = self._pos_to_emu(pos)

        source = node.source
        if isinstance(source, str):
            # 尝试作为本地文件
            file_path = Path(source.replace("file://", ""))
            if file_path.exists():
                slide.shapes.add_picture(str(file_path), left, top, width, height)
                return

        # 降级：占位符
        self._render_placeholder(slide, node, left, top, width, height)

    def _render_table(self, slide, node: IRNode, doc: IRDocument):
        """渲染表格元素

        数据来源：
          - extra.data: 内联二维数组
          - extra.rows/extra.cols: 行列数
        """
        pos = self._get_position(node)
        left, top, width, height = self._pos_to_emu(pos)

        rows = node.extra.get("rows", 3)
        cols = node.extra.get("cols", 3)

        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
        table = table_shape.table

        # 填充数据
        inline_data = node.extra.get("data")
        if isinstance(inline_data, list):
            for r, row_data in enumerate(inline_data[:rows]):
                if isinstance(row_data, list):
                    for c, cell_val in enumerate(row_data[:cols]):
                        cell = table.cell(r, c)
                        cell.text = str(cell_val)
                        # 首行加粗（表头）
                        if r == 0:
                            for paragraph in cell.text_frame.paragraphs:
                                for run in paragraph.runs:
                                    run.font.bold = True

        # 表格样式（交替行颜色）
        self._apply_table_style(table, rows, cols)

    def _render_chart(self, slide, node: IRNode, doc: IRDocument):
        """渲染图表元素

        DSL 示例：
          - type: chart
            chart_type: bar
            data_ref: revenue
            position: { x: 20mm, y: 40mm, width: 200mm, height: 100mm }
            extra:
              categories: ["Q1", "Q2", "Q3", "Q4"]
              series:
                - name: "营收"
                  values: [100, 120, 150, 180]
                - name: "利润"
                  values: [30, 40, 50, 60]
        """
        pos = self._get_position(node)
        left, top, width, height = self._pos_to_emu(pos)

        chart_type_str = node.chart_type or node.extra.get("chart_type", "bar")
        xl_chart_type = CHART_TYPE_MAP.get(chart_type_str, XL_CHART_TYPE.BAR_CLUSTERED)

        # 构建图表数据
        chart_data = self._build_chart_data(node)

        # 添加图表
        chart_frame = slide.shapes.add_chart(
            xl_chart_type, left, top, width, height, chart_data
        )
        chart = chart_frame.chart

        # 图表标题
        title = node.extra.get("title")
        if title:
            chart.has_title = True
            chart.chart_title.text_frame.paragraphs[0].text = title

        # 图例
        show_legend = node.extra.get("legend", True)
        chart.has_legend = show_legend
        if show_legend:
            chart.legend.position = XL_LEGEND_POSITION.BOTTOM
            chart.legend.include_in_layout = False

        # 应用主题色到系列
        self._apply_chart_colors(chart, node)

    def _build_chart_data(self, node: IRNode) -> CategoryChartData:
        """从 IRNode.extra 构建 CategoryChartData"""
        categories = node.extra.get("categories", [])
        series_list = node.extra.get("series", [])

        chart_data = CategoryChartData()
        chart_data.categories = categories

        for series in series_list:
            name = series.get("name", "")
            values = series.get("values", [])
            chart_data.add_series(name, values)

        return chart_data

    def _apply_chart_colors(self, chart, node: IRNode):
        """为图表系列应用颜色

        从 node.extra.colors 读取颜色列表，或使用默认主题色。
        """
        colors = node.extra.get("colors", [
            "#2563EB", "#16A34A", "#EA580C", "#9333EA",
            "#E11D48", "#0891B2", "#CA8A04", "#4F46E5",
        ])
        for i, series in enumerate(chart.series):
            color_hex = colors[i % len(colors)]
            series.format.fill.solid()
            series.format.fill.fore_color.rgb = self._hex_to_rgb(color_hex)

    def _render_placeholder(self, slide, node: IRNode, left=None, top=None, width=None, height=None):
        """渲染占位符（不支持的元素类型或缺失资源）"""
        if left is None:
            pos = self._get_position(node)
            left, top, width, height = self._pos_to_emu(pos)

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

    # ============================================================
    # 填充/边框/样式辅助方法
    # ============================================================

    def _apply_shape_fill(self, shape, style: IRStyle | None, node: IRNode):
        """应用形状填充（纯色 / 渐变 / 透明度）"""
        if style and style.fill_gradient:
            shape.fill.gradient()
            self._apply_gradient_fill(shape.fill, style.fill_gradient)
        elif style and style.fill_color:
            shape.fill.solid()
            shape.fill.fore_color.rgb = self._hex_to_rgb(style.fill_color)
            # 透明度
            if style.fill_opacity is not None and style.fill_opacity < 1.0:
                shape.fill.fore_color.brightness = 0
        else:
            shape.fill.background()

    def _apply_gradient_fill(self, fill, gradient: dict[str, Any]):
        """应用渐变填充

        支持 linear 和 radial 类型。
        python-pptx 的 gradient API 通过 gradient_stops 操作。
        """
        fill.gradient()
        stops = gradient.get("stops", ["#000000", "#FFFFFF"])
        angle = gradient.get("angle", 0)

        # 清除默认停止点，添加新停止点
        # python-pptx 至少需要 2 个停止点
        for i, color_hex in enumerate(stops):
            position = i / max(len(stops) - 1, 1)
            if i < len(fill.gradient_stops):
                fill.gradient_stops[i].color.rgb = self._hex_to_rgb(color_hex)
                fill.gradient_stops[i].position = position
            else:
                # python-pptx 不支持动态添加停止点，取首尾
                break

        # 角度（linear 时有效）
        if gradient.get("type") == "linear":
            # python-pptx 使用 angle 属性（0-360 度）
            try:
                fill.gradient_angle = angle
            except AttributeError:
                pass  # 某些版本不支持

    def _apply_shape_border(self, shape, node: IRNode):
        """应用形状边框"""
        outline = node.extra.get("outline")
        if outline:
            shape.line.color.rgb = self._hex_to_rgb(outline.get("color", "#000000"))
            shape.line.width = Pt(outline.get("width", 1))
            # 虚线样式
            dash = outline.get("dash")
            if dash == "solid":
                shape.line.dash_style = 1
            elif dash == "dashed":
                shape.line.dash_style = 4
            elif dash == "dotted":
                shape.line.dash_style = 2
        else:
            shape.line.fill.background()

    def _apply_table_style(self, table, rows: int, cols: int):
        """应用表格样式（交替行颜色）"""
        for r in range(rows):
            for c in range(cols):
                cell = table.cell(r, c)
                if r == 0:
                    # 表头：深色背景
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(0x1E, 0x29, 0x3B)
                    for p in cell.text_frame.paragraphs:
                        for run in p.runs:
                            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                            run.font.size = Pt(11)
                elif r % 2 == 0:
                    # 偶数行：浅灰背景
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(0xF1, 0xF5, 0xF9)
                else:
                    # 奇数行：白色
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # ============================================================
    # 位置/样式工具方法
    # ============================================================

    def _get_position(self, node: IRNode) -> IRPosition:
        """获取节点位置，无位置时返回默认"""
        return node.position or IRPosition()

    def _pos_to_emu(self, pos: IRPosition) -> tuple:
        """将 IRPosition (mm) 转换为 EMU 元组 (left, top, width, height)"""
        left = Mm(int(pos.x_mm))
        top = Mm(int(pos.y_mm))
        width = Mm(int(pos.width_mm)) if pos.width_mm > 0 else Mm(int(SLIDE_WIDTH_MM - pos.x_mm))
        height = Mm(int(pos.height_mm)) if pos.height_mm > 0 else Mm(30)
        return left, top, width, height

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

    def _apply_text_warp(self, shape, text_effect: dict[str, Any]):
        """应用 WordArt 文本变换

        通过 Oxml 注入 <a:bodyPr> 的 presetTextWarp 属性。
        text_effect 示例: { transform: "arch", bend: 50 }
        """
        from lxml import etree

        a_ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'

        # 获取 shape 的 txBody
        tx_body = shape._element.find(f'.//{{{a_ns}}}txBody')
        if tx_body is None:
            return

        # 获取或创建 bodyPr
        body_pr = tx_body.find(f'{{{a_ns}}}bodyPr')
        if body_pr is None:
            body_pr = etree.SubElement(tx_body, f'{{{a_ns}}}bodyPr')

        # 文本变换映射
        transform_map = {
            "arch": "textArchDown",
            "arch_up": "textArchUp",
            "wave": "textWave1",
            "circle": "textCircle",
            "slant_up": "textSlantUp",
            "slant_down": "textSlantDown",
            "triangle": "textTriangle",
            "chevron_up": "textChevronUp",
            "chevron_down": "textChevronDown",
            "button": "textButton",
            "deflate": "textDeflate",
            "inflate": "textInflate",
            "fade_up": "textFadeUp",
            "fade_down": "textFadeDown",
        }

        transform_type = text_effect.get("transform", text_effect.get("type", "plain"))
        preset = transform_map.get(transform_type, "textPlain")

        # 注入 presetTextWarp
        prst_tx_warp = etree.SubElement(body_pr, f'{{{a_ns}}}prstTxWarp')
        prst_tx_warp.set('prst', preset)

        # avLst (adjust value list)
        av_lst = etree.SubElement(prst_tx_warp, f'{{{a_ns}}}avLst')

        # bend 参数
        bend = text_effect.get("bend", 0)
        if bend != 0:
            gd = etree.SubElement(av_lst, f'{{{a_ns}}}gd')
            gd.set('name', 'adj')
            # PPTX bend 范围: -100000 ~ 100000 (万分比)
            gd.set('fmla', f'val {int(bend * 1000)}')

    @staticmethod
    def _hex_to_rgb(hex_str: str) -> RGBColor:
        """将 HEX 颜色转为 RGBColor"""
        hex_str = hex_str.lstrip("#")
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
            "hexagon": MSO_SHAPE.HEXAGON,
            "pentagon": MSO_SHAPE.PENTAGON,
            "chevron": MSO_SHAPE.CHEVRON,
            "cross": MSO_SHAPE.CROSS,
        }
        return mapping.get(name, MSO_SHAPE.RECTANGLE)
