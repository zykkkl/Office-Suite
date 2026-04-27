"""信息图组件 — 标题 + 指标网格

参数:
  title: str — 信息图标题
  metrics: list[dict] — 指标列表 [{value, label, icon}]
  columns: int — 每行列数 (默认 3)
  position: dict — 位置 (可选)
"""

from ...ir.types import IRNode, NodeType, IRPosition, IRStyle
from ..registry import register_component


def _generate(params: dict) -> list[IRNode]:
    title = params.get("title", "")
    metrics = params.get("metrics", [])
    columns = params.get("columns", 3)
    pos = params.get("position", {})
    x = pos.get("x", 10)
    y = pos.get("y", 10)
    w = pos.get("width", 220)

    nodes = []
    current_y = y

    # 标题
    if title:
        nodes.append(IRNode(
            node_type=NodeType.TEXT,
            content=title,
            style=IRStyle(font_size=24, font_weight=700, font_color="#0F172A"),
            position=IRPosition(x_mm=x, y_mm=current_y, width_mm=w, height_mm=12),
        ))
        current_y += 16

    # 指标网格
    cell_w = (w - (columns - 1) * 6) / columns
    cell_h = 28

    for i, metric in enumerate(metrics):
        row = i // columns
        col = i % columns
        mx = x + col * (cell_w + 6)
        my = current_y + row * (cell_h + 6)

        value = metric.get("value", "")
        label = metric.get("label", "")

        # 指标值
        nodes.append(IRNode(
            node_type=NodeType.TEXT,
            content=value,
            style=IRStyle(font_size=28, font_weight=700, font_color="#2563EB"),
            position=IRPosition(x_mm=mx, y_mm=my, width_mm=cell_w, height_mm=14),
        ))

        # 指标标签
        if label:
            nodes.append(IRNode(
                node_type=NodeType.TEXT,
                content=label,
                style=IRStyle(font_size=11, font_color="#6B7280"),
                position=IRPosition(x_mm=mx, y_mm=my + 15, width_mm=cell_w, height_mm=8),
            ))

    return nodes


register_component(
    name="infographic",
    description="信息图: 标题 + 指标网格",
    generator=_generate,
    param_schema={
        "title": {"type": "str", "default": ""},
        "metrics": {"type": "list", "required": True},
        "columns": {"type": "int", "default": 3},
        "position": {"type": "dict", "default": {}},
    },
)
