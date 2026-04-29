"""PPTX 渲染器 — IRDocument → .pptx 文件"""

from .deck import PPTXRenderer
from .animation import apply_animations
from . import slide, shape, transition, master

__all__ = [
    "PPTXRenderer",
    "apply_animations",
    "slide",
    "shape",
    "transition",
    "master",
]
