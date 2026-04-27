"""HTML 渲染器 — IRDocument → .html 文件

将 IR 渲染为独立的 HTML 文件（含内联 CSS）。

架构位置：ir/compiler.py → IRDocument → [本文件] → .html 文件

渲染流程：
  1. 生成 HTML 骨架 + 内联 CSS
  2. 遍历 IRDocument.children (SECTION 或 SLIDE)
  3. 每个节映射为一个 <section>
  4. 元素按类型渲染为 HTML 元素
  5. 写入 .html 文件

HTML 能力：
  - 文本/标题 (h1-h6, p)
  - 表格 (table)
  - 图片 (img)
  - 形状 (div + CSS)
  - 图表 (占位符 div)
  - 完整 CSS 样式
  - 不支持动画、艺术字
"""

from pathlib import Path
from html import escape

from ...ir.types import IRDocument, IRNode, IRPosition, IRStyle, NodeType
from ...ir.validator import validate_ir_v2
from ..base import BaseRenderer, RendererCapability


class HTMLRenderer(BaseRenderer):
    """HTML 渲染器"""

    @property
    def capability(self) -> RendererCapability:
        return RendererCapability(
            supported_node_types={
                NodeType.SLIDE, NodeType.SECTION, NodeType.TEXT,
                NodeType.IMAGE, NodeType.TABLE, NodeType.SHAPE,
                NodeType.CHART, NodeType.GROUP,
            },
            supported_layout_modes={"absolute", "relative"},
            supported_text_transforms=set(),
            supported_animations=set(),
            supported_effects={"shadow", "gradient_fill"},
            fallback_map={
                "arch": "plain_text",
                "wave": "plain_text",
            },
        )

    def render(self, doc: IRDocument, output_path: str | Path) -> Path:
        """渲染 IRDocument 为 .html 文件"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 校验
        validation = validate_ir_v2(doc)
        for issue in validation.issues:
            print(f"[IR {issue.severity.value.upper()}] {issue}")

        sections = []
        for node in doc.children:
            if node.node_type in (NodeType.SLIDE, NodeType.SECTION):
                sections.append(self._render_slide(node, doc))

        html = self._build_html(sections, doc)
        output_path.write_text(html, encoding="utf-8")
        return output_path

    def _render_slide(self, node: IRNode, doc: IRDocument) -> str:
        """渲染一张幻灯片/节为 <section>"""
        elements = []
        for child in node.children:
            elements.append(self._render_element(child, doc))

        inner = "\n".join(elements)
        return f'<section class="slide">\n{inner}\n</section>'

    def _render_element(self, node: IRNode, doc: IRDocument) -> str:
        """按节点类型分派"""
        if node.node_type == NodeType.TEXT:
            return self._render_text(node)
        elif node.node_type == NodeType.TABLE:
            return self._render_table(node)
        elif node.node_type == NodeType.SHAPE:
            return self._render_shape(node)
        elif node.node_type == NodeType.IMAGE:
            return self._render_image(node)
        elif node.node_type == NodeType.CHART:
            return self._render_chart(node)
        elif node.node_type == NodeType.GROUP:
            children = "\n".join(self._render_element(c, doc) for c in node.children)
            return f'<div class="group">\n{children}\n</div>'
        else:
            return f'<div class="unsupported">[{node.node_type.value}]</div>'

    def _render_text(self, node: IRNode) -> str:
        """渲染文本"""
        content = escape(node.content or "")
        if not content.strip():
            return ""

        style = node.style
        pos = node.position

        # 判断标签
        font_size = style.font_size if style and style.font_size else 14
        if font_size >= 28:
            tag = "h1"
        elif font_size >= 22:
            tag = "h2"
        elif font_size >= 18:
            tag = "h3"
        else:
            tag = "p"

        css = self._text_css(style, pos)
        return f'<{tag} style="{css}">{content}</{tag}>'

    def _render_table(self, node: IRNode) -> str:
        """渲染表格"""
        data = node.extra.get("data", [])
        rows = node.extra.get("rows", len(data))
        cols = node.extra.get("cols", len(data[0]) if data else 0)

        if not data:
            return ""

        pos_css = self._position_css(node.position)

        lines = [f'<table style="border-collapse:collapse;{pos_css}">']
        for r, row in enumerate(data[:rows]):
            if not isinstance(row, list):
                continue
            lines.append("  <tr>")
            for c, cell_val in enumerate(row[:cols]):
                cell = escape(str(cell_val))
                if r == 0:
                    lines.append(f'    <th style="background:#1E293B;color:#FFF;padding:6px 10px;text-align:left;font-weight:600">{cell}</th>')
                else:
                    bg = "#F1F5F9" if r % 2 == 0 else "#FFFFFF"
                    lines.append(f'    <td style="background:{bg};padding:6px 10px;border-bottom:1px solid #E2E8F0">{cell}</td>')
            lines.append("  </tr>")
        lines.append("</table>")
        return "\n".join(lines)

    def _render_shape(self, node: IRNode) -> str:
        """渲染形状 → div + CSS"""
        style = node.style
        pos = node.position
        css = self._position_css(pos)

        fill = ""
        if style and style.fill_color:
            fill = f"background-color:{style.fill_color};"

        shape_type = node.extra.get("shape_type", "rectangle")
        radius = ""
        if shape_type in ("circle", "ellipse"):
            radius = "border-radius:50%;"
        elif shape_type == "rounded_rectangle":
            radius = "border-radius:8px;"

        content = escape(node.content or "")
        return f'<div style="{css}{fill}{radius}">{content}</div>'

    def _render_image(self, node: IRNode) -> str:
        """渲染图片"""
        pos = node.position
        css = self._position_css(pos)
        src = escape(str(node.source or ""))
        return f'<img src="{src}" style="{css}object-fit:contain" alt="" />'

    def _render_chart(self, node: IRNode) -> str:
        """渲染图表占位符"""
        pos = node.position
        css = self._position_css(pos)
        title = escape(node.extra.get("title", node.chart_type or "chart"))
        return f'<div style="{css}background:#EFF6FF;border:1px solid #BFDBFE;display:flex;align-items:center;justify-content:center;color:#3B82F6;font-family:sans-serif">[Chart: {title}]</div>'

    def _text_css(self, style: IRStyle | None, pos: IRPosition | None) -> str:
        """生成文本 CSS"""
        parts = []
        if style:
            if style.font_family:
                parts.append(f"font-family:'{style.font_family}'")
            if style.font_size:
                parts.append(f"font-size:{style.font_size}pt")
            if style.font_weight:
                parts.append(f"font-weight:{style.font_weight}")
            if style.font_italic:
                parts.append("font-style:italic")
            if style.font_color:
                parts.append(f"color:{style.font_color}")
            if style.fill_color:
                parts.append(f"background-color:{style.fill_color}")
        if pos:
            parts.extend(self._position_parts(pos))
        return ";".join(parts)

    def _position_css(self, pos: IRPosition | None) -> str:
        """生成位置 CSS"""
        if not pos:
            return ""
        parts = self._position_parts(pos)
        return ";".join(parts) + ";" if parts else ""

    def _position_parts(self, pos: IRPosition) -> list[str]:
        """位置 CSS 部件"""
        parts = []
        if pos.x_mm > 0 or pos.y_mm > 0:
            parts.append("position:absolute")
            parts.append(f"left:{pos.x_mm:.1f}mm")
            parts.append(f"top:{pos.y_mm:.1f}mm")
        if pos.width_mm > 0:
            parts.append(f"width:{pos.width_mm:.1f}mm")
        if pos.height_mm > 0:
            parts.append(f"height:{pos.height_mm:.1f}mm")
        return parts

    def _build_html(self, sections: list[str], doc: IRDocument) -> str:
        """构建完整 HTML"""
        body = "\n".join(sections)
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Office Suite 4.0 Output</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
  font-size: 14pt;
  color: #0F172A;
  background: #F8FAFC;
}}
.slide {{
  position: relative;
  width: 254mm;
  height: 190mm;
  margin: 20px auto;
  background: #FFFFFF;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  overflow: hidden;
  page-break-after: always;
}}
h1 {{ font-size: 28pt; font-weight: 700; margin: 8px 0; }}
h2 {{ font-size: 22pt; font-weight: 700; margin: 6px 0; }}
h3 {{ font-size: 18pt; font-weight: 600; margin: 4px 0; }}
p {{ margin: 4px 0; line-height: 1.5; }}
table {{ border-collapse: collapse; }}
.group {{ position: relative; }}
</style>
</head>
<body>
{body}
</body>
</html>"""
