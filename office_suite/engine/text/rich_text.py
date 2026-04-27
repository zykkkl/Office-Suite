"""富文本引擎 — 混合样式文本段落处理

设计方案第八章：文本引擎。

富文本支持在同一段落中混合不同样式：
  - 部分文字加粗/斜体
  - 部分文字不同颜色
  - 嵌入行内元素（链接、图标）
  - 上下标
  - 删除线/下划线

渲染器映射：
  - PPTX: 多个 <a:r> Run 元素
  - DOCX: python-docx Run 对象
  - HTML: <span> + <strong> + <em> 等内联标签
  - PDF: reportlab RichText
"""

from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class InlineType(Enum):
    """行内元素类型"""
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    SUPERSCRIPT = "superscript"
    SUBSCRIPT = "subscript"
    LINK = "link"
    ICON = "icon"
    BREAK = "break"    # 换行


@dataclass
class TextRun:
    """文本片段（同一样式的一段文字）"""
    content: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    superscript: bool = False
    subscript: bool = False
    color: str | None = None         # hex
    font_family: str | None = None
    font_size: float | None = None   # pt
    link: str | None = None          # 超链接 URL
    bg_color: str | None = None      # 背景色

    @property
    def is_styled(self) -> bool:
        """是否有非默认样式"""
        return any([
            self.bold, self.italic, self.underline, self.strikethrough,
            self.superscript, self.subscript, self.color, self.font_family,
            self.font_size, self.link, self.bg_color,
        ])


@dataclass
class RichParagraph:
    """富文本段落"""
    runs: list[TextRun] = field(default_factory=list)
    alignment: str = "left"     # left / center / right / justify
    line_height: float = 1.5
    indent_first: float = 0.0   # 首行缩进（pt）
    space_before: float = 0.0   # 段前间距（pt）
    space_after: float = 0.0    # 段后间距（pt）

    def add_run(self, content: str, **kwargs) -> TextRun:
        """添加文本片段"""
        run = TextRun(content=content, **kwargs)
        self.runs.append(run)
        return run

    @property
    def plain_text(self) -> str:
        """获取纯文本"""
        return "".join(r.content for r in self.runs)


@dataclass
class RichDocument:
    """富文本文档"""
    paragraphs: list[RichParagraph] = field(default_factory=list)

    def add_paragraph(self, **kwargs) -> RichParagraph:
        """添加段落"""
        para = RichParagraph(**kwargs)
        self.paragraphs.append(para)
        return para

    @property
    def plain_text(self) -> str:
        """获取纯文本"""
        return "\n".join(p.plain_text for p in self.paragraphs)


# ============================================================
# 解析：从 DSL 格式构建富文本
# ============================================================

def parse_rich_text(raw: str | list | dict) -> RichDocument:
    """从 DSL 格式解析富文本

    支持的 DSL 格式：
      - 纯字符串
      - TextRun 列表：[{"content": "hello", "bold": true}, ...]
      - 段落列表：[{"runs": [...], "alignment": "center"}, ...]

    Args:
        raw: DSL 输入

    Returns:
        RichDocument 实例
    """
    doc = RichDocument()

    if isinstance(raw, str):
        para = doc.add_paragraph()
        para.add_run(raw)
        return doc

    if isinstance(raw, list):
        # 判断是段落列表还是 Run 列表
        if raw and isinstance(raw[0], dict):
            if "runs" in raw[0] or "alignment" in raw[0]:
                # 段落列表
                for item in raw:
                    para = doc.add_paragraph(
                        alignment=item.get("alignment", "left"),
                        line_height=item.get("line_height", 1.5),
                    )
                    for run_data in item.get("runs", []):
                        if isinstance(run_data, str):
                            para.add_run(run_data)
                        elif isinstance(run_data, dict):
                            para.add_run(
                                content=run_data.get("content", ""),
                                bold=run_data.get("bold", False),
                                italic=run_data.get("italic", False),
                                underline=run_data.get("underline", False),
                                color=run_data.get("color"),
                                font_size=run_data.get("font_size"),
                                link=run_data.get("link"),
                            )
            else:
                # Run 列表（单段落）
                para = doc.add_paragraph()
                for run_data in raw:
                    if isinstance(run_data, str):
                        para.add_run(run_data)
                    elif isinstance(run_data, dict):
                        para.add_run(
                            content=run_data.get("content", ""),
                            bold=run_data.get("bold", False),
                            italic=run_data.get("italic", False),
                            color=run_data.get("color"),
                        )

    return doc


# ============================================================
# 渲染器适配
# ============================================================

def to_html(rich: RichDocument) -> str:
    """转换为 HTML

    Returns:
        HTML 字符串
    """
    parts = []
    for para in rich.paragraphs:
        style = f"text-align:{para.alignment};line-height:{para.line_height}"
        if para.space_before:
            style += f";margin-top:{para.space_before}pt"
        if para.space_after:
            style += f";margin-bottom:{para.space_after}pt"

        runs_html = []
        for run in para.runs:
            if run.content == "\n":
                runs_html.append("<br>")
                continue

            text = _escape_html(run.content)
            attrs = []
            style_parts = []

            if run.bold:
                text = f"<strong>{text}</strong>"
            if run.italic:
                text = f"<em>{text}</em>"
            if run.underline:
                text = f"<u>{text}</u>"
            if run.strikethrough:
                text = f"<s>{text}</s>"
            if run.superscript:
                text = f"<sup>{text}</sup>"
            if run.subscript:
                text = f"<sub>{text}</sub>"
            if run.color:
                style_parts.append(f"color:{run.color}")
            if run.bg_color:
                style_parts.append(f"background-color:{run.bg_color}")
            if run.font_size:
                style_parts.append(f"font-size:{run.font_size}pt")
            if run.font_family:
                style_parts.append(f"font-family:{run.font_family}")
            if run.link:
                text = f'<a href="{run.link}">{text}</a>'

            if style_parts:
                text = f'<span style="{";".join(style_parts)}">{text}</span>'

            runs_html.append(text)

        parts.append(f'<p style="{style}">{"".join(runs_html)}</p>')

    return "\n".join(parts)


def to_pptx_runs(para: RichParagraph) -> list[dict[str, Any]]:
    """转换为 PPTX Run 参数列表

    Returns:
        每个 Run 的参数字典列表
    """
    runs = []
    for run in para.runs:
        runs.append({
            "text": run.content,
            "bold": run.bold,
            "italic": run.italic,
            "underline": run.underline,
            "color": run.color,
            "font_size": run.font_size,
            "font_family": run.font_family,
        })
    return runs


def to_docx_runs(para: RichParagraph) -> list[dict[str, Any]]:
    """转换为 DOCX Run 参数列表"""
    return to_pptx_runs(para)  # 参数格式相同


def _escape_html(text: str) -> str:
    """HTML 转义"""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
