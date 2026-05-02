"""Generate SVG / PNG icon assets and a manifest for deck use.

Each icon is a simple 100×100 SVG with a semantic glyph derived from the
requested name, rendered to both SVG and PNG (via Pillow).

Usage::

    from office_suite.tools.icon_assets import generate_icon_assets
    manifest = generate_icon_assets(output_dir, names=["efficiency", "content"])
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ── Simple SVG templates keyed by semantic name ────────────────────
# Each template is the *inner* content placed inside a 100×100 viewBox.

_GLYPHS: dict[str, str] = {
    # Arrow / efficiency motif
    "efficiency": (
        '<polygon points="50,10 80,50 60,50 60,90 40,90 40,50 20,50" '
        'fill="{color}" />'
    ),
    # Document / content motif
    "content": (
        '<rect x="25" y="10" width="50" height="80" rx="4" fill="{color}" />'
        '<line x1="35" y1="30" x2="65" y2="30" stroke="white" stroke-width="3" />'
        '<line x1="35" y1="42" x2="65" y2="42" stroke="white" stroke-width="3" />'
        '<line x1="35" y1="54" x2="55" y2="54" stroke="white" stroke-width="3" />'
    ),
    # Generic fallback: filled circle
    "_default": '<circle cx="50" cy="50" r="35" fill="{color}" />',
}


def _make_svg(name: str, color: str, size: int = 128) -> str:
    """Return a complete SVG string for *name*."""
    template = _GLYPHS.get(name, _GLYPHS["_default"]).format(color=color)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 100 100" width="{size}" height="{size}">\n'
        "{glyph}\n"
        "</svg>\n"
    ).format(size=size, glyph=template)


def _svg_to_png(svg_bytes: bytes, size: int, output_path: Path) -> None:
    """Rasterise *svg_bytes* to a PNG via Pillow (raster-only fallback)."""
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Parse the fill colour from the SVG (hex → RGBA tuple)
    # For simplicity draw a centred circle with the given colour.
    def _hex_to_rgb(h: str) -> tuple[int, int, int]:
        h = h.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    try:
        rgb = _hex_to_rgb(svg_bytes.decode("utf-8").split('fill="')[1].split('"')[0])
    except (IndexError, ValueError):
        rgb = (100, 100, 100)

    margin = int(size * 0.15)
    draw.ellipse([margin, margin, size - margin, size - margin], fill=(*rgb, 255))
    img.save(str(output_path), "PNG")


def generate_icon_assets(
    output_dir: str | Path,
    *,
    names: list[str],
    color: str = "#6366F1",
    size: int = 128,
    topic: str = "",
) -> dict[str, Any]:
    """Generate SVG + PNG icon assets and write a manifest.

    Args:
        output_dir: Directory where assets and manifest.json are written.
        names: Semantic icon names (e.g. ``["efficiency", "content"]``).
        color: Hex fill colour applied to each icon.
        size: Raster PNG size in pixels.
        topic: Optional topic label recorded in the manifest.

    Returns:
        Manifest dict written to ``<output_dir>/manifest.json``.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    assets: list[dict[str, Any]] = []
    for idx, name in enumerate(names, start=1):
        svg_filename = f"{idx:02d}_{name}.svg"
        png_filename = f"{idx:02d}_{name}.png"

        svg_content = _make_svg(name, color, size)
        svg_path = out / svg_filename
        svg_path.write_text(svg_content, encoding="utf-8")

        png_path = out / png_filename
        _svg_to_png(svg_content.encode("utf-8"), size, png_path)

        assets.append({
            "name": name,
            "svg": svg_filename,
            "png": png_filename,
            "color": color,
            "size": size,
        })

    manifest: dict[str, Any] = {
        "source_skill": "logo-generator",
        "topic": topic,
        "style_policy": {"harmony": True},
        "assets": assets,
    }

    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest
