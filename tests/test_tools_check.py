from pathlib import Path

from office_suite.tools.check import check_dsl_file


def test_check_dsl_file_multifile_presentation():
    deck_path = Path(__file__).parent / "fixtures" / "multifile_presentation" / "deck.yml"
    output_dir = Path(__file__).parent / "output" / "check_tool"

    result = check_dsl_file(deck_path, render_formats=["pptx"], output_dir=output_dir)

    assert result.is_valid
    assert result.slide_count == 2
    assert result.outputs["pptx"].exists()
