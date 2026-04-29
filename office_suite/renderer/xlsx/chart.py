"""XLSX 图表渲染 — 从 workbook.py 提取的图表操作

本模块提供 Excel 图表渲染的独立接口。

支持图表类型：
  - bar: 条形图
  - column: 柱状图
  - line: 折线图
  - pie: 饼图
  - scatter: 散点图

使用方式：
    from office_suite.renderer.xlsx.chart import render_chart, CHART_CLASS_MAP
"""

from openpyxl.chart import BarChart, LineChart, PieChart, ScatterChart

# 图表类型映射
CHART_CLASS_MAP = {
    "bar": BarChart,
    "column": BarChart,
    "line": LineChart,
    "pie": PieChart,
    "scatter": ScatterChart,
}


def render_chart(renderer, node, ws):
    """渲染图表到 Sheet（委托给 XLSXRenderer._render_chart）"""
    renderer._render_chart(node, ws)
