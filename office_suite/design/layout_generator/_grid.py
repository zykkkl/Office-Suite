"""Grid 布局生成"""
from __future__ import annotations

from typing import Any

from ._constants import _SLIDE_W, _SLIDE_H, _MARGIN_PRESETS, _GAP_PRESETS, _GAP_NAMES


def _calc_grid(
    columns: int,
    rows: int,
    gap: float,
    margin_key: str,
) -> dict[str, Any]:
    """计算 grid 布局的完整配置"""
    top, bottom, left, right = _MARGIN_PRESETS[margin_key]
    usable_w = _SLIDE_W - left - right
    usable_h = _SLIDE_H - top - bottom

    col_width = (usable_w - gap * (columns - 1)) / columns
    row_height = (usable_h - gap * (rows - 1)) / rows

    return {
        "mode": "grid",
        "grid": {
            "columns": columns,
            "gutter": gap,
            "row_height": round(row_height, 2),
            "col_width": round(col_width, 2),
            "margin": (top, right, bottom, left),
        },
    }


def _grid_name(columns: int, rows: int, gap: float, margin_key: str) -> str:
    """生成 grid 布局名称：g{cols}x{rows}g{gap}{margin}"""
    g = _GAP_NAMES.get(gap, str(int(gap)))
    return f"g{columns}x{rows}g{g}{margin_key}"


def _generate_grid_layouts() -> dict[str, dict[str, Any]]:
    """生成所有 grid 布局"""
    layouts: dict[str, dict[str, Any]] = {}
    for cols in range(1, 7):
        for rows in range(1, 5):
            for gap in _GAP_PRESETS:
                for mk in _MARGIN_PRESETS:
                    name = _grid_name(cols, rows, gap, mk)
                    if cols == 1 and rows == 1:
                        continue
                    layouts[name] = _calc_grid(cols, rows, gap, mk)
    return layouts
