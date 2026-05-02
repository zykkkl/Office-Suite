"""幻灯片模板系统 — 完整的封面/内容/结尾设计方案

提供可直接使用的幻灯片模板，包含布局、背景、装饰、字体层级的完整组合。
不只是背景，而是整页幻灯片的完整设计。

用法：
    from office_suite.design.slide_templates import cover_slide, content_slide, closing_slide
    slide = cover_slide(palette="corporate", title="Q1 财报", subtitle="年度总结")
"""

from .cover import cover_slide
from .content import content_slide
from .closing import closing_slide
from .section import section_slide
from .quote import quote_slide

__all__ = [
    "cover_slide",
    "content_slide",
    "closing_slide",
    "section_slide",
    "quote_slide",
]
