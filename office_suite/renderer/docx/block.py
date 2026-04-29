"""DOCX 块级元素渲染 — 从 document.py 提取的块级操作

本模块提供文档块级元素（段落、列表、表格）渲染的独立接口。

设计方案要求：
  - 段落渲染（对齐、间距、行距、缩进）
  - 列表渲染（有序/无序）
  - 表格渲染
  - 图片渲染
  - 形状降级

使用方式：
    from office_suite.renderer.docx.block import render_text, render_list_item
"""

from ...ir.types import IRNode, IRDocument


def render_text(renderer, node: IRNode, doc: IRDocument):
    """渲染文本元素（委托给 DOCXRenderer._render_text）"""
    renderer._render_text(node, doc)


def render_list_item(renderer, node: IRNode, content: str, style, list_type: str):
    """渲染列表项（委托给 DOCXRenderer._render_list_item）"""
    renderer._render_list_item(node, content, style, list_type)


def render_table(renderer, node: IRNode, doc: IRDocument):
    """渲染表格（委托给 DOCXRenderer._render_table）"""
    renderer._render_table(node, doc)


def render_image(renderer, node: IRNode, doc: IRDocument):
    """渲染图片（委托给 DOCXRenderer._render_image）"""
    renderer._render_image(node, doc)


def render_shape(renderer, node: IRNode, doc: IRDocument):
    """渲染形状（委托给 DOCXRenderer._render_shape）"""
    renderer._render_shape(node, doc)
