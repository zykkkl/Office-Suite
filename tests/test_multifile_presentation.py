from pathlib import Path

from office_suite.dsl.parser import parse_yaml


def test_parse_presentation_pages():
    deck_path = Path(__file__).parent / "fixtures" / "multifile_presentation" / "deck.yml"
    doc = parse_yaml(deck_path)

    assert doc.title == "Multi-file deck"
    assert len(doc.slides) == 2
    assert doc.slides[0].elements[0].content == "Cover"
    assert doc.slides[1].elements[0].content == "Content"
