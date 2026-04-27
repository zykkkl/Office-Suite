"""Pipeline 节点库 — 导入即注册

所有节点模块在此导入，触发 __init_subclass__ 自动注册到全局注册表。
"""

from .base import NodeExecutor, get_handler, list_registered

# 导入所有节点模块（触发注册）
from .data import fetch, transform
from .compute import skill_invoke, mcp_call, ai_generate
from .design import layout, style
from .render import to_pptx, to_docx, to_xlsx, to_pdf, to_html
from .control import condition, parallel, retry
