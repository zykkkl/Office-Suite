"""模板注册表 — 业务模板管理

设计方案：模板是预定义的 DSL 文档，用户通过填充数据快速生成文档。

模板分类：
  - business: 商务汇报、项目方案、年度报告
  - academic: 学术论文、实验报告、课程展示
  - creative: 产品发布、创意提案、社交媒体

数据流：
  模板 (YAML DSL) + 参数 → 填充变量 → parse_yaml_string → IR → Renderer
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TemplateInfo:
    """模板元数据"""
    name: str
    display_name: str
    category: str         # business / academic / creative
    doc_type: str         # presentation / document / spreadsheet
    description: str
    # 变量定义 (名称 → 默认值)
    variables: dict[str, str] = field(default_factory=dict)
    # 标签
    tags: list[str] = field(default_factory=list)
    # 模板内容 (YAML DSL 字符串)
    content: str = ""


# ============================================================
# 注册表
# ============================================================

_TEMPLATE_REGISTRY: dict[str, TemplateInfo] = {}


def register_template(info: TemplateInfo):
    """注册模板"""
    _TEMPLATE_REGISTRY[info.name] = info


def get_template(name: str) -> TemplateInfo | None:
    """获取模板"""
    return _TEMPLATE_REGISTRY.get(name)


def list_templates(category: str = "") -> list[TemplateInfo]:
    """列出模板"""
    templates = list(_TEMPLATE_REGISTRY.values())
    if category:
        templates = [t for t in templates if t.category == category]
    return templates


def list_categories() -> list[str]:
    """列出所有分类"""
    return list(set(t.category for t in _TEMPLATE_REGISTRY.values()))


def render_template(name: str, variables: dict[str, str] | None = None) -> str:
    """渲染模板 — 将变量替换为实际值

    Args:
        name: 模板名
        variables: 变量值映射

    Returns:
        填充后的 YAML DSL 字符串
    """
    tmpl = _TEMPLATE_REGISTRY.get(name)
    if tmpl is None:
        raise ValueError(f"模板 '{name}' 不存在。可用模板: {list(_TEMPLATE_REGISTRY.keys())}")

    content = tmpl.content
    merged = {**tmpl.variables}
    if variables:
        merged.update(variables)

    # 替换 {{var}} 占位符
    for key, value in merged.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))

    return content
