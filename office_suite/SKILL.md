# Office Suite 4.0 — Presentation & Document Generation

## Scope

Generate professional presentations and documents from YAML DSL. Runtime path:

```text
YAML DSL -> Parser -> IR Document -> Renderer -> .pptx / .docx / .xlsx / .pdf / .html
```

## Core Workflow: Generate-All-First, Check-Once

For every generation task, adopt a **generate-all-first, then check-once** strategy:

1. Complete ALL files (outline, design, deck.yml, every page) before any rendering or validation.
2. Never render, check, or deliver one page at a time.
3. Only after the complete deck is written, run the unified quality gate.
4. Fix issues in batch, then re-render.

## Agent Orchestration

| Role | Scope | Prohibited |
|------|-------|-----------|
| **Main Agent** | Visual design, structure contract, style contract, `deck.yml` construction, quality gate, final delivery | Delegating design decisions to sub-agents before `deck.yml` exists |
| **Sub-Agent** | Generating individual `.page` / `.yml` slide files under `pages/` only | Making visual design choices, changing color/font rules, modifying `deck.yml` or `design.md` |

Before the `deck.yml` and `design.md` are finalized, **strictly prohibited** from assigning page-generation tasks to sub-agents.

## PPT Generation Workflow

### Step 0: Read Guidelines

Before generating any PPT content, read `office_suite/guidelines/ppt_layout_system.md`. Do not proceed without reading it.

### Step 1: Understand Inputs

- Read all user-provided source files.
- Identify language, audience, page count, required data, tone, visual constraints.
- Decide the **content mode**:
  - `outline`: user supplied a page plan, chapter tree, or structured outline.
  - `summary`: user supplied a long document and wants it distilled into slides.
  - `research`: user supplied only a topic or sparse requirements.
- Decide the **visual mode**:
  - `creative`: no visual reference; create from scenario, audience, topic.
  - `reference`: user supplied screenshots, website, images, or style sample.
  - `template`: user explicitly asked to follow a provided template.

Record these decisions in `outline.md` and `design.md`.

### Step 2: Write Structure Contract (`outline.md`)

Persist a page-level outline before writing YAML. Include:

- Deck title and target audience
- Content mode and expansion policy
- Slide count and slide-by-slide story flow
- For each slide: title, key message (one single message per slide), content bullets, suggested layout pattern, visual treatment notes
- Explicit notes for charts, tables, diagrams, images, callouts

**Expansion policy:**
- If the user asks to follow provided content exactly, preserve structure and wording.
- If the user asks for enrichment, add supporting examples and data, marking what was supplemented.
- If the user is silent, stay conservative: clarify structure and only add obvious missing structural pages.

Recommended outline shape:

```markdown
# Presentation Outline

## Context
- Audience:
- Content mode:
- Expansion policy:
- Page count:

## Page 1 [cover] — Layout: cover_split
- Title:
- Key message:
- Content:
- Visual:

## Page 2 [content] — Layout: card_grid_3x2
- Title:
- Key message:
- Content:
- Visual:
```

### Step 3: Write Style Contract (`design.md`)

Persist the visual design system before writing YAML. Must include:

#### 3.1 Canvas
- 16:9, `254mm x 142.875mm`
- Background color, margin system

#### 3.2 Theme Selection (MANDATORY — do this before picking any colors)

**First**, read `office_suite/design/tokens.py` and review all 10 built-in presets. Evaluate which preset best matches the deck's domain, audience, and emotional tone:

| Preset | Background | Accent | Suits |
|--------|-----------|--------|-------|
| `warm` | cream #FFFBEB | amber #D97706 | Education, reading, lifestyle, nonprofit |
| `elegant` | white #FFFFFF | gold #D4AF37 | Formal events, luxury, literature, arts |
| `editorial` | white #FFFFFF | blue #2563EB | Reports, journalism, clean communication |
| `corporate` | white #FFFFFF | blue #1E40AF | Business, finance, enterprise |
| `minimal` | white #FFFFFF | blue #2563EB | Startups, modern tech, design-focused |
| `tech` | dark #0B0F19 | cyan #06B6D4 | Developer tools, AI, deep tech |
| `creative` | dark #18181B | rose #E11D48 | Brand launches, creative portfolios, bold pitches |
| `flat` | light #F0F9FF | sky #0EA5E9 | Healthcare, wellness, accessibility |
| `chinese` | deep red #7F1D1D | gold #D4AF37 | Chinese festivals, traditional culture, celebration |
| `forest` | — | — | (gradient only: green-teal) |

**Second**, set `style_preset` in `deck.yml` to the chosen preset name. The compiler will auto-derive base styles from the preset.

**Third**, if the preset needs tuning (e.g., a lighter card surface, a warmer accent), override individual tokens in `design.md` palette. Never invent a palette from scratch without first consulting the preset list and documenting why no preset fits.

#### 3.3 Color Palette (strict limit)
Define exactly 5-6 colors using the preset as baseline:
```text
style_preset: warm     # ← selected from tokens.py preset list
# Overrides (if any):
bg_primary:    #FFFBEB   (from preset)
bg_surface:    #FEF3C7   (from preset)
border:        #FDE68A   (from preset)
accent:        #D97706   (from preset)
text_primary:  #1C1917   (from preset)
text_muted:    #78716C   (from preset)
```
All emphasis must use opacity/brightness variations of these colors. Do not add new hues. If the preset provides exactly what's needed, use it as-is.

#### 3.3 Typography Scale (strict 4-level)

| Level | Size | Weight | Use |
|-------|------|--------|-----|
| H1 | 32-36pt | 700 | Page titles |
| H2 | 14-16pt | 700 | Card titles, section headers |
| Body | 12-13pt | 400 | Descriptions, bullet text |
| Caption | 9-10pt | 400 | Labels, tags, page markers |

Never use more than 4 distinct font sizes on a single slide.

#### 3.4 Layout Pattern Library

For each slide, pick one pattern from the library:

| Pattern | Use Case | Structure |
|---------|----------|-----------|
| `cover_center` | Cover/closing | Full-bleed bg, centered title block, decorative lines |
| `title_body` | Simple content | Title band + body text block |
| `card_grid_2x2` | 4 items | 2x2 equal cards with title + description |
| `card_grid_3x2` | 6 items | 3x2 equal cards (use for races, features) |
| `card_row_4` | 4 items horizontal | 4 equal cards in one row |
| `split_50_50` | Two sections | Left panel + right panel |
| `timeline_h6` | 6-step journey | Horizontal axis + 6 nodes above/below |
| `three_column` | 3 comparable items | 3 equal cards side by side |
| `hero_card_left` | Character/profile | Large left card + right attribute grid |
| `panel_with_grid` | Complex data | Large panel containing internal grid |

#### 3.5 Spacing Rhythm
```text
Page margins: 20mm L/R, 16mm top, 12mm bottom
Title band: y 16-32mm (title + divider)
Body region: y 40-116mm
Footer: y 124-132mm
Card gap: 4mm
Group gap: 8mm
Card internal padding: 4mm
```

#### 3.6 Risk Checklist
- [ ] No more than 6 colors total
- [ ] No more than 4 font sizes per slide
- [ ] Body text minimum 12pt
- [ ] All cards use identical radius (3mm)
- [ ] Page markers: `x: 196mm, y: 126mm, width: 38mm`, align:right

#### 3.7 Asset Decision Gate

Before any page YAML is written, `design.md` must explicitly record the visual asset plan:

- Photo decision: `use`, `skip`, or `brief-only`
- Target slides that need photos, if any
- Search queries or source criteria for each photo
- Icon decision: `native semantic_icon`, `external SVG/PNG`, or `skip`
- Icon inventory: exact icon names, target slides, meaning, size class, stroke width, and color
- Fallback when network/API access is unavailable

This gate is mandatory even when the final decision is to use no photos. A deck may skip photo search only when `design.md` explains why diagrams, native icons, charts, or text-only layouts are clearer than photographic material.

### Step 4: Search Photo Assets

**This step is mandatory for every deck.** Do not write `deck.yml` or any page YAML before completing it.

1. Always run `python -m office_suite.tools.unsplash_assets` with at least 3 search queries tailored to the deck topic.
2. If `UNSPLASH_ACCESS_KEY` is not set, the tool still generates `asset_brief.md` and `manifest.json` — that is the minimum viable output.
3. Only after the tool has run may you decide which photos to actually use. Skipping the run entirely is a process defect.

Read `office_suite/guideline/design/unsplash_assets.md`, then execute:

```bash
python -m office_suite.tools.unsplash_assets \
  --output-dir output/<deck-name>/assets/photos \
  --topic "<deck topic>" \
  --query "<query 1: scene / mood / object relevant to topic>" \
  --query "<query 2: different angle or setting>" \
  --query "<query 3: third variation>" \
  --orientation landscape
```

Rules:
- Craft queries that match the deck's specific topic, not generic filler.
- Prefer 1-3 strong photos in a short deck, not images on every slide.
- Select images with clean negative space and colors compatible with the chosen preset.
- Use local downloaded JPG paths from `manifest.json` in page YAML.
- Preserve attribution metadata in `manifest.json`.
- Apply `blur` + `opacity` filters to full-bleed background images so text remains readable.
- If no suitable image is found, record that result in `design.md` and proceed with native diagram/icon treatment.
- Missing `asset_brief.md`, `manifest.json`, or a documented skip reason blocks the quality gate.

### Step 5: Design and Author semantic_icon Assets

**This step is mandatory for every deck.** Do not write any page YAML before it is complete.

Every deck must include at least 1-2 `semantic_icon` elements authored from basic primitives. These are PPT-native shapes (no external tools needed) composed from: `line`, `rectangle`, `rounded_rectangle`, `ellipse`, `circle`, `triangle`.

#### Workflow

1. **Design the icon set** — Identify 1-3 icons that visually reinforce the deck's message. Examples per domain:
   - Reading/books: open book, bookmark, lamp
   - Business: chart bar, handshake, target
   - Tech: chip, cloud, gear
   - Education: pencil, graduation cap, lightbulb
   - Health: heart, cross, leaf

2. **Write primitive recipes** — Each icon lives in a 100×100 coordinate space (viewBox). Use the deck's `accent` color. Example:

```yaml
- type: semantic_icon
  color: "<accent color>"
  stroke_width: 1.6
  position: { x: 117mm, y: 26mm, width: 20mm, height: 14mm }
  primitives:
    - { type: line, x1: 18, y1: 14, x2: 50, y2: 4 }
    - { type: line, x1: 50, y1: 4, x2: 82, y2: 14 }
    - { type: line, x1: 18, y1: 14, x2: 18, y2: 88 }
    - { type: line, x1: 82, y1: 14, x2: 82, y2: 88 }
    - { type: line, x1: 18, y1: 88, x2: 50, y2: 78 }
    - { type: line, x1: 50, y1: 78, x2: 82, y2: 88 }
    - { type: line, x1: 50, y1: 4, x2: 50, y2: 78 }
```

3. **Record the inventory** in `design.md` before writing page YAML:
   - Icon name, semantic meaning, primitive count, size, stroke width, color
   - Which slide(s) each icon appears on

4. **Add to page YAML** — Place the `semantic_icon` element in the target slide's YAML alongside other elements.

Rules:
- Author at least 1 icon for the cover or closing slide.
- Use one color from the deck palette, normally `accent`.
- Keep primitives minimal (5-15 primitives per icon).
- Do not use emoji, clip art, or external SVG/PNG as icons.
- Missing icon inventory or missing primitive recipes in design.md blocks the quality gate.

### Step 6: Generate YAML Files (Generate-All-First)

Prerequisite: `outline.md`, `design.md`, and the photo/icon asset plan are complete. If photos are used, page YAML must reference local image paths from `manifest.json`; if photos are skipped, `design.md` must contain the skip reason. If icons are used, page YAML must include the preplanned `semantic_icon.primitives`.

Write files in this order, all in one batch:

1. `deck.yml`
2. `pages/001_*.yml` through `pages/NNN_*.yml` (can use parallel sub-agents for pages)

Main file:
```yaml
version: "4.0"
type: presentation
title: "Presentation Title"
theme: default
style_preset: warm   # ← REQUIRED: one of the 10 presets from design/tokens.py
styles:
  h1:
    font: { family: "Microsoft YaHei UI", size: 36, weight: 700, color: "#D97706" }
  h2:
    font: { family: "Microsoft YaHei UI", size: 16, weight: 700, color: "#1C1917" }
  body:
    font: { family: "Microsoft YaHei UI", size: 13, weight: 400, color: "#1C1917" }
  caption:
    font: { family: "Microsoft YaHei UI", size: 10, weight: 400, color: "#78716C" }
pages:
  - pages/001_cover.yml
  - pages/002_content.yml
```
The `style_preset` auto-generates base styles; the `styles:` section can override individual tokens. Page YAML inline styles override both.

Page file rules:
- Every slide must pick a layout pattern from the library.
- Related elements must share a card container (`rounded_rectangle` with `bg_surface` fill).
- Card internal layout: title (H2) → divider → body (Body) → optional caption (Caption).
- Use `align: center`, `vertical_align: middle`, `margin: 0` for centered content inside cards.
- Never hand-tune coordinates to simulate centering.

### Step 7: Unified Quality Gate

After ALL files are written, run:

```bash
python -m office_suite.tools.check output/<deck-name>/deck.yml --render pptx --output-dir output/<deck-name>/check
```

Blocking issues (must fix):
- YAML parse errors, missing page files
- IR validation errors, failed render
- Out-of-bounds content
- Confirmed text overlap or truncation

Review items (consciously accept or fix):
- Font hierarchy warnings (>4 sizes)
- Color count warnings (>6 colors)
- Spacing warnings (intentional compact layout is acceptable)
- Decorative overlap

Fix order:
1. Syntax and missing-file errors
2. Out-of-bounds content
3. Text overflow and unreadable font sizes
4. Text occlusion
5. Misalignment and inconsistent spacing

## Layout System (Normative)

### Canvas
- 16:9, width: 254mm, height: 142.875mm
- Origin: top-left
- Constraints: `x + width <= 254mm`, `y + height <= 142.875mm`

### Page Regions
```text
Title band:     y 16-32mm
Body region:    y 40-116mm
Footer:         y 124-132mm
```

### Text Layout Fields
| Field | Values | Meaning |
|-------|--------|---------|
| `align` | left, center, right | Horizontal paragraph alignment |
| `vertical_align` | top, middle, bottom | Text frame vertical anchoring |
| `margin` | mm | Uniform internal margin |

For centered badges/labels inside shapes: set text box equal to shape bounds + `align: center` + `vertical_align: middle` + `margin: 0`.

### Card System
- Cards are containers, not decoration.
- Fill: `bg_surface`, radius: 3mm, border: 1pt `border` color.
- Do not use cards inside cards.
- Card text left-aligned for sentences; center-aligned for compact tiles.

### Repeated Elements
Repeated cards must be generated as a system:
- Same object type, width, height, internal alignment.
- Consistent gaps (4mm).
- Complete sequences. If the outline says 6 modules, render exactly 6.

## Visual Quality Rules

- **One message per slide**: Every content slide must have one dominant message. Move secondary detail to another slide.
- **Density limit**: Body text max 40-50 Chinese characters or ~80 English words per slide.
- **Data prominence**: In data slides, make the conclusion visually dominant; chart/table is supporting evidence.
- **Palette control**: Exactly 1 primary, 1 accent, neutrals, optional semantic colors. Never exceed 6 colors.
- **Typography control**: Max 4 font sizes per slide. Minimum body 12pt.
- **Alignment**: Use explicit layout fields for internal positioning; use coordinates only for container placement.

## Build and Convert

```python
from office_suite.dsl.parser import parse_yaml
from office_suite.ir.compiler import compile_document
from office_suite.renderer.pptx.deck import PPTXRenderer

doc = parse_yaml("output/my_deck/deck.yml")
ir_doc = compile_document(doc)
PPTXRenderer().render(ir_doc, "output/my_deck/my_deck.pptx")
```

CLI:
```bash
python -m office_suite build output/my_deck/deck.yml -o output/my_deck/my_deck.pptx
```

For non-PPT formats:
```python
from office_suite.tools.convert import convert_dsl_file
convert_dsl_file("input.yml", "output.docx", "docx")
convert_dsl_file("input.yml", "output.xlsx", "xlsx")
convert_dsl_file("input.yml", "output.pdf", "pdf")
convert_dsl_file("input.yml", "output.html", "html")
```

## Non-PPT Formats

### DOCX
- Single YAML file, `type: document`
- Clear heading hierarchy, concise paragraphs, tables for comparisons.
- Verify: `python -m office_suite.tools.check document.yml --render docx`

### XLSX
- Single YAML file, `type: spreadsheet`
- Model data as tables; use charts only for trends/comparisons.
- Preserve numeric types, dates, percentages.

### PDF
- Fixed layout, print-safe margins, explicit block sizing.
- High-resolution images; avoid blurry screenshots.

### HTML
- `type: presentation` for slide-like sections, `type: document` for document-like pages.
- Semantic structure, responsive readability.

## Project Directory Structure

```text
output/<deck-name>/
  outline.md          # Structure contract
  design.md           # Style contract (palette, typography, layout patterns, spacing)
  deck.yml            # Main entry
  pages/
    001_cover.yml
    002_content.yml
    ...
  <deck-name>.pptx    # Rendered output
  check/              # Quality gate outputs
```
