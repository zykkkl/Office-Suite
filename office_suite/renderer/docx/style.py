"""DOCX 样式管理 — 从 document.py 提取的样式操作

本模块提供 Word 样式应用的独立接口。

设计方案要求：
  - 使用 Word 内置样式（Heading 1-9, List Bullet 等）
  - 段落级格式（间距、行距、缩进、对齐）
  - Run 级格式（字体、大小、粗体、斜体、颜色）

使用方式：
    from office_suite.renderer.docx.style import apply_paragraph_style, apply_heading_style
"""

from ...ir.types import IRStyle


def apply_paragraph_style(renderer, para, style: IRStyle | None):
    """应用段落 run 级样式（委托给 DOCXRenderer._apply_paragraph_style）"""
    renderer._apply_paragraph_style(para, style)


def apply_heading_style(renderer, heading, style: IRStyle | None):
    """应用标题样式（委托给 DOCXRenderer._apply_heading_style）"""
    renderer._apply_heading_style(heading, style)


def apply_paragraph_format(renderer, para, node):
    """应用段落级格式（委托给 DOCXRenderer._apply_paragraph_format）"""
    renderer._apply_paragraph_format(para, node)
