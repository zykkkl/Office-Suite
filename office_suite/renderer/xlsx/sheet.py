"""XLSX 工作表渲染 — 从 workbook.py 提取的工作表级操作

本模块提供工作表渲染的独立接口。

设计方案要求：
  - 工作表创建和管理
  - 单元格写入和样式
  - 单元格合并
  - 数字格式
  - 条件格式
  - 冻结窗格

使用方式：
    from office_suite.renderer.xlsx.sheet import render_to_sheet, apply_cell_style
"""

from ...ir.types import IRNode, IRDocument


def render_to_sheet(renderer, node: IRNode, ws, doc: IRDocument):
    """将节点渲染到 Sheet（委托给 XLSXRenderer._render_node_to_sheet）"""
    renderer._render_node_to_sheet(node, ws, doc)


def render_text(renderer, node: IRNode, ws):
    """渲染文本到单元格（委托给 XLSXRenderer._render_text）"""
    renderer._render_text(node, ws)


def render_table(renderer, node: IRNode, ws):
    """渲染表格到 Sheet（委托给 XLSXRenderer._render_table）"""
    renderer._render_table(node, ws)


def apply_cell_style(renderer, cell, style):
    """应用单元格样式（委托给 XLSXRenderer._apply_cell_style）"""
    renderer._apply_cell_style(cell, style)
