"""Special 语义布局生成"""
from __future__ import annotations

from typing import Any

from ._constants import _SPECIAL_LAYOUTS, _GAP_NAMES
from ._grid import _calc_grid
from ._split import _calc_split


def _init_special_layouts() -> None:
    """初始化所有预定义语义布局"""
    if _SPECIAL_LAYOUTS:
        return

    layouts: dict[str, dict[str, Any]] = {}

    # ── Stats Row ──
    for count in (2, 3, 4, 5, 6):
        layouts[f"stats_{count}"] = _calc_grid(count, 1, 4.0, "d")

    # ── Feature Grid ──
    for cols in (2, 3, 4):
        for rows in (1, 2):
            layouts[f"feature_{cols}x{rows}"] = _calc_grid(cols, rows, 8.0, "d")

    # ── Timeline ──
    for steps in (3, 4, 5, 6, 7, 8):
        layouts[f"timeline_{steps}"] = _calc_grid(steps, 1, 2.0, "d")
        layouts[f"timeline_{steps}x2"] = _calc_grid(steps, 2, 2.0, "d")

    # ── Card Grid ──
    for cols in (2, 3, 4, 5):
        for rows in (1, 2, 3):
            layouts[f"card_{cols}x{rows}"] = _calc_grid(cols, rows, 4.0, "d")

    # ── Step List ──
    for steps in (3, 4, 5, 6, 7, 8):
        layouts[f"steps_{steps}"] = _calc_grid(1, steps, 2.0, "d")

    # ── Hero Layouts ──
    layouts["hero_left"] = _calc_split("d", "6040", 8.0)
    layouts["hero_right"] = _calc_split("d", "4060", 8.0)
    layouts["hero_top"] = _calc_split("v", "6040", 4.0)
    layouts["hero_bottom"] = _calc_split("v", "4060", 4.0)

    # ── Cover Layouts ──
    layouts["cover_center"] = {"mode": "absolute"}
    layouts["cover_split"] = _calc_split("d", "5050", 0.0)
    layouts["cover_full"] = {"mode": "absolute"}

    # ── Quote Layouts ──
    layouts["quote_center"] = {"mode": "absolute"}
    layouts["quote_left"] = _calc_split("d", "4060", 8.0)

    # ── Comparison ──
    layouts["compare_2"] = _calc_split("d", "5050", 8.0)
    layouts["compare_3"] = _calc_grid(3, 1, 4.0, "d")
    layouts["compare_4"] = _calc_grid(4, 1, 4.0, "d")

    # ── Team / Profile ──
    for count in (2, 3, 4, 5, 6):
        layouts[f"team_{count}"] = _calc_grid(count, 1, 8.0, "d")
    layouts["team_2x2"] = _calc_grid(2, 2, 8.0, "d")
    layouts["team_3x2"] = _calc_grid(3, 2, 8.0, "d")

    # ── Gallery ──
    for cols in (2, 3, 4):
        for rows in (1, 2, 3):
            layouts[f"gallery_{cols}x{rows}"] = _calc_grid(cols, rows, 2.0, "s")

    # ── KPI / Metrics ──
    for count in (2, 3, 4, 5):
        layouts[f"kpi_{count}"] = _calc_grid(count, 1, 4.0, "d")
    for count in (4, 6, 8):
        layouts[f"kpi_{count // 2}x2"] = _calc_grid(count // 2, 2, 4.0, "d")

    # ── Agenda ──
    for items in (3, 4, 5, 6, 7, 8):
        layouts[f"agenda_{items}"] = _calc_grid(1, items, 2.0, "d")

    # ── Dashboard ──
    layouts["dashboard_2x2"] = _calc_grid(2, 2, 4.0, "d")
    layouts["dashboard_3x2"] = _calc_grid(3, 2, 4.0, "d")
    layouts["dashboard_4x2"] = _calc_grid(4, 2, 4.0, "d")
    layouts["dashboard_mixed"] = _calc_grid(12, 2, 2.0, "d")

    # ── Content + Sidebar ──
    layouts["sidebar_left"] = _calc_split("d", "3070", 8.0)
    layouts["sidebar_right"] = _calc_split("d", "7030", 8.0)
    layouts["sidebar_narrow"] = _calc_split("d", "4060", 4.0)

    # ── Full-width Sections ──
    layouts["full"] = _calc_grid(1, 1, 4.0, "d")
    layouts["full_padded"] = _calc_grid(1, 1, 4.0, "s")

    # ── Stacked Cards ──
    for count in (2, 3, 4, 5, 6, 7, 8):
        layouts[f"stack_{count}"] = _calc_grid(1, count, 4.0, "d")

    # ── Process / Pipeline ──
    for steps in (3, 4, 5, 6, 7, 8):
        layouts[f"process_{steps}"] = _calc_grid(steps, 1, 4.0, "d")
        layouts[f"process_{steps}x2"] = _calc_grid(steps, 2, 4.0, "d")

    # ── Pricing ──
    for count in (2, 3, 4, 5):
        layouts[f"pricing_{count}"] = _calc_grid(count, 1, 4.0, "d")

    # ── Roadmap ──
    for phases in (3, 4, 5, 6, 7, 8):
        layouts[f"roadmap_{phases}"] = _calc_grid(phases, 1, 2.0, "d")
        layouts[f"roadmap_{phases}x2"] = _calc_grid(phases, 2, 2.0, "d")

    # ── Bento Grid ──
    for cols in (2, 3, 4):
        for rows in (2, 3):
            for gap in (2.0, 4.0, 8.0):
                g = _GAP_NAMES.get(gap, str(int(gap)))
                layouts[f"bento_{cols}x{rows}g{g}"] = _calc_grid(cols, rows, gap, "d")

    # ── Magazine / Editorial ──
    for cols in (2, 3, 4):
        layouts[f"magazine_{cols}col"] = _calc_grid(cols, 2, 4.0, "d")
        layouts[f"magazine_{cols}col_s"] = _calc_grid(cols, 2, 4.0, "s")

    # ── Masonry-like ──
    for cols in (2, 3, 4, 5, 6):
        for rows in (2, 3):
            layouts[f"masonry_{cols}x{rows}"] = _calc_grid(cols, rows, 2.0, "d")

    # ── Resume / CV ──
    layouts["resume_2col"] = _calc_split("d", "3565", 8.0)
    layouts["resume_3col"] = _calc_grid(3, 1, 4.0, "d")

    # ── Onboarding / Intro ──
    for steps in (3, 4, 5):
        layouts[f"onboarding_{steps}"] = _calc_grid(steps, 1, 8.0, "d")

    # ── Quiz / Q&A ──
    for count in (2, 3, 4):
        layouts[f"quiz_{count}"] = _calc_grid(count, 1, 4.0, "d")
        layouts[f"quiz_{count}x2"] = _calc_grid(count, 2, 4.0, "d")

    # ── Portfolio ──
    for cols in (2, 3, 4):
        for rows in (1, 2, 3):
            layouts[f"portfolio_{cols}x{rows}"] = _calc_grid(cols, rows, 4.0, "d")

    # ── Notification / Alert ──
    for count in (2, 3, 4, 5):
        layouts[f"notification_{count}"] = _calc_grid(1, count, 2.0, "d")

    # ── Chart + Text split ──
    layouts["chart_left"] = _calc_split("d", "6040", 8.0)
    layouts["chart_right"] = _calc_split("d", "4060", 8.0)
    layouts["chart_top"] = _calc_split("v", "6040", 4.0)
    layouts["chart_bottom"] = _calc_split("v", "4060", 4.0)

    # ── Table layouts ──
    for cols in (1, 2):
        layouts[f"table_{cols}col"] = _calc_grid(cols, 1, 4.0, "d")

    # ── Split with more gap variants ──
    for direction in ("d", "v"):
        for ratio_key in ("5050", "4060", "6040", "3070", "7030"):
            for gap in (0.0, 2.0, 16.0, 20.0):
                g_name = str(int(gap)) if gap == int(gap) else str(gap)
                name = f"f{direction}r{ratio_key}g{g_name}"
                if name not in layouts:
                    layouts[name] = _calc_split(direction, ratio_key, gap)

    # ── Icon Grid ──
    for count in (4, 6, 8, 9, 12):
        cols = min(count, 6)
        rows = max(1, (count + cols - 1) // cols)
        layouts[f"icons_{count}"] = _calc_grid(cols, rows, 8.0, "d")

    # ── Tag / Badge Grid ──
    for cols in (3, 4, 5, 6):
        for rows in (1, 2, 3):
            layouts[f"tags_{cols}x{rows}"] = _calc_grid(cols, rows, 2.0, "s")

    # ── Checkpoint / Milestone ──
    for count in (3, 4, 5, 6):
        layouts[f"milestone_{count}"] = _calc_grid(count, 1, 4.0, "d")
        layouts[f"milestone_{count}x2"] = _calc_grid(count, 2, 4.0, "d")

    # ── Slide Variants ──
    for mk in ("t", "d", "s"):
        layouts[f"full_{mk}"] = _calc_grid(1, 1, 4.0, mk)
        for cols in (2, 3):
            layouts[f"full_{cols}col_{mk}"] = _calc_grid(cols, 1, 4.0, mk)

    # ── Form / Input layouts ──
    for rows in (2, 3, 4, 5, 6):
        layouts[f"form_{rows}row"] = _calc_grid(1, rows, 4.0, "d")

    # ── Comparison table ──
    for cols in (2, 3, 4, 5):
        for rows in (2, 3, 4):
            layouts[f"compare_{cols}x{rows}"] = _calc_grid(cols, rows, 2.0, "d")

    # ── Kanban / Board ──
    for cols in (3, 4, 5, 6):
        layouts[f"kanban_{cols}"] = _calc_grid(cols, 1, 4.0, "d")

    # ── Carousel indicators ──
    for count in (3, 4, 5, 6):
        layouts[f"carousel_{count}"] = _calc_grid(count, 1, 2.0, "d")

    # ── Map + Info split ──
    layouts["map_left"] = _calc_split("d", "6040", 4.0)
    layouts["map_right"] = _calc_split("d", "4060", 4.0)
    layouts["map_top"] = _calc_split("v", "6040", 2.0)

    _SPECIAL_LAYOUTS.update(layouts)
