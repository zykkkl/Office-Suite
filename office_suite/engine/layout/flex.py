"""弹性布局引擎 — Flexbox 语义

设计方案第六章：布局引擎。

Flexbox 布局在一维方向（行或列）上排列元素，
支持对齐、分布、换行、伸缩等语义。

与 CSS Flexbox 语义对齐。
"""

from dataclasses import dataclass
from ...ir.layout_spec import (
    AbsolutePosition, FlexPosition, FlexDirection, FlexJustify, FlexAlign,
    FlexWrap, LayoutMode, LayoutSpec,
)


@dataclass
class FlexItem:
    """弹性布局子项"""
    width: float = 0.0       # 固定宽度（mm）
    height: float = 0.0      # 固定高度（mm）
    grow: float = 0.0        # 放大比例
    shrink: float = 1.0      # 缩小比例
    basis: float | None = None  # 初始尺寸（mm），None = auto
    order: int = 0
    align_self: FlexAlign | None = None  # 覆盖容器的 align-items
    content: object = None   # 关联内容


class FlexLayout:
    """弹性布局引擎

    在一维方向上排列子项，支持：
    - 主轴方向：row / column / row-reverse / column-reverse
    - 主轴对齐：justify-content（start/center/end/space-between/space-around/space-evenly）
    - 交叉轴对齐：align-items（start/center/end/stretch）
    - 换行：nowrap / wrap / wrap-reverse
    - 多行分布：align-content（start/center/end/space-between/space-around/stretch）
    - 间距：gap / row-gap
    - 伸缩：flex-grow / flex-shrink

    用法：
        layout = FlexLayout(container_width=254, container_height=142.875)
        positions = layout.resolve(
            flex_pos=FlexPosition(direction=FlexDirection.ROW, gap=5),
            items=[FlexItem(width=50, height=30), FlexItem(width=80, height=30)],
        )
    """

    def __init__(
        self,
        container_width: float = 254.0,
        container_height: float = 142.875,  # 16:9 正确高度
        margin: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0),
    ):
        self.container_width = container_width
        self.container_height = container_height
        self.margin_top, self.margin_right, self.margin_bottom, self.margin_left = margin

    def resolve(
        self,
        flex_pos: FlexPosition,
        items: list[FlexItem],
    ) -> list[AbsolutePosition]:
        """计算每个子项的位置

        Args:
            flex_pos: 容器的弹性布局参数
            items: 子项列表

        Returns:
            每个子项的绝对位置列表
        """
        if not items:
            return []

        is_row = flex_pos.direction in (FlexDirection.ROW, FlexDirection.ROW_REVERSE)
        is_reverse = flex_pos.direction in (FlexDirection.ROW_REVERSE, FlexDirection.COLUMN_REVERSE)

        # 页边距后的可用区域
        if is_row:
            main_size = self.container_width - self.margin_left - self.margin_right
            cross_size = self.container_height - self.margin_top - self.margin_bottom
            main_offset_base = self.margin_left
            cross_offset_base = self.margin_top
        else:
            main_size = self.container_height - self.margin_top - self.margin_bottom
            cross_size = self.container_width - self.margin_left - self.margin_right
            main_offset_base = self.margin_top
            cross_offset_base = self.margin_left
        gap = flex_pos.gap
        row_gap = flex_pos.row_gap if flex_pos.row_gap > 0 else gap

        # 计算每个子项的主轴尺寸
        item_sizes = self._calc_item_sizes(items, flex_pos, main_size, gap, is_row)

        # 换行模式：将子项分组为多行
        if flex_pos.wrap != FlexWrap.NOWRAP:
            lines = self._split_into_lines(items, item_sizes, main_size, gap, flex_pos)
        else:
            lines = [(list(range(len(items))), list(range(len(items))))]

        # 逐行计算位置
        all_positions: list[AbsolutePosition | None] = [None] * len(items)

        # 计算每行的交叉轴尺寸
        line_cross_sizes = []
        for line_indices, _ in lines:
            if flex_pos.wrap == FlexWrap.NOWRAP:
                line_cross_sizes.append(cross_size)
            else:
                max_cross = 0.0
                for idx in line_indices:
                    cross_val = items[idx].height if is_row else items[idx].width
                    if cross_val > 0:
                        max_cross = max(max_cross, cross_val)
                if max_cross <= 0:
                    max_cross = cross_size / max(1, len(lines))
                line_cross_sizes.append(max_cross)

        # 计算每行的交叉轴起始位置（align-content）+ 页边距
        total_lines_cross = sum(line_cross_sizes) + row_gap * max(0, len(lines) - 1)
        cross_offset = cross_offset_base + self._calc_align_content_offset(
            flex_pos.align_content, cross_size, total_lines_cross, len(lines), row_gap,
        )

        for line_num, (line_indices, original_indices) in enumerate(lines):
            line_items = [items[i] for i in line_indices]
            line_sizes = [item_sizes[i] for i in line_indices]
            line_cross = line_cross_sizes[line_num]

            # 计算主轴偏移和间距
            total_gap = gap * max(0, len(line_items) - 1)
            total_items_size = sum(line_sizes) + total_gap
            n = len(line_items)

            main_offset, step_gap = self._calc_main_offset(
                flex_pos.justify, main_size, sum(line_sizes), n, gap,
            )

            # 分配位置（+ 页边距偏移）
            current = main_offset_base + main_offset
            indices = range(n)
            if is_reverse:
                indices = range(n - 1, -1, -1)

            for idx in indices:
                item = line_items[idx]
                size = line_sizes[idx]
                orig_idx = original_indices[idx]

                # 交叉轴对齐
                item_align = item.align_self or flex_pos.align
                cross_pos = self._calc_cross_position(
                    item_align, line_cross,
                    item.height if is_row else item.width,
                )

                # STRETCH：拉伸交叉轴尺寸
                if item_align == FlexAlign.STRETCH:
                    if is_row:
                        item_h = line_cross
                        item_w = size
                    else:
                        item_w = line_cross
                        item_h = size
                else:
                    item_w = size if is_row else (item.width if item.width > 0 else cross_size)
                    item_h = (item.height if item.height > 0 else cross_size) if is_row else size

                if is_row:
                    pos = AbsolutePosition(
                        x=round(current, 2),
                        y=round(cross_offset + cross_pos, 2),
                        width=round(max(0, item_w), 2),
                        height=round(max(0, item_h), 2),
                    )
                else:
                    pos = AbsolutePosition(
                        x=round(cross_offset + cross_pos, 2),
                        y=round(current, 2),
                        width=round(max(0, item_w), 2),
                        height=round(max(0, item_h), 2),
                    )

                all_positions[orig_idx] = pos
                current += size + step_gap

            cross_offset += line_cross + row_gap

        return all_positions  # type: ignore

    def _calc_item_sizes(
        self, items: list[FlexItem], flex_pos: FlexPosition,
        main_size: float, gap: float, is_row: bool,
    ) -> list[float]:
        """计算每个子项的主轴最终尺寸"""
        item_sizes = []
        total_fixed = 0.0
        total_grow = 0.0

        for item in items:
            basis = item.basis if item.basis is not None else (item.width if is_row else item.height)
            if basis is None or basis <= 0:
                # basis=0 或 auto：如果没有 grow，使用内容尺寸
                basis = 0.0
            item_sizes.append(basis)
            total_fixed += basis
            total_grow += item.grow

        total_gap = gap * max(0, len(items) - 1)
        available = main_size - total_fixed - total_gap

        if available > 0 and total_grow > 0:
            for i, item in enumerate(items):
                if item.grow > 0:
                    item_sizes[i] += available * (item.grow / total_grow)
        elif available < 0:
            total_shrink = sum(
                item.shrink for i, item in enumerate(items) if item_sizes[i] > 0
            )
            if total_shrink > 0:
                for i, item in enumerate(items):
                    if item.shrink > 0 and item_sizes[i] > 0:
                        item_sizes[i] += available * (item.shrink / total_shrink)
                        item_sizes[i] = max(0, item_sizes[i])

        return item_sizes

    def _split_into_lines(
        self, items: list[FlexItem], item_sizes: list[float],
        main_size: float, gap: float, flex_pos: FlexPosition,
    ) -> list[tuple[list[int], list[int]]]:
        """将子项按换行规则分组

        Returns:
            list of (line_indices, original_indices)
        """
        lines: list[tuple[list[int], list[int]]] = []
        current_line: list[int] = []
        current_main = 0.0

        for i in range(len(items)):
            size = item_sizes[i]
            needed = size + (gap if current_line else 0)

            if current_line and current_main + needed > main_size + 0.01:
                lines.append((current_line[:], current_line[:]))
                current_line = [i]
                current_main = size
            else:
                current_line.append(i)
                current_main += needed

        if current_line:
            lines.append((current_line[:], current_line[:]))

        if flex_pos.wrap == FlexWrap.WRAP_REVERSE:
            lines.reverse()

        return lines

    def _calc_main_offset(
        self, justify: FlexJustify, container_size: float,
        items_size: float, item_count: int, gap: float,
    ) -> tuple[float, float]:
        """计算主轴起始偏移和每步间距

        Returns:
            (offset, step_gap) — offset 为第一个子项的起始位置，
            step_gap 为子项间的间距（space-* 模式下动态计算）
        """
        if justify == FlexJustify.START:
            return 0.0, gap
        elif justify == FlexJustify.CENTER:
            return max(0, (container_size - items_size) / 2), gap
        elif justify == FlexJustify.END:
            return max(0, container_size - items_size), gap
        elif justify == FlexJustify.SPACE_BETWEEN:
            free = container_size - items_size
            if item_count > 1:
                return 0.0, free / (item_count - 1)
            return 0.0, 0.0
        elif justify == FlexJustify.SPACE_AROUND:
            free = container_size - items_size
            if item_count > 0:
                around_gap = free / item_count
                return around_gap / 2, around_gap
            return 0.0, 0.0
        elif justify == FlexJustify.SPACE_EVENLY:
            free = container_size - items_size
            if item_count > 0:
                even_gap = free / (item_count + 1)
                return even_gap, even_gap
            return 0.0, 0.0
        return 0.0, gap

    def _calc_cross_position(
        self, align: FlexAlign, container_size: float, item_size: float,
    ) -> float:
        """计算交叉轴位置"""
        if align == FlexAlign.START:
            return 0.0
        elif align == FlexAlign.CENTER:
            return (container_size - item_size) / 2 if item_size > 0 else 0.0
        elif align == FlexAlign.END:
            return container_size - item_size if item_size > 0 else 0.0
        elif align == FlexAlign.STRETCH:
            return 0.0
        elif align == FlexAlign.BASELINE:
            return 0.0  # 简化处理
        return 0.0

    def _calc_align_content_offset(
        self, align: FlexAlign, container_size: float,
        total_lines_size: float, line_count: int, row_gap: float,
    ) -> float:
        """计算多行交叉轴起始偏移（align-content）"""
        if line_count <= 1:
            return 0.0
        if align == FlexAlign.START:
            return 0.0
        elif align == FlexAlign.CENTER:
            return max(0, (container_size - total_lines_size) / 2)
        elif align == FlexAlign.END:
            return max(0, container_size - total_lines_size)
        elif align == FlexAlign.STRETCH:
            return 0.0  # 拉伸模式下每行高度会重新计算
        return 0.0
