from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.ir.types import NodeType


def test_style_ref_is_parsed_and_compiled_to_ir_style():
    doc = parse_yaml_string(
        """
version: "4.0"
type: presentation
title: Style Ref Regression
styles:
  h1:
    font: { family: "Microsoft YaHei UI", size: 34, weight: 700, color: "#FACC15" }
slides:
  - layout: blank
    background: { color: "#020617" }
    elements:
      - type: text
        content: "Visible title"
        style_ref: h1
        position: { x: 20mm, y: 20mm, width: 120mm, height: 16mm }
"""
    )

    element = doc.slides[0].elements[0]
    assert element.style_ref == "h1"
    assert "style_ref" not in element.extra

    ir_doc = compile_document(doc)
    slide = ir_doc.children[0]
    text_node = next(child for child in slide.children if child.node_type == NodeType.TEXT)

    assert text_node.style_ref == "h1"
    assert text_node.style is not None
    assert text_node.style.font_color == "#FACC15"
    assert text_node.style.font_size == 34
    assert text_node.style.font_weight == 700


def test_legacy_style_string_reference_still_compiles():
    doc = parse_yaml_string(
        """
version: "4.0"
type: presentation
title: Legacy Style Ref
styles:
  caption:
    font: { family: "Microsoft YaHei UI", size: 10, weight: 400, color: "#CBD5E1" }
slides:
  - layout: blank
    elements:
      - type: text
        content: "Page marker"
        style: caption
        position: { x: 196mm, y: 126mm, width: 38mm, height: 8mm }
"""
    )

    ir_doc = compile_document(doc)
    slide = ir_doc.children[0]
    text_node = next(child for child in slide.children if child.node_type == NodeType.TEXT)

    assert text_node.style_ref == "caption"
    assert text_node.style is not None
    assert text_node.style.font_color == "#CBD5E1"
    assert text_node.style.font_size == 10
