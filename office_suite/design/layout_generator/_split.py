"""Split 布局生成"""
from __future__ import annotations

from typing import Any

from ._constants import _SLIDE_W, _SLIDE_H, _MARGIN_PRESETS, _GAP_NAMES, _RATIO_PRESETS


def _calc_split(
    direction: str,
    ratio_key: str,
    gap: float,
) -> dict[str, Any]:
    """计算 split 布局的完整配置"""
    ratio = _RATIO_PRESETS[ratio_key]
    cols = len(ratio)

    top, bottom, left, right = _MARGIN_PRESETS["d"]
    usable_w = _SLIDE_W - left - right
    usable_h = _SLIDE_H - top - bottom

    if direction == "d":  # row (水平分栏)
        total_gap = gap * (cols - 1)
        widths = [(usable_w - total_gap) * r for r in ratio]
        return {
            "mode": "flex",
            "flex": {
                "direction": "row",
                "justify": "start",
                "align": "stretch",
                "gap": gap,
                "margin": (top, right, bottom, left),
            },
            "_ratios": {str(i): round(w, 2) for i, w in enumerate(widths)},
        }
    else:  # column (垂直分栏)
        total_gap = gap * (cols - 1)
        heights = [(usable_h - total_gap) * r for r in ratio]
        return {
            "mode": "flex",
            "flex": {
                "direction": "column",
                "justify": "start",
                "align": "stretch",
                "gap": gap,
                "margin": (top, right, bottom, left),
            },
            "_ratios": {str(i): round(h, 2) for i, h in enumerate(heights)},
        }


def _split_name(direction: str, ratio_key: str, gap: float) -> str:
    """生成 split 布局名称：f{direction}r{ratio}g{gap}"""
    g = _GAP_NAMES.get(gap, str(int(gap)))
    return f"f{direction}r{ratio_key}g{g}"


def _generate_split_layouts() -> dict[str, dict[str, Any]]:
    """生成所有 split 布局"""
    layouts: dict[str, dict[str, Any]] = {}
    for direction in ("d", "v"):
        for ratio_key in _RATIO_PRESETS:
            for gap in _GAP_NAMES:
                name = _split_name(direction, ratio_key, gap)
                layouts[name] = _calc_split(direction, ratio_key, gap)
    return layouts
