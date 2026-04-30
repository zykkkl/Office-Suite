# Style Contract Template

This document defines the reusable visual style rules for an Office Suite presentation. Use this template when creating `design.md` for any generation task.

## Mandatory Design Constraints

1. **6 colors maximum** -- Exactly 5-6 colors in the palette. No exceptions
2. **4 font sizes per slide** -- H1, H2, Body, Caption. Never exceed
3. **Body text minimum 12pt** -- Anything smaller is unreadable in projection
4. **Card radius 3mm** -- All cards use identical corner radius
5. **Page marker position fixed** -- `x: 196mm, y: 128mm, width: 38mm`, align:right

## Color Palette Definition

Define exactly 5-6 colors using the Office Suite design token system:

```text
bg_primary:    #0A0E1A   (page background)
bg_surface:    #12182B   (card/panel background)
border:        #1E2642   (dividers, card borders)
accent:        #C9A84C   (titles, highlights, primary emphasis)
text_primary:  #E8E4DC   (body text)
text_muted:    #6B7280   (labels, captions, page numbers)
```

All emphasis must use opacity/brightness variations of these colors. Do not add new hues.

### Color Assignment Rules

| Token | Usage |
|-------|-------|
| `bg_primary` | Page background color |
| `bg_surface` | Card/panel container fills |
| `border` | Dividers, card borders, separator lines |
| `accent` | Page titles (H1), highlights, key data, primary emphasis |
| `text_primary` | Body text, card titles (H2) |
| `text_muted` | Captions, labels, page markers, secondary information |

## Typography Scale (Strict 4-Level)

| Level | Size | Weight | Use |
|-------|------|--------|-----|
| H1 | 32-36pt | 700 | Page titles, chapter headers |
| H2 | 14-16pt | 700 | Card titles, section headers |
| Body | 12-13pt | 400 | Descriptions, paragraphs, bullet text |
| Caption | 9-10pt | 400 | Labels, tags, page markers, metadata |

**Font selection**: Read `format/fonts.md` for the available font list.

When the user's query is in Chinese or requires Chinese PPT delivery, specify both Chinese and English fonts.

Default font family: Microsoft YaHei UI (Chinese + English), Arial (numbers/English in Chinese presentations).

## Card System

Cards are the primary content grouping mechanism:

- **Shape**: `rounded_rectangle`
- **Fill**: `bg_surface` color
- **Border**: `border` color, 1pt width
- **Corner radius**: 3mm (via `adjustments: [16667]`)
- **Internal layout**: Title (H2) -> Divider -> Body (Body) -> Caption (Caption)
- **No nesting**: Do not use cards inside cards

### Card Internal Layout

```yaml
# Card container
- type: shape
  shape_type: rounded_rectangle
  position: { x: 20mm, y: 42mm, width: 68mm, height: 72mm }
  style:
    fill: { color: "#12182B" }
    border: { color: "#1E2642", width: 1 }

# Card title (inside card)
- type: text
  content: "Section Title"
  position: { x: 24mm, y: 46mm, width: 60mm, height: 10mm }
  align: center
  vertical_align: middle
  margin: 0
  style:
    font: { family: "Microsoft YaHei UI", size: 16, weight: 700, color: "#E8E4DC" }
```

## Spacing Rhythm

```text
Page margins:     20mm L/R, 16mm top, 12mm bottom
Title band:       y 16-32mm (title + divider)
Body region:      y 40-116mm
Footer:           y 124-132mm
Card gap:         4mm
Group gap:        8mm
Card padding:     4mm internal
```

## Repeated Elements System

Repeated cards must follow a system:
- Same object type, width, height, internal alignment
- Consistent gaps (4mm between cards)
- Complete sequences (if outline says 6 modules, render exactly 6)
- Grid alignment: cards use standardized widths (32mm, 50mm, 68mm)

## Background Treatment

- **Default**: Solid `bg_primary` color
- **Background layers** (optional): Image, gradient, or color layers via `background.layers`
- **Decorative elements**: Divider lines (rectangle, 0.5mm height, `accent` color)

## Text Effects (Optional)

Available text effects via `style.text_effect`:
- `shadow`: `{ blur, offset, color }`
- `stroke`: `{ color, width, dash }`
- `reflection`: `{ opacity, distance, blur, direction }`
- `bevel`: `{ type, width, height }`
- `letter_spacing`: pt value
- `word_spacing`: pt value

Use sparingly. Titles may use shadow for depth; body text should have no effects.

## Chart and Table Styles

### Charts
- Use `chart` element with `chart_type`: bar, line, pie, area, scatter
- Data referenced via `data_ref` pointing to global data in `deck.yml`
- Chart colors derived from palette (accent for primary series, text_muted for secondary)

### Tables
- Use `table` element with `data_ref`
- Header: `bg_primary` or `accent` background, white text, bold
- Body: alternating `bg_primary`/`bg_surface` or white/light gray
- Borders: 1pt `border` color, horizontal only

## Risk Checklist Template

Copy this checklist into every `design.md`:

```markdown
## Risk Checklist
- [ ] No more than 6 colors total
- [ ] No more than 4 font sizes per slide
- [ ] Body text minimum 12pt
- [ ] All cards use identical radius (3mm)
- [ ] Page markers: x: 196mm, y: 128mm, width: 38mm, align:right
- [ ] No card nesting (cards inside cards)
- [ ] Repeated elements follow consistent grid alignment
- [ ] Content within canvas bounds (x + width <= 254mm, y + height <= 142.875mm)
```

## deck.yml Style Definition Template

```yaml
version: "4.0"
type: presentation
title: "Presentation Title"
theme: default
styles:
  h1:
    font: { family: "Microsoft YaHei UI", size: 36, weight: 700, color: "#C9A84C" }
  h2:
    font: { family: "Microsoft YaHei UI", size: 16, weight: 700, color: "#E8E4DC" }
  body:
    font: { family: "Microsoft YaHei UI", size: 13, weight: 400, color: "#E8E4DC" }
  caption:
    font: { family: "Microsoft YaHei UI", size: 10, weight: 400, color: "#6B7280" }
pages:
  - pages/001_cover.yml
  - pages/002_content.yml
```
