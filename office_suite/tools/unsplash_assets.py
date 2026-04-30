"""Search and prepare Unsplash photo assets for Office Suite decks.

The tool uses the official Unsplash API when an access key is available from
the explicit function argument, tools/unsplash_config.json, or the
`UNSPLASH_ACCESS_KEY` environment variable.
It records attribution metadata and can download local JPG files for PPTX
rendering, triggering Unsplash's download tracking endpoint before each file is
stored locally.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_ROOT = "https://api.unsplash.com"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("unsplash_config.json")


def _slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return text.strip("-") or "photo"


def _request_json(url: str, access_key: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Client-ID {access_key}",
            "Accept-Version": "v1",
            "User-Agent": "office-suite-unsplash-assets",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _read_access_key_from_config(config_path: str | Path | None = None) -> str:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        return ""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    if not isinstance(data, dict):
        return ""

    value = data.get("access_key") or data.get("UNSPLASH_ACCESS_KEY")
    return str(value).strip() if value else ""


def _download_url(url: str, output_path: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "office-suite-unsplash-assets"})
    with urllib.request.urlopen(request, timeout=60) as response:
        output_path.write_bytes(response.read())


def _search_url(query: str, *, page: int, per_page: int, orientation: str, color: str = "") -> str:
    params = {
        "query": query,
        "page": str(page),
        "per_page": str(per_page),
        "orientation": orientation,
        "content_filter": "high",
        "order_by": "relevant",
    }
    if color:
        params["color"] = color
    return f"{API_ROOT}/search/photos?{urllib.parse.urlencode(params)}"


def _photo_record(photo: dict[str, Any], *, query: str, local_file: str | None = None) -> dict[str, Any]:
    user = photo.get("user") or {}
    urls = photo.get("urls") or {}
    links = photo.get("links") or {}
    return {
        "query": query,
        "id": photo.get("id", ""),
        "description": photo.get("description") or photo.get("alt_description") or "",
        "width": photo.get("width"),
        "height": photo.get("height"),
        "color": photo.get("color", ""),
        "local_file": local_file,
        "urls": {
            "regular": urls.get("regular", ""),
            "small": urls.get("small", ""),
            "thumb": urls.get("thumb", ""),
        },
        "links": {
            "html": links.get("html", ""),
            "download_location": links.get("download_location", ""),
        },
        "attribution": {
            "name": user.get("name", ""),
            "username": user.get("username", ""),
            "profile": (user.get("links") or {}).get("html", ""),
            "text": f"Photo by {user.get('name', 'Unsplash photographer')} on Unsplash",
        },
    }


def write_asset_brief(output_dir: str | Path, queries: list[str], *, topic: str = "") -> Path:
    """Write a human/AI-readable search brief even when API access is absent."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Unsplash Asset Brief",
        "",
        f"- Topic: {topic or 'unspecified'}",
        "- Goal: Select real photographic material only where it clarifies the slide message.",
        "- Style: Prefer clean compositions, strong negative space, and colors compatible with design.md.",
        "- Avoid: busy stock-like scenes, unreadable dark overlays, unrelated decoration, faces unless needed.",
        "",
        "## Queries",
    ]
    for query in queries:
        lines.append(f"- {query}")
    brief_path = output_path / "asset_brief.md"
    brief_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return brief_path


def prepare_unsplash_assets(
    output_dir: str | Path,
    *,
    queries: list[str],
    topic: str = "",
    per_query: int = 3,
    orientation: str = "landscape",
    color: str = "",
    download: bool = True,
    access_key: str | None = None,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Search Unsplash and optionally download one local image per query."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    write_asset_brief(output_path, queries, topic=topic)

    access_key = (
        access_key
        or _read_access_key_from_config(config_path)
        or os.environ.get("UNSPLASH_ACCESS_KEY", "")
    )
    manifest: dict[str, Any] = {
        "topic": topic,
        "provider": "unsplash",
        "orientation": orientation,
        "queries": queries,
        "assets": [],
        "status": "brief_only",
    }

    if not access_key:
        manifest["note"] = (
            "No Unsplash access key found in tools/unsplash_config.json or "
            "UNSPLASH_ACCESS_KEY; no API search was performed."
        )
        (output_path / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest

    manifest["status"] = "searched"
    images_dir = output_path / "images"
    if download:
        images_dir.mkdir(parents=True, exist_ok=True)

    for query_index, query in enumerate(queries, start=1):
        data = _request_json(_search_url(query, page=1, per_page=per_query, orientation=orientation, color=color), access_key)
        candidates = data.get("results", []) if isinstance(data, dict) else []
        query_assets = []
        for candidate_index, photo in enumerate(candidates, start=1):
            local_file = None
            if download and candidate_index == 1:
                download_location = ((photo.get("links") or {}).get("download_location") or "")
                if download_location:
                    _request_json(download_location, access_key)
                image_url = (photo.get("urls") or {}).get("regular") or (photo.get("urls") or {}).get("full")
                if image_url:
                    image_path = images_dir / f"{query_index:02d}_{_slug(query)}_{photo.get('id', candidate_index)}.jpg"
                    _download_url(image_url, image_path)
                    local_file = str(image_path).replace("\\", "/")
            query_assets.append(_photo_record(photo, query=query, local_file=local_file))
        manifest["assets"].extend(query_assets)

    (output_path / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search Unsplash and prepare deck photo assets")
    parser.add_argument("--output-dir", required=True, help="Output directory for manifest and images")
    parser.add_argument("--topic", default="", help="Deck topic")
    parser.add_argument("--query", action="append", default=[], help="Unsplash search query; repeatable")
    parser.add_argument("--queries", default="", help="Comma-separated search queries")
    parser.add_argument("--per-query", type=int, default=3, help="Candidates to record per query")
    parser.add_argument("--orientation", default="landscape", choices=["landscape", "portrait", "squarish"])
    parser.add_argument("--color", default="", help="Optional Unsplash color filter")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="JSON config path containing access_key. Defaults to tools/unsplash_config.json",
    )
    parser.add_argument("--no-download", action="store_true", help="Only write search results; do not download local JPG files")
    args = parser.parse_args(argv)

    queries = list(args.query)
    if args.queries:
        queries.extend(item.strip() for item in args.queries.split(",") if item.strip())
    if not queries:
        raise SystemExit("At least one --query or --queries value is required")

    manifest = prepare_unsplash_assets(
        args.output_dir,
        queries=queries,
        topic=args.topic,
        per_query=args.per_query,
        orientation=args.orientation,
        color=args.color,
        download=not args.no_download,
        config_path=args.config,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
