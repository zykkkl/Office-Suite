"""图表卡片组件 — 标题 + 图表 + 注释

参数:
  title: str — 卡片标题
  chart_type: str — 图表类型 (bar/line/pie/column)
  categories: list — 分类
  series: list[dict] — 数据系列 [{name, values}]
  caption: str — 注释文本 (可选)
  position: dict — 位置 (可选, 默认 x=10mm y=10mm w=220mm h=150mm)
"""

from ...ir.types import IRNode, NodeType, IRPosition, IRStyle
from ..registry import register_component


def _generate(params: dict) -> list[IRNode]:
    title = params.get("title", "图表")
    chart_type = params.get("chart_type", "bar")
    categories = params.get("categories", [])
    series = params.get("series", [])
    caption = params.get("caption", "")
    pos = params.get("position", {})
    x = pos.get("x", 10)
    y = pos.get("y", 10)
    w = pos.get("width", 220)
    h = pos.get("height", 150)

    nodes = []

    # 标题
    nodes.append(IRNode(
        node_type=NodeType.TEXT,
        content=title,
        style=IRStyle(font_size=22, font_weight=700),
        position=IRPosition(x_mm=x, y_mm=y, width_mm=w, height_mm=12),
    ))

    # 图表
    nodes.append(IRNode(
        node_type=NodeType.CHART,
        chart_type=chart_type,
        extra={
            "title": title,
            "categories": categories,
            "series": series,
        },
        position=IRPosition(x_mm=x, y_mm=y + 16, width_mm=w, height_mm=h - 30),
    ))

    # 注释
    if caption:
        nodes.append(IRNode(
            node_type=NodeType.TEXT,
            content=caption,
            style=IRStyle(font_size=10, font_color="#94A3B8"),
            position=IRPosition(x_mm=x, y_mm=y + h - 10, width_mm=w, height_mm=8),
        ))

    return nodes


register_component(
    name="chart_card",
    description="图表卡片: 标题 + 图表 + 注释",
    generator=_generate,
    param_schema={
        "title": {"type": "str", "default": "图表"},
        "chart_type": {"type": "str", "default": "bar"},
        "categories": {"type": "list", "required": True},
        "series": {"type": "list", "required": True},
        "caption": {"type": "str", "default": ""},
        "position": {"type": "dict", "default": {}},
    },
)
