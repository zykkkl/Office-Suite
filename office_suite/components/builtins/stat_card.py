"""统计卡片组件 — 大数字 + 标签 + 趋势指示

参数:
  value: str — 统计值 (如 "¥128K", "95%", "1,234")
  label: str — 标签 (如 "月营收", "转化率")
  trend: str — 趋势 ("up" / "down" / "flat", 可选)
  trend_value: str — 趋势值 (如 "+12%", 可选)
  position: dict — 位置 (可选)
"""

from ...ir.types import IRNode, NodeType, IRPosition, IRStyle
from ..registry import register_component


TREND_COLORS = {
    "up": "#10B981",
    "down": "#EF4444",
    "flat": "#6B7280",
}


def _generate(params: dict) -> list[IRNode]:
    value = params.get("value", "0")
    label = params.get("label", "")
    trend = params.get("trend", "")
    trend_value = params.get("trend_value", "")
    pos = params.get("position", {})
    x = pos.get("x", 10)
    y = pos.get("y", 10)
    w = pos.get("width", 60)
    h = pos.get("height", 40)

    nodes = []

    # 大数字
    nodes.append(IRNode(
        node_type=NodeType.TEXT,
        content=value,
        style=IRStyle(font_size=36, font_weight=700, font_color="#0F172A"),
        position=IRPosition(x_mm=x, y_mm=y, width_mm=w, height_mm=16),
    ))

    # 标签
    if label:
        nodes.append(IRNode(
            node_type=NodeType.TEXT,
            content=label,
            style=IRStyle(font_size=12, font_color="#6B7280"),
            position=IRPosition(x_mm=x, y_mm=y + 18, width_mm=w, height_mm=8),
        ))

    # 趋势
    if trend and trend_value:
        arrow = {"up": "↑", "down": "↓", "flat": "→"}.get(trend, "")
        color = TREND_COLORS.get(trend, "#6B7280")
        nodes.append(IRNode(
            node_type=NodeType.TEXT,
            content=f"{arrow} {trend_value}",
            style=IRStyle(font_size=11, font_weight=500, font_color=color),
            position=IRPosition(x_mm=x, y_mm=y + 28, width_mm=w, height_mm=8),
        ))

    return nodes


register_component(
    name="stat_card",
    description="统计卡片: 大数字 + 标签 + 趋势",
    generator=_generate,
    param_schema={
        "value": {"type": "str", "required": True},
        "label": {"type": "str", "default": ""},
        "trend": {"type": "str", "default": ""},
        "trend_value": {"type": "str", "default": ""},
        "position": {"type": "dict", "default": {}},
    },
)
