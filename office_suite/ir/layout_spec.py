"""IR 布局规格 — 定义元素在容器中的位置和尺寸

布局模式：
  - absolute: 绝对坐标（mm）
  - relative: 相对坐标（百分比）
  - grid: 栅格布局（12/24 列）
  - flex: 弹性布局（Flexbox 语义）

P0 仅支持 absolute + relative。grid/flex 为 P1。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LayoutMode(Enum):
    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    GRID = "grid"
    FLEX = "flex"
    CONSTRAINT = "constraint"


@dataclass(frozen=True)
class AbsolutePosition:
    """绝对坐标定位（mm）"""
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0


@dataclass(frozen=True)
class RelativePosition:
    """相对坐标定位（百分比，0-100）"""
    x_pct: float = 0.0
    y_pct: float = 0.0
    width_pct: float = 100.0
    height_pct: float = 100.0


class GridAlign(Enum):
    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"


@dataclass(frozen=True)
class GridPosition:
    """栅格布局定位"""
    column: int = 1            # 起始列（1-based）
    column_span: int = 1       # 跨列数
    row: int = 1               # 起始行（1-based）
    row_span: int = 1          # 跨行数
    columns: int = 12          # 总列数
    align: GridAlign = GridAlign.STRETCH


class FlexDirection(Enum):
    ROW = "row"
    COLUMN = "column"
    ROW_REVERSE = "row-reverse"
    COLUMN_REVERSE = "column-reverse"


class FlexJustify(Enum):
    START = "start"
    CENTER = "center"
    END = "end"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"
    SPACE_EVENLY = "space-evenly"


class FlexAlign(Enum):
    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"
    BASELINE = "baseline"


class FlexWrap(Enum):
    """弹性换行模式"""
    NOWRAP = "nowrap"
    WRAP = "wrap"
    WRAP_REVERSE = "wrap-reverse"


@dataclass(frozen=True)
class FlexPosition:
    """弹性布局定位"""
    direction: FlexDirection = FlexDirection.ROW
    justify: FlexJustify = FlexJustify.START
    align: FlexAlign = FlexAlign.START
    wrap: FlexWrap = FlexWrap.NOWRAP
    align_content: FlexAlign = FlexAlign.START  # 多行交叉轴分布
    gap: float = 0.0           # 主轴间距（mm）
    row_gap: float = 0.0       # 交叉轴间距（mm），wrap 模式使用
    order: int = 0             # 排序
    grow: float = 0.0          # 放大比例
    shrink: float = 1.0        # 缩小比例
    basis: str = "auto"        # 初始尺寸


@dataclass
class LayoutSpec:
    """统一布局规格"""
    mode: LayoutMode = LayoutMode.ABSOLUTE
    absolute: AbsolutePosition | None = None
    relative: RelativePosition | None = None
    grid: GridPosition | None = None
    flex: FlexPosition | None = None

    def resolve_mm(
        self,
        container_width: float,
        container_height: float,
        row_height: float | None = None,
        flex_items: list | None = None,
        flex_index: int = 0,
    ) -> AbsolutePosition:
        """将任意布局模式解析为绝对坐标（mm）

        Args:
            container_width: 容器宽度（mm）
            container_height: 容器高度（mm）
            row_height: 栅格行高（mm），仅 GRID 模式使用。默认为列宽。
            flex_items: FlexItem 列表，仅 FLEX 模式使用。提供时按多 item 解析。
            flex_index: 当前 item 在 flex_items 中的索引。

        Returns:
            AbsolutePosition（mm）
        """
        if self.mode == LayoutMode.ABSOLUTE and self.absolute:
            return self.absolute

        if self.mode == LayoutMode.RELATIVE and self.relative:
            return AbsolutePosition(
                x=self.relative.x_pct / 100 * container_width,
                y=self.relative.y_pct / 100 * container_height,
                width=self.relative.width_pct / 100 * container_width,
                height=self.relative.height_pct / 100 * container_height,
            )

        if self.mode == LayoutMode.GRID and self.grid:
            col_width = container_width / self.grid.columns
            rh = row_height if row_height is not None else col_width
            return AbsolutePosition(
                x=(self.grid.column - 1) * col_width,
                y=(self.grid.row - 1) * rh,
                width=self.grid.column_span * col_width,
                height=self.grid.row_span * rh,
            )

        if self.mode == LayoutMode.FLEX and self.flex:
            from ..engine.layout.flex import FlexLayout, FlexItem as FItem
            engine = FlexLayout(container_width, container_height)
            if flex_items:
                # 多 item 模式：用传入的兄弟列表
                items = flex_items
            else:
                # 单 item fallback
                items = [FItem(width=container_width, height=container_height)]
                flex_index = 0
            positions = engine.resolve(self.flex, items)
            if flex_index < len(positions) and positions[flex_index] is not None:
                ap = positions[flex_index]
                return AbsolutePosition(
                    x=ap.x,
                    y=ap.y,
                    width=ap.width,
                    height=ap.height,
                )

        return AbsolutePosition()


# ============================================================
# 坐标转换工具
# ============================================================

EMU_PER_MM = 36000
TWIPS_PER_MM = 1440
PT_PER_MM = 2.834645669


def mm_to_emu(mm: float) -> int:
    """mm → EMU (PPTX)"""
    return int(mm * EMU_PER_MM)


def mm_to_twips(mm: float) -> float:
    """mm → Twips (DOCX)"""
    return mm * TWIPS_PER_MM


def mm_to_pt(mm: float) -> float:
    """mm → points (PDF)"""
    return mm * PT_PER_MM


def mm_to_px(mm: float, dpi: float = 96) -> float:
    """mm → pixels (HTML)"""
    return mm * dpi / 25.4
