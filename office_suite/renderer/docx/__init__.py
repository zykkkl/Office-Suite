"""DOCX 渲染器 — IRDocument → .docx 文件"""

from .document import DOCXRenderer
from . import section, block, style

__all__ = ["DOCXRenderer", "section", "block", "style"]
