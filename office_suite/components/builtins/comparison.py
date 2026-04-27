"""对比组件 — 左右两栏对比

参数:
  left_title: str — 左栏标题
  left_items: list[str] — 左栏要点
  right_title: str — 右栏标题
  right_items: list[str] — 右栏要点
  position: dict — 位置 (可选)
"""

from ...ir.types import IRNode, NodeType, IRPosition, IRStyle
from ..registry import register_component


def _generate(params: dict) -> list[IRNode]:
    left_title = params.get("left_title", "Before")
    left_items = params.get("left_items", [])
    right_title = params.get("right_title", "After")
    right_items = params.get("right_items", [])
    pos = params.get("position", {})
    x = pos.get("x", 10)
    y = pos.get("y", 10)
    w = pos.get("width", 220)
    h = pos.get("height", 120)

    col_w = (w - 10) / 2  # 两栏宽度, 中间留 10mm 间距
    nodes = []

    # 左栏标题
    nodes.append(IRNode(
        node_type=NodeType.TEXT,
        content=left_title,
        style=IRStyle(font_size=18, font_weight=700, font_color="#0F172A"),
        position=IRPosition(x_mm=x, y_mm=y, width_mm=col_w, height_mm=10),
    ))

    # 左栏要点
    left_text = "\n".join(f"• {item}" for item in left_items)
    nodes.append(IRNode(
        node_type=NodeType.TEXT,
        content=left_text,
        style=IRStyle(font_size=13, font_color="#475569"),
        position=IRPosition(x_mm=x, y_mm=y + 12, width_mm=col_w, height_mm=h - 14),
    ))

    # 右栏标题
    nodes.append(IRNode(
        node_type=NodeType.TEXT,
        content=right_title,
        style=IRStyle(font_size=18, font_weight=700, font_color="#2563EB"),
        position=IRPosition(x_mm=x + col_w + 10, y_mm=y, width_mm=col_w, height_mm=10),
    ))

    # 右栏要点
    right_text = "\n".join(f"• {item}" for item in right_items)
    nodes.append(IRNode(
        node_type=NodeType.TEXT,
        content=right_text,
        style=IRStyle(font_size=13, font_color="#475569"),
        position=IRPosition(x_mm=x + col_w + 10, y_mm=y + 12, width_mm=col_w, height_mm=h - 14),
    ))

    return nodes


register_component(
    name="comparison",
    description="对比: 左右两栏对比布局",
    generator=_generate,
    param_schema={
        "left_title": {"type": "str", "default": "Before"},
        "left_items": {"type": "list", "required": True},
        "right_title": {"type": "str", "default": "After"},
        "right_items": {"type": "list", "required": True},
        "position": {"type": "dict", "default": {}},
    },
)
