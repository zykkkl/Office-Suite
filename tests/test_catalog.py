"""元素分类目录测试"""

import pytest
from pathlib import Path

from office_suite.catalog import ElementLayer, ElementDef, ElementCatalog, get_catalog


CATALOG_YAML = Path(__file__).parent.parent / "office_suite" / "catalog" / "catalog.yaml"


class TestElementLayer:
    def test_enum_values(self):
        assert ElementLayer.ATOM.value == "ATOM"
        assert ElementLayer.TEMPLATE.value == "TEMPLATE"

    def test_layer_order(self):
        d = ElementDef(id="x", layer=ElementLayer.ATOM, category="c", name="n")
        assert d.layer_order == 4
        d2 = ElementDef(id="y", layer=ElementLayer.TEMPLATE, category="c", name="n")
        assert d2.layer_order == 0


class TestElementDef:
    def test_defaults(self):
        d = ElementDef(id="test", layer=ElementLayer.ATOM, category="shape", name="Test")
        assert d.tags == []
        assert d.scenes == []
        assert d.component_name is None
        assert d.dsl_fragment is None


class TestElementCatalog:
    def test_load_yaml(self):
        catalog = ElementCatalog()
        count = catalog.load_yaml(CATALOG_YAML)
        assert count > 10, f"Expected >10 elements, got {count}"

    def test_get(self):
        catalog = ElementCatalog()
        catalog.load_yaml(CATALOG_YAML)
        entry = catalog.get("stat_card")
        assert entry is not None
        assert entry.layer == ElementLayer.COMPONENT
        assert "card" in entry.tags

    def test_get_missing(self):
        catalog = ElementCatalog()
        assert catalog.get("nonexistent") is None

    def test_search_by_tags(self):
        catalog = ElementCatalog()
        catalog.load_yaml(CATALOG_YAML)
        results = catalog.search(tags=["cover"])
        assert len(results) > 0
        for r in results:
            assert "cover" in r.tags

    def test_search_by_layer(self):
        catalog = ElementCatalog()
        catalog.load_yaml(CATALOG_YAML)
        results = catalog.search(layer=ElementLayer.ATOM)
        assert len(results) > 0
        for r in results:
            assert r.layer == ElementLayer.ATOM

    def test_search_by_category(self):
        catalog = ElementCatalog()
        catalog.load_yaml(CATALOG_YAML)
        results = catalog.search(category="data_display")
        assert len(results) > 0
        for r in results:
            assert r.category == "data_display"

    def test_search_by_scenes(self):
        catalog = ElementCatalog()
        catalog.load_yaml(CATALOG_YAML)
        results = catalog.search(scenes=["timeline"])
        assert len(results) > 0

    def test_search_intersection(self):
        catalog = ElementCatalog()
        catalog.load_yaml(CATALOG_YAML)
        results = catalog.search(layer=ElementLayer.ATOM, tags=["text"])
        for r in results:
            assert r.layer == ElementLayer.ATOM
            assert "text" in r.tags

    def test_search_limit(self):
        catalog = ElementCatalog()
        catalog.load_yaml(CATALOG_YAML)
        results = catalog.search(limit=3)
        assert len(results) <= 3

    def test_generate_dsl_fragment(self):
        catalog = ElementCatalog()
        catalog.load_yaml(CATALOG_YAML)
        fragments = catalog.generate_dsl("stat_card", {"value": "1.2M", "label": "DAU"})
        assert len(fragments) > 0
        texts = [f for f in fragments if f.get("type") == "text"]
        values = [t["content"] for t in texts]
        assert "1.2M" in values
        assert "DAU" in values

    def test_generate_dsl_component_ref(self):
        catalog = ElementCatalog()
        catalog.load_yaml(CATALOG_YAML)
        fragments = catalog.generate_dsl("icon_badge", {"icon": "star"})
        assert len(fragments) == 1
        assert fragments[0]["type"] == "component"
        assert fragments[0]["component"] == "semantic_icon"

    def test_generate_dsl_missing(self):
        catalog = ElementCatalog()
        with pytest.raises(KeyError):
            catalog.generate_dsl("nonexistent")

    def test_register_custom(self):
        catalog = ElementCatalog()
        entry = ElementDef(
            id="custom_thing",
            layer=ElementLayer.COMPONENT,
            category="custom",
            name="Custom Thing",
            tags=["custom"],
            dsl_fragment=[{"type": "text", "content": "hello"}],
        )
        catalog.register(entry)
        assert catalog.get("custom_thing") is not None
        fragments = catalog.generate_dsl("custom_thing")
        assert fragments[0]["content"] == "hello"

    def test_list_all(self):
        catalog = ElementCatalog()
        catalog.load_yaml(CATALOG_YAML)
        all_entries = catalog.list_all()
        assert len(all_entries) > 10
        # 验证按 layer_order 排序
        orders = [e.layer_order for e in all_entries]
        assert orders == sorted(orders)


class TestGlobalCatalog:
    def test_get_catalog(self):
        catalog = get_catalog()
        assert isinstance(catalog, ElementCatalog)
        # 应该自动加载了默认 catalog
        entry = catalog.get("heading_text")
        assert entry is not None

    def test_catalog_yaml_exists(self):
        assert CATALOG_YAML.exists()


class TestParseCatalogRef:
    """测试 parser 中的 catalog_ref 展开"""

    def test_expand_catalog_ref_in_slide(self):
        from office_suite.dsl.parser import parse_yaml_string

        yaml_str = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: catalog_ref
        catalog_id: heading_text
        params:
          content: "Test Title"
        position: { x: 10mm, y: 10mm, width: 200mm, height: 20mm }
"""
        doc = parse_yaml_string(yaml_str)
        slide = doc.slides[0]
        # catalog_ref 应被展开为 text 元素
        texts = [e for e in slide.elements if e.type == "text"]
        assert len(texts) >= 1
        assert texts[0].content == "Test Title"

    def test_non_catalog_ref_preserved(self):
        from office_suite.dsl.parser import parse_yaml_string

        yaml_str = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: text
        content: "Normal text"
"""
        doc = parse_yaml_string(yaml_str)
        assert doc.slides[0].elements[0].content == "Normal text"
