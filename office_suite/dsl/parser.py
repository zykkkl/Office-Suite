"""DSL Parser — YAML/JSON → Document 对象解析器

数据流：YAML 文件/字符串 → load_yaml() → 原始 dict → parse_document() → Document 对象

注意：parse_element() 中 style 字段保持原始 dict 不做解析，
由 ir/compiler.py::compile_element() 负责将 dict → StyleSpec → IRStyle。
这样设计的原因：编译器需要在样式级联的上下文中处理样式，
而不是在解析阶段就丢失级联信息。

架构位置：YAML 文件 → [本文件] → Document → ir/compiler.py → IRDocument
"""

from pathlib import Path
from typing import Any

import yaml

from .schema import (
    DataBinding,
    Document,
    DocType,
    Element,
    FillSpec,
    FontSpec,
    GradientSpec,
    PositionSpec,
    ShadowSpec,
    Slide,
    StyleSpec,
)


def parse_position(raw: dict[str, Any] | None) -> PositionSpec | None:
    """解析位置规格"""
    if not raw:
        return None
    return PositionSpec(
        x=raw.get("x"),
        y=raw.get("y"),
        width=raw.get("width"),
        height=raw.get("height"),
        bottom=raw.get("bottom"),
        center=raw.get("center", False),
    )


def parse_font(raw: dict[str, Any] | None) -> FontSpec | None:
    """解析字体规格"""
    if not raw:
        return None
    return FontSpec(
        family=raw.get("family", "Microsoft YaHei UI"),
        size=raw.get("size", 18),
        weight=raw.get("weight", 400),
        italic=raw.get("italic", False),
        color=raw.get("color", "#000000"),
    )


def parse_gradient(raw: dict[str, Any] | None) -> GradientSpec | None:
    """解析渐变规格"""
    if not raw:
        return None
    return GradientSpec(
        type=raw.get("type", "linear"),
        angle=raw.get("angle", 0),
        stops=raw.get("stops", ["#000000", "#FFFFFF"]),
    )


def parse_fill(raw: dict[str, Any] | None) -> FillSpec | None:
    """解析填充规格"""
    if not raw:
        return None
    return FillSpec(
        color=raw.get("color"),
        gradient=parse_gradient(raw.get("gradient")),
        opacity=raw.get("opacity", 1.0),
    )


def parse_shadow(raw: dict[str, Any] | None) -> ShadowSpec | None:
    """解析阴影规格"""
    if not raw:
        return None
    return ShadowSpec(
        blur=raw.get("blur", 0),
        offset=raw.get("offset", [0, 0]),
        color=raw.get("color", "#00000040"),
    )


def parse_style(raw: dict[str, Any] | None) -> StyleSpec | None:
    """解析样式规格"""
    if not raw:
        return None
    return StyleSpec(
        font=parse_font(raw.get("font")),
        fill=parse_fill(raw.get("fill")),
        shadow=parse_shadow(raw.get("shadow")),
        border=raw.get("border"),
        text_effect=raw.get("text_effect"),
    )


def parse_element(raw: dict[str, Any]) -> Element:
    """解析单个元素"""
    position_raw = raw.get("position")
    # 支持简写：position 可以直接是字符串 "background"
    if isinstance(position_raw, str) and position_raw == "background":
        position_raw = None  # 特殊标记

    return Element(
        type=raw.get("type", "text"),
        content=raw.get("content"),
        source=raw.get("source"),
        style=raw.get("style"),  # 可以是字符串引用或内联样式
        position=parse_position(position_raw) if isinstance(position_raw, dict) else None,
        data_ref=raw.get("data_ref"),
        chart_type=raw.get("chart_type"),
        query=raw.get("query"),
        prompt=raw.get("prompt"),
        size=raw.get("size"),
        opacity=raw.get("opacity", 1.0),
        filter=raw.get("filter"),
        animation=raw.get("animation"),
        children=[parse_element(c) for c in raw.get("children", [])],
        extra={k: v for k, v in raw.items()
               if k not in {"type", "content", "source", "style", "position",
                            "data_ref", "chart_type", "query", "prompt",
                            "size", "opacity", "filter", "animation", "children"}},
    )


def parse_slide(raw: dict[str, Any]) -> Slide:
    """解析单张幻灯片"""
    return Slide(
        layout=raw.get("layout", "blank"),
        background=raw.get("background"),
        elements=[parse_element(e) for e in raw.get("elements", [])],
        transition=raw.get("transition"),
    )


def parse_data_binding(raw: dict[str, Any]) -> DataBinding:
    """解析数据绑定"""
    return DataBinding(
        source=raw.get("source"),
        columns=raw.get("columns", []),
        formula=raw.get("formula"),
        inline=raw.get("inline"),
    )


def parse_document(raw: dict[str, Any]) -> Document:
    """解析完整文档"""
    doc_type_str = raw.get("type", "presentation")
    try:
        doc_type = DocType(doc_type_str)
    except ValueError:
        doc_type = DocType.PRESENTATION

    data_bindings = {}
    for key, val in raw.get("data", {}).items():
        if isinstance(val, dict):
            data_bindings[key] = parse_data_binding(val)

    styles = {}
    for key, val in raw.get("styles", {}).items():
        if isinstance(val, dict):
            styles[key] = parse_style(val)

    slides = [parse_slide(s) for s in raw.get("slides", [])]

    return Document(
        version=raw.get("version", "4.0"),
        type=doc_type,
        theme=raw.get("theme", "default"),
        title=raw.get("title", ""),
        data=data_bindings,
        styles=styles,
        slides=slides,
        sections=raw.get("sections", []),
        raw=raw,
    )


def load_yaml(path: str | Path) -> dict[str, Any]:
    """加载 YAML 文件"""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_yaml(path: str | Path) -> Document:
    """从 YAML 文件解析为 Document"""
    raw = load_yaml(path)
    return parse_document(raw)


def parse_yaml_string(yaml_str: str) -> Document:
    """从 YAML 字符串解析为 Document"""
    raw = yaml.safe_load(yaml_str)
    return parse_document(raw)
