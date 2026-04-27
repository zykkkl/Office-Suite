"""模板库 — 预定义业务模板

使用方式：
  from office_suite.templates import render_template
  dsl = render_template("work_report", {"title": "Q1 汇报", "author": "张三"})
  doc = parse_yaml_string(dsl)
  ir = compile_document(doc)
  PPTXRenderer().render(ir, "output.pptx")
"""

from .registry import (
    TemplateInfo,
    register_template,
    get_template,
    list_templates,
    list_categories,
    render_template,
)

# 确保内置模板被注册
from . import builtins  # noqa: F401

__all__ = [
    "TemplateInfo",
    "register_template",
    "get_template",
    "list_templates",
    "list_categories",
    "render_template",
]
