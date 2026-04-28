# PPT Layout System

This guideline defines the layout system for Office Suite PPT/PPTX generation. It is normative: follow it when authoring or revising presentation YAML.

## 1. Purpose

The PPT layout system separates three concerns:

- Page structure: the major regions of a slide, such as title, body, footer, chart area, and card grid.
- Element geometry: the outer rectangle of each visual object, expressed with `position`.
- Internal layout: how text sits inside its rectangle, expressed with alignment, vertical anchoring, and margins.

Do not use coordinates to solve an internal layout problem. Coordinates place the container; text layout fields place content inside the container.

## 2. Canvas Model

Office Suite PPT uses a 16:9 canvas:

```text
width: 254mm
height: 142.875mm
origin: top-left
x: left to right
y: top to bottom
```

Required constraints:

- `x + width <= 254mm`
- `y + height <= 142.875mm`
- Keep recurring page numbers, footers, and navigation in stable positions.
- Use a page grid before placing content. Recommended default margins are `20mm` left/right and `13mm` top.

## 3. Page Regions

Use these common regions unless the design document specifies otherwise:

```text
Header/title band: y 12-32mm
Intro/subtitle band: y 32-48mm
Body region: y 52-118mm
Footer/page marker: y 124-132mm
```

Rules:

- The title band should not compete with the body.
- The body region should be visually centered when content is sparse.
- The footer must not overlap with charts, tables, cards, or closing actions.
- If a slide feels top-heavy or bottom-heavy, move the whole content group, not individual labels.

## 4. Text Layout Fields

The PPTX renderer supports these DSL fields on `text` elements and shape elements with `content`:

| Field | Values | Meaning |
|---|---|---|
| `align` | `left`, `center`, `right` | Horizontal paragraph alignment |
| `text_align` | same as `align` | Alias |
| `vertical_align` | `top`, `middle`, `center`, `bottom` | Text frame vertical anchoring |
| `verticalAlign` | same as `vertical_align` | Alias |
| `valign` | same as `vertical_align` | Alias |
| `margin` | number in mm | Same margin on all sides |
| `margins` | `{left, right, top, bottom}` | Per-side margins in mm |
| `margin_left` etc. | number in mm | Individual margins |

Use explicit internal layout fields for:

- Numbers inside circles.
- Pills, chips, and badges.
- Card titles that should be centered.
- Short labels inside shapes.
- Button-like or tab-like text.

Canonical centered badge:

```yaml
- type: text
  content: "1"
  position: { x: 30mm, y: 70mm, width: 16mm, height: 16mm }
  align: center
  vertical_align: middle
  margin: 0
  style:
    font: { family: "Arial", size: 15, weight: 700, color: "#FFFFFF" }
```

Anti-pattern:

```yaml
# Bad: the text box is too narrow and relies on guessed offsets.
- type: text
  content: "1"
  position: { x: 36mm, y: 73mm, width: 5mm, height: 8mm }
```

PowerPoint text boxes have default internal margins. Narrow text boxes often make centered-looking coordinates render off-center.

## 5. Repeated Elements

Repeated elements must be generated as a system:

- Same object type, width, height, and internal alignment.
- Consistent gaps.
- Consistent title and description positions.
- Same page-level baseline.
- Shared styling, with only deliberate variation.

For repeated card groups, define the card grid first:

```text
available width = right_edge - left_edge
card width = fixed
gap = fixed
x_i = left + i * (card_width + gap)
```

Five short items usually work better as five equal columns than as a `3 + 2` layout. A `3 + 2` layout is acceptable only when the second row has a deliberate anchor or different hierarchy.

## 6. Card System

Cards are containers, not decoration. Use them when they group related content.

Rules:

- Keep card radius restrained.
- Do not use cards inside cards.
- If card text is centered, set `align: center`, `vertical_align: middle`, and appropriate margins.
- If card body text is a sentence, left-align it unless the card is a compact tile.
- Alternating fills may be used to support scanning, but should not create visual noise.

Compact five-card row pattern:

```yaml
- type: shape
  shape_type: rounded_rectangle
  position: { x: 20mm, y: 62mm, width: 38mm, height: 52mm }
  style: { fill: { color: "#F5EBDC" } }
- type: text
  content: "01"
  position: { x: 20mm, y: 68mm, width: 38mm, height: 7mm }
  align: center
  vertical_align: middle
  margin: 0
```

## 7. Text Box Sizing

Estimate text height before writing YAML:

```text
single-line height ~= font_size * 1.3
multi-line height ~= font_size * 1.3 * line_count
```

Guidelines:

- Body text in PPT should normally be at least 13pt in this renderer.
- Do not shrink text below readability to avoid overflow.
- If a text box overflows, first condense the content or redesign the layout.
- If a text box looks underfilled, reduce its height, increase font size, or rebalance the surrounding layout.
- Chinese text often needs more vertical space than a naive point-size estimate suggests.

## 8. Visual Balance

Visual balance is not the same as geometric balance.

Check:

- Does the slide have one dominant message?
- Is the body group vertically balanced inside the body region?
- Are repeated items visually equal?
- Does the footer have enough separation from the body?
- Are special slides such as cover, chapter, and closing visually distinct but not disconnected?

Common corrections:

- Final slide feels low: move the whole title/subtitle/action group up.
- Numbers are not centered in circles: make the text box equal to the circle bounds and set internal centering.
- Two-row cards feel sparse: switch to one row, or add a strong visual anchor for the second row.
- Chart dominates the conclusion: make the conclusion text more prominent and treat the chart as evidence.

## 9. Revision Protocol

When revising a PPT after visual feedback:

1. Classify the issue: structure, geometry, internal text layout, spacing, typography, or content density.
2. Fix the system, not only the instance. If one card is wrong, inspect the whole card pattern.
3. Prefer DSL intent fields over micro-coordinate changes.
4. Re-render the PPTX.
5. Read back PPTX properties when possible: slide count, shape count, paragraph alignment, vertical anchors, and text margins.
6. Run the unified check command:

```bash
python -m office_suite.tools.check output/<deck-name>/deck.yml --render pptx --output-dir output/<deck-name>/check
```

## 10. Quality Gate Interpretation

`office_suite.tools.check` combines DSL validation, IR validation, design lint, and optional rendering.

Treat these as blocking:

- YAML parse errors.
- Missing referenced page files.
- IR validation errors.
- Failed PPTX render.
- Out-of-bounds content.
- Confirmed text overlap or truncation.

Treat these as review items:

- Font hierarchy warnings.
- Small spacing warnings.
- Color count warnings.
- Intentional decorative overlap.

Warnings are not automatically wrong, but they must be consciously accepted or fixed.
