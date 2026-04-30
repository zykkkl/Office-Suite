# Unsplash Photo Asset Search

Use this step before writing page YAML when a deck benefits from real photographic material.

## When To Use

Use Unsplash for:

- Cover backgrounds where a real image improves context.
- Section dividers that need atmosphere without heavy text.
- Product, workplace, technology, learning, travel, environment, or human-context slides.

Do not use Unsplash when:

- The slide is a dense chart, table, process, or checklist.
- A native icon or diagram is clearer.
- The image would be decorative filler.

## Required Workflow

After `outline.md` and `design.md` are finalized, create a concise photo search plan:

```bash
python -m office_suite.tools.unsplash_assets \
  --output-dir output/<deck-name>/assets/photos \
  --topic "<deck topic>" \
  --query "abstract artificial intelligence workspace" \
  --query "person using laptop automation" \
  --orientation landscape
```

If `UNSPLASH_ACCESS_KEY` is set, the tool searches the official Unsplash API, records candidates, triggers download tracking for downloaded photos, and stores local JPG files.

If `UNSPLASH_ACCESS_KEY` is not set, the tool still writes `asset_brief.md`; use it as the search plan before manually selecting images.

## Output

```text
output/<deck-name>/assets/photos/
  asset_brief.md
  manifest.json
  images/
    01_query_photoid.jpg
```

## YAML Usage

Use local files from `manifest.json`:

```yaml
- type: image
  source: "output/<deck-name>/assets/photos/images/01_query_photoid.jpg"
  position: { x: 0mm, y: 0mm, width: 254mm, height: 142.875mm }
  fit: cover
```

## Harmony Rules

- Select images with open areas for text and avoid clutter.
- Match the deck palette: use Unsplash color filters when helpful.
- Add overlays or scrims only from the deck palette.
- Record photo attribution in `manifest.json`; do not delete it.
- Prefer 1-3 strong images across a short deck instead of image clutter on every slide.
