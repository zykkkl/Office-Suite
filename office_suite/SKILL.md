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

#### 3.2 Color Palette (strict limit)
Define exactly 5-6 colors:
```text
bg_primary:    #0A0E1A   (page background)
bg_surface:    #12182B   (card/panel background)
border:        #1E2642   (dividers, card borders)
accent:        #C9A84C   (titles, highlights, primary emphasis)
text_primary:  #E8E4DC   (body text)
text_muted:    #6B7280   (labels, captions, page numbers)
```
All emphasis must use opacity/brightness variations of these colors. Do not add new hues.

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

### Step 4: Generate YAML Files (Generate-All-First)

Write files in this order, all in one batch:

1. `deck.yml`
2. `pages/001_*.yml` through `pages/NNN_*.yml` (can use parallel sub-agents for pages)

Main file:
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

Page file rules:
- Every slide must pick a layout pattern from the library.
- Related elements must share a card container (`rounded_rectangle` with `bg_surface` fill).
- Card internal layout: title (H2) → divider → body (Body) → optional caption (Caption).
- Use `align: center`, `vertical_align: middle`, `margin: 0` for centered content inside cards.
- Never hand-tune coordinates to simulate centering.

### Step 5: Unified Quality Gate

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
