"""时间线组件 — 垂直时间线 + 事件节点

参数:
  events: list[dict] — 事件列表 [{date, title, description}]
  position: dict — 位置 (可选)
  orientation: str — 方向 ("vertical" / "horizontal", 默认 vertical)
"""

from ...ir.types import IRNode, NodeType, IRPosition, IRStyle
from ..registry import register_component


def _generate(params: dict) -> list[IRNode]:
    events = params.get("events", [])
    pos = params.get("position", {})
    x = pos.get("x", 20)
    y = pos.get("y", 20)
    w = pos.get("width", 200)
    item_height = 20

    nodes = []
    current_y = y

    for i, event in enumerate(events):
        date = event.get("date", "")
        title = event.get("title", "")
        desc = event.get("description", "")

        # 日期标记
        if date:
            nodes.append(IRNode(
                node_type=NodeType.TEXT,
                content=date,
                style=IRStyle(font_size=11, font_weight=700, font_color="#2563EB"),
                position=IRPosition(x_mm=x, y_mm=current_y, width_mm=30, height_mm=8),
            ))

        # 事件标题
        if title:
            nodes.append(IRNode(
                node_type=NodeType.TEXT,
                content=title,
                style=IRStyle(font_size=14, font_weight=600),
                position=IRPosition(x_mm=x + 35, y_mm=current_y, width_mm=w - 40, height_mm=8),
            ))

        # 事件描述
        if desc:
            nodes.append(IRNode(
                node_type=NodeType.TEXT,
                content=desc,
                style=IRStyle(font_size=11, font_color="#6B7280"),
                position=IRPosition(x_mm=x + 35, y_mm=current_y + 9, width_mm=w - 40, height_mm=8),
            ))

        current_y += item_height

        # 分隔线 (非最后一个)
        if i < len(events) - 1:
            nodes.append(IRNode(
                node_type=NodeType.SHAPE,
                extra={"shape_type": "line"},
                style=IRStyle(border={"color": "#E2E8F0", "width": 1}),
                position=IRPosition(x_mm=x + 35, y_mm=current_y + 2, width_mm=w - 40, height_mm=0),
            ))
            current_y += 4

    return nodes


register_component(
    name="timeline",
    description="时间线: 垂直排列的事件节点",
    generator=_generate,
    param_schema={
        "events": {"type": "list", "required": True},
        "position": {"type": "dict", "default": {}},
        "orientation": {"type": "str", "default": "vertical"},
    },
)
