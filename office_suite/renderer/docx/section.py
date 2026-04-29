"""DOCX 节管理 — 从 document.py 提取的节级操作

本模块提供文档节（Section）渲染的独立接口。

设计方案要求：
  - 节分隔符类型（连续、新页、偶数/奇数页）
  - 节级页面属性（纸张大小、方向、边距）
  - 页眉/页脚

当前实现：
  - 分节符类型：continuous / new_page / even_page / odd_page
  - 页面属性：a4/a3/letter/legal + portrait/landscape

使用方式：
    from office_suite.renderer.docx.section import render_section, add_section_break
"""

from ...ir.types import IRNode, IRDocument


def render_section(renderer, node: IRNode, doc: IRDocument, add_break: bool = False):
    """渲染 SECTION 节点（委托给 DOCXRenderer._render_section）"""
    renderer._render_section(node, doc, add_break=add_break)


def add_section_break(renderer, break_type: str):
    """添加分节符（委托给 DOCXRenderer._add_section_break）"""
    renderer._add_section_break(break_type)


def apply_section_properties(renderer, page_size: str, orientation: str):
    """应用节属性（委托给 DOCXRenderer._apply_section_properties）"""
    renderer._apply_section_properties(page_size, orientation)
