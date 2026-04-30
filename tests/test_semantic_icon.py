import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.dsl.parser import parse_yaml_string
from office_suite.dsl.validator import validate_dsl
from office_suite.ir.compiler import compile_document
from office_suite.ir.validator import validate_ir_v2
from office_suite.ir.types import NodeType
from office_suite.renderer.pptx.deck import PPTXRenderer
from office_suite.tools.check import check_dsl_file


def test_semantic_icon_compiles_to_native_shape_group():
    raw = """
version: "4.0"
type: presentation
title: Native Icon
slides:
  - layout: blank
    elements:
      - type: semantic_icon
        color: "#FACC15"
        position: { x: 20mm, y: 20mm, width: 16mm, height: 16mm }
        primitives:
          - { type: line, x1: 50, y1: 16, x2: 26, y2: 54 }
          - { type: line, x1: 26, y1: 54, x2: 46, y2: 54 }
          - { type: line, x1: 46, y1: 54, x2: 38, y2: 84 }
          - { type: line, x1: 38, y1: 84, x2: 72, y2: 40 }
          - { type: line, x1: 72, y1: 40, x2: 52, y2: 40 }
          - { type: line, x1: 52, y1: 40, x2: 50, y2: 16 }
"""
    result = validate_dsl(__import__("yaml").safe_load(raw))
    assert not result.errors

    doc = parse_yaml_string(raw)
    ir_doc = compile_document(doc)
    icon = ir_doc.children[0].children[0]

    assert icon.node_type == NodeType.GROUP
    assert icon.extra["semantic_icon"] == "custom"
    assert icon.children
    assert all(child.node_type == NodeType.SHAPE for child in icon.children)
    assert not any(child.node_type == NodeType.IMAGE for child in icon.children)


def test_semantic_icon_requires_ai_authored_primitives():
    raw = """
version: "4.0"
type: presentation
title: Native Icon
slides:
  - layout: blank
    elements:
      - type: semantic_icon
        icon: efficiency
        color: "#FACC15"
        position: { x: 20mm, y: 20mm, width: 16mm, height: 16mm }
"""
    result = validate_dsl(__import__("yaml").safe_load(raw))
    assert result.errors
    assert result.errors[0].rule == "semantic_icon_primitives_required"


def test_empty_semantic_icon_is_invalid_after_compile():
    raw = """
version: "4.0"
type: presentation
title: Native Icon
slides:
  - layout: blank
    elements:
      - type: semantic_icon
        icon: missing
        color: "#FACC15"
        position: { x: 20mm, y: 20mm, width: 16mm, height: 16mm }
"""
    ir_doc = compile_document(parse_yaml_string(raw))
    result = validate_ir_v2(ir_doc)

    assert result.errors
    assert result.errors[0].rule == "semantic_icon_empty"


def test_check_validates_semantic_icons_in_page_files():
    project_dir = PROJECT_ROOT / "tests" / "output" / "page_ref_icon_validation"
    pages_dir = project_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "deck.yml").write_text(
        """
version: "4.0"
type: presentation
title: Page Ref Icon
pages:
  - pages/001.yml
""",
        encoding="utf-8",
    )
    (pages_dir / "001.yml").write_text(
        """
layout: blank
elements:
  - type: semantic_icon
    icon: missing
    color: "#FACC15"
    position: { x: 20mm, y: 20mm, width: 16mm, height: 16mm }
""",
        encoding="utf-8",
    )

    result = check_dsl_file(project_dir / "deck.yml", run_lint=False)

    assert result.dsl_errors
    assert result.dsl_errors[0].rule == "semantic_icon_primitives_required"


def test_semantic_icon_rejects_non_basic_primitives():
    raw = """
version: "4.0"
type: presentation
title: Native Icon
slides:
  - layout: blank
    elements:
      - type: semantic_icon
        color: "#FACC15"
        position: { x: 20mm, y: 20mm, width: 16mm, height: 16mm }
        primitives:
          - { type: spark, x: 20, y: 20, width: 60, height: 60 }
"""
    result = validate_dsl(__import__("yaml").safe_load(raw))
    assert result.errors
    assert result.errors[0].rule == "semantic_icon_primitive_unknown"


def test_semantic_icon_renders_to_pptx():
    raw = """
version: "4.0"
type: presentation
title: Native Icon Render
slides:
  - layout: blank
    background: { color: "#020617" }
    elements:
      - type: semantic_icon
        color: "#FACC15"
        position: { x: 20mm, y: 20mm, width: 20mm, height: 20mm }
        primitives:
          - { type: ellipse, x: 16, y: 16, width: 68, height: 68 }
          - { type: rounded_rectangle, x: 38, y: 38, width: 24, height: 24, fill_opacity: 0.16 }
"""
    ir_doc = compile_document(parse_yaml_string(raw))
    output = PROJECT_ROOT / "tests" / "output" / "semantic_icon_native.pptx"
    rendered = PPTXRenderer().render(ir_doc, output)

    assert rendered.exists()
    assert rendered.stat().st_size > 0
