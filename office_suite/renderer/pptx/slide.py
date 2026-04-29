"""PPTX 幻灯片渲染 — 从 deck.py 提取的幻灯片级操作

本模块提供幻灯片渲染的独立接口，内部委托给 PPTXRenderer。
deck.py 中的 _render_slide / _get_layout_index / _set_background 对应此处。

使用方式：
    from office_suite.renderer.pptx.slide import render_slide
    render_slide(renderer, slide_node, doc)
"""

from ...ir.types import IRNode, IRDocument


def render_slide(renderer, slide_node: IRNode, doc: IRDocument):
    """渲染单张幻灯片（委托给 PPTXRenderer._render_slide）"""
    renderer._render_slide(slide_node, doc)


def get_layout_index(renderer, layout_name: str) -> int:
    """获取母版布局索引"""
    return renderer._get_layout_index(layout_name)


def set_background(renderer, slide, bg_data: dict):
    """设置幻灯片背景"""
    renderer._set_background(slide, bg_data)
