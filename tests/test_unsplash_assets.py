import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.tools.unsplash_assets import prepare_unsplash_assets


def test_unsplash_assets_writes_brief_without_api_key():
    output_dir = PROJECT_ROOT / "tests" / "output" / "unsplash_assets_brief"
    manifest = prepare_unsplash_assets(
        output_dir,
        queries=["abstract AI workspace", "automation laptop"],
        topic="AIGC bonus",
        access_key="",
    )

    assert manifest["status"] == "brief_only"
    assert (output_dir / "asset_brief.md").exists()
    manifest_path = output_dir / "manifest.json"
    assert manifest_path.exists()
    saved = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert saved["queries"] == ["abstract AI workspace", "automation laptop"]
