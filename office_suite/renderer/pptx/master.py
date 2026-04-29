"""PPTX 母版管理

设计方案要求：
  - 查询可用母版布局
  - 创建自定义母版
  - 管理占位符

当前状态：骨架实现，仅提供查询接口。
"""

from pptx import Presentation
from typing import Any


def list_master_layouts(prs: Presentation) -> list[dict[str, Any]]:
    """列出所有可用的母版布局

    Returns:
        包含 layout_index, name, placeholder_count 的字典列表
    """
    layouts = []
    for i, layout in enumerate(prs.slide_layouts):
        placeholders = []
        for ph in layout.placeholders:
            placeholders.append({
                "idx": ph.placeholder_format.idx,
                "type": str(ph.placeholder_format.type),
                "name": ph.name,
            })
        layouts.append({
            "index": i,
            "name": layout.name,
            "placeholder_count": len(placeholders),
            "placeholders": placeholders,
        })
    return layouts


def get_layout_by_name(prs: Presentation, name: str):
    """按名称查找布局，返回 (index, layout) 或 None"""
    for i, layout in enumerate(prs.slide_layouts):
        if layout.name.lower() == name.lower():
            return i, layout
    return None


def create_slide_with_layout(prs: Presentation, layout_index: int):
    """使用指定布局创建幻灯片"""
    layout = prs.slide_layouts[min(layout_index, len(prs.slide_layouts) - 1)]
    return prs.slides.add_slide(layout)
