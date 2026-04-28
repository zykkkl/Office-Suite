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
  - 基础图表 (内联 SVG: bar/column/line/pie)
  - 完整 CSS 样式
  - 不支持动画、艺术字
"""

from pathlib import Path
from html import escape
import math

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
            rendered = self._render_element(child, doc)
            if rendered:
                elements.append(rendered)

        inner = "\n".join(elements)
        bg_css = self._background_css(node.extra.get("background", {}) if node.extra else {})
        return f'<section class="slide" style="{bg_css}">\n{inner}\n</section>'

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
            return self._render_chart(node, doc)
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
        cols = node.extra.get("cols", len(data[0]) if data and isinstance(data[0], list) else 0)

        if not data or cols == 0:
            return ""

        pos_css = self._position_css(node.position)

        lines = [f'<table class="os-table" style="{pos_css}">']
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
        shadow = self._shadow_css(style.shadow if style else None)
        border = self._border_css(style.border if style else None)
        text_css = self._text_style_css(style)
        return f'<div style="{css}{fill}{radius}{shadow}{border}{text_css}">{content}</div>'

    def _render_image(self, node: IRNode) -> str:
        """渲染图片"""
        pos = node.position
        css = self._position_css(pos)
        src = self._image_src(node.source)
        if not src:
            return self._image_fallback(node)
        alt = escape(str(node.extra.get("alt", "")))
        return f'<img src="{escape(src)}" style="{css}object-fit:contain;display:block" alt="{alt}" />'

    def _render_chart(self, node: IRNode, doc: IRDocument) -> str:
        """渲染基础 SVG 图表"""
        pos = node.position
        css = self._position_css(pos)
        data = self._chart_payload(node, doc)
        if not data["categories"] or not data["series"]:
            title = escape(str(data["title"]))
            return f'<div class="chart-empty" style="{css}">Chart unavailable: {title}</div>'

        svg = self._chart_svg(data)
        return f'<div class="chart" style="{css}">{svg}</div>'

    def _text_css(self, style: IRStyle | None, pos: IRPosition | None) -> str:
        """生成文本 CSS"""
        parts = []
        if style:
            parts.extend(self._text_style_parts(style))
            if style.fill_color:
                parts.append(f"background-color:{style.fill_color}")
            if style.shadow:
                parts.append(self._shadow_css(style.shadow))
        if pos:
            parts.extend(self._position_parts(pos))
        return self._join_css(parts)

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

    def _join_css(self, parts: list[str]) -> str:
        return ";".join(p.rstrip(";") for p in parts if p) + (";" if parts else "")

    def _text_style_parts(self, style: IRStyle) -> list[str]:
        parts = []
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
        return parts

    def _text_style_css(self, style: IRStyle | None) -> str:
        return self._join_css(self._text_style_parts(style)) if style else ""

    def _shadow_css(self, shadow: dict | None) -> str:
        if not shadow:
            return ""
        offset = shadow.get("offset", [0, 2])
        blur = shadow.get("blur", 8)
        color = shadow.get("color", "#00000025")
        ox = offset[0] if isinstance(offset, list) and offset else 0
        oy = offset[1] if isinstance(offset, list) and len(offset) > 1 else 2
        return f"box-shadow:{ox}px {oy}px {blur}px {color};"

    def _border_css(self, border: dict | None) -> str:
        if not border:
            return ""
        width = border.get("width", 1)
        color = border.get("color", "#CBD5E1")
        style = border.get("style", "solid")
        return f"border:{width}px {style} {color};"

    def _background_css(self, bg: dict) -> str:
        if not isinstance(bg, dict):
            return ""
        gradient = bg.get("gradient")
        if gradient:
            stops = gradient.get("stops", [])
            angle = gradient.get("angle", 180)
            if len(stops) >= 2:
                if gradient.get("type") == "radial":
                    return f"background:radial-gradient(circle, {', '.join(stops)});"
                return f"background:linear-gradient({angle}deg, {', '.join(stops)});"
        color = bg.get("color")
        if color:
            return f"background:{color};"
        return ""

    def _image_src(self, source) -> str:
        if not isinstance(source, str):
            return ""
        if source.startswith("file://"):
            return source[7:]
        return source

    def _image_fallback(self, node: IRNode) -> str:
        css = self._position_css(node.position)
        label = escape(str(node.source or "image"))
        return f'<div class="image-empty" style="{css}">Image unavailable: {label}</div>'

    def _chart_payload(self, node: IRNode, doc: IRDocument) -> dict:
        categories = []
        series = []
        if node.data_ref and node.data_ref in doc.data:
            ref_val = doc.data[node.data_ref]
            if isinstance(ref_val, dict):
                categories = ref_val.get("categories", [])
                series = ref_val.get("series", [])
        if not categories:
            categories = node.extra.get("categories", [])
        if not series:
            series = node.extra.get("series", [])
        return {
            "title": node.extra.get("title", node.chart_type or "chart"),
            "chart_type": node.chart_type or node.extra.get("chart_type", "bar"),
            "categories": categories,
            "series": series,
            "colors": node.extra.get("colors", [
                "#2563EB", "#16A34A", "#EA580C", "#9333EA",
                "#E11D48", "#0891B2", "#CA8A04", "#4F46E5",
            ]),
        }

    def _chart_svg(self, data: dict) -> str:
        chart_type = data["chart_type"]
        if chart_type == "pie":
            return self._pie_svg(data)
        if chart_type in ("line", "line_marked"):
            return self._line_svg(data)
        return self._bar_svg(data)

    def _max_value(self, series: list[dict]) -> float:
        values = []
        for item in series:
            values.extend(v for v in item.get("values", []) if isinstance(v, (int, float)))
        return max(values) if values else 1.0

    def _svg_title(self, title: str) -> str:
        return f'<text x="18" y="24" class="chart-title">{escape(str(title))}</text>'

    def _bar_svg(self, data: dict) -> str:
        categories = data["categories"]
        series = data["series"]
        colors = data["colors"]
        max_val = max(self._max_value(series), 1.0)
        width, height = 720, 360
        left, top, plot_w, plot_h = 58, 42, 630, 260
        cat_count = max(len(categories), 1)
        series_count = max(len(series), 1)
        group_w = plot_w / cat_count
        bar_w = max(group_w / (series_count + 1.25), 3)
        lines = [f'<svg viewBox="0 0 {width} {height}" role="img">', self._svg_title(data["title"])]
        lines.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" class="axis" />')
        lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" class="axis" />')
        for i in range(1, 5):
            y = top + plot_h - plot_h * i / 4
            lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" class="grid-line" />')
        for ci, cat in enumerate(categories):
            base_x = left + ci * group_w + (group_w - bar_w * series_count) / 2
            for si, item in enumerate(series):
                values = item.get("values", [])
                val = values[ci] if ci < len(values) and isinstance(values[ci], (int, float)) else 0
                bar_h = plot_h * max(val, 0) / max_val
                bx = base_x + si * bar_w
                by = top + plot_h - bar_h
                lines.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w * 0.82:.1f}" height="{bar_h:.1f}" fill="{colors[si % len(colors)]}" rx="3" />')
            lines.append(f'<text x="{left + ci * group_w + group_w / 2:.1f}" y="{height - 18}" class="axis-label" text-anchor="middle">{escape(str(cat))}</text>')
        lines.append("</svg>")
        return "".join(lines)

    def _line_svg(self, data: dict) -> str:
        categories = data["categories"]
        series = data["series"]
        colors = data["colors"]
        max_val = max(self._max_value(series), 1.0)
        width, height = 720, 360
        left, top, plot_w, plot_h = 58, 42, 630, 260
        step = plot_w / max(len(categories) - 1, 1)
        lines = [f'<svg viewBox="0 0 {width} {height}" role="img">', self._svg_title(data["title"])]
        lines.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" class="axis" />')
        lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" class="axis" />')
        for si, item in enumerate(series):
            points = []
            for i, val in enumerate(item.get("values", [])[:len(categories)]):
                if not isinstance(val, (int, float)):
                    continue
                px = left + i * step
                py = top + plot_h - plot_h * max(val, 0) / max_val
                points.append(f"{px:.1f},{py:.1f}")
            if points:
                lines.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{colors[si % len(colors)]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />')
                for point in points:
                    px, py = point.split(",")
                    lines.append(f'<circle cx="{px}" cy="{py}" r="5" fill="{colors[si % len(colors)]}" />')
        for i, cat in enumerate(categories):
            lines.append(f'<text x="{left + i * step:.1f}" y="{height - 18}" class="axis-label" text-anchor="middle">{escape(str(cat))}</text>')
        lines.append("</svg>")
        return "".join(lines)

    def _pie_svg(self, data: dict) -> str:
        categories = data["categories"]
        series = data["series"]
        colors = data["colors"]
        values = series[0].get("values", []) if series else []
        numeric = [float(v) if isinstance(v, (int, float)) and v > 0 else 0.0 for v in values[:len(categories)]]
        total = sum(numeric)
        if total <= 0:
            return '<div class="chart-empty">Chart unavailable: no data</div>'
        width, height = 720, 360
        cx, cy, r = 210, 190, 112
        current = -90.0
        lines = [f'<svg viewBox="0 0 {width} {height}" role="img">', self._svg_title(data["title"])]
        for i, val in enumerate(numeric):
            angle = 360.0 * val / total
            end = current + angle
            large = 1 if angle > 180 else 0
            x1 = cx + r * math.cos(math.radians(current))
            y1 = cy + r * math.sin(math.radians(current))
            x2 = cx + r * math.cos(math.radians(end))
            y2 = cy + r * math.sin(math.radians(end))
            lines.append(f'<path d="M {cx} {cy} L {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f} Z" fill="{colors[i % len(colors)]}" />')
            current = end
        for i, cat in enumerate(categories[:8]):
            pct = numeric[i] / total * 100 if i < len(numeric) else 0
            ly = 92 + i * 26
            lines.append(f'<rect x="390" y="{ly - 11}" width="14" height="14" rx="3" fill="{colors[i % len(colors)]}" />')
            lines.append(f'<text x="414" y="{ly}" class="legend-label">{escape(str(cat))} {pct:.0f}%</text>')
        lines.append("</svg>")
        return "".join(lines)

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
  height: 142.875mm;
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
.os-table {{ background: #FFFFFF; border: 1px solid #E2E8F0; }}
.os-table th, .os-table td {{ line-height: 1.35; }}
.group {{ position: relative; }}
.chart, .chart-empty, .image-empty {{
  background: #FFFFFF;
  border: 1px solid #D8DEE8;
  border-radius: 8px;
  overflow: hidden;
}}
.chart svg {{ width: 100%; height: 100%; display: block; }}
.chart-title {{ font: 700 18px 'Microsoft YaHei UI', 'Segoe UI', sans-serif; fill: #0F172A; }}
.axis {{ stroke: #CBD5E1; stroke-width: 2; }}
.grid-line {{ stroke: #EEF2F7; stroke-width: 1; }}
.axis-label, .legend-label {{ font: 13px 'Microsoft YaHei UI', 'Segoe UI', sans-serif; fill: #64748B; }}
.chart-empty, .image-empty {{
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748B;
  font-size: 12pt;
}}
</style>
</head>
<body>
{body}
</body>
</html>"""
