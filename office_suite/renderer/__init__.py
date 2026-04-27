"""格式渲染器 — PPTX / DOCX / XLSX / PDF / HTML"""

from .base import RendererCapability, BaseRenderer
from .capability_map import get_capabilities, supports, get_fallback

__all__ = [
    "RendererCapability", "BaseRenderer",
    "get_capabilities", "supports", "get_fallback",
]
