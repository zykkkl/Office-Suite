import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

from office_suite.tools.icon_assets import generate_icon_assets


def test_generate_icon_assets_writes_svg_png_and_manifest():
    output_dir = PROJECT_ROOT / "tests" / "output" / "icon_assets_regression"
    manifest = generate_icon_assets(
        output_dir,
        names=["efficiency", "content"],
        color="#FACC15",
        size=128,
        topic="AIGC bonus",
    )

    assert manifest["source_skill"] == "logo-generator"
    assert len(manifest["assets"]) == 2

    manifest_path = output_dir / "manifest.json"
    assert manifest_path.exists()
    saved = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert saved["style_policy"]["harmony"]

    for asset in saved["assets"]:
        svg_path = output_dir / asset["svg"]
        png_path = output_dir / asset["png"]
        assert svg_path.exists()
        assert png_path.exists()
        assert 'viewBox="0 0 100 100"' in svg_path.read_text(encoding="utf-8")
        assert png_path.stat().st_size > 0
