"""PPTX 形状渲染 — 从 deck.py 提取的形状级操作

本模块提供形状渲染的独立接口，内部委托给 PPTXRenderer。
deck.py 中的 _render_shape / _apply_shape_fill / _apply_shape_border / _get_shape_type 对应此处。

使用方式：
    from office_suite.renderer.pptx.shape import render_shape, get_shape_type
"""

from pptx.enum.shapes import MSO_SHAPE


# 形状名称 → MSO_SHAPE 映射（合并自 deck.py + shape.py）
SHAPE_TYPE_MAP = {
    "rectangle": MSO_SHAPE.RECTANGLE,
    "rounded_rectangle": MSO_SHAPE.ROUNDED_RECTANGLE,
    "oval": MSO_SHAPE.OVAL,
    "circle": MSO_SHAPE.OVAL,
    "diamond": MSO_SHAPE.DIAMOND,
    "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE,
    "star": MSO_SHAPE.STAR_5_POINT,
    "hexagon": MSO_SHAPE.HEXAGON,
    "pentagon": MSO_SHAPE.PENTAGON,
    "arrow": MSO_SHAPE.RIGHT_ARROW,
    "chevron": MSO_SHAPE.CHEVRON,
    "cross": MSO_SHAPE.CROSS,
    "heart": MSO_SHAPE.HEART,
    "lightning_bolt": MSO_SHAPE.LIGHTNING_BOLT,
}


def get_shape_type(name: str) -> MSO_SHAPE:
    """将形状名称映射为 MSO_SHAPE 枚举"""
    return SHAPE_TYPE_MAP.get(name, MSO_SHAPE.RECTANGLE)


def render_shape(renderer, slide, node, doc):
    """渲染形状元素（委托给 PPTXRenderer._render_shape）"""
    renderer._render_shape(slide, node, doc)


def apply_shape_fill(renderer, shape, style, node):
    """应用形状填充（委托给 PPTXRenderer._apply_shape_fill）"""
    renderer._apply_shape_fill(shape, style, node)


def apply_shape_border(renderer, shape, node):
    """应用形状边框（委托给 PPTXRenderer._apply_shape_border）"""
    renderer._apply_shape_border(shape, node)
