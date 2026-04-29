# Office Suite 4.0

## Scope

Use this skill for Office document generation from the Office Suite YAML DSL, especially PowerPoint/PPTX generation. The runtime path is:

```text
YAML DSL -> Parser -> IR Document -> Renderer -> .pptx / .docx / .xlsx / .pdf / .html
```

PPT generation has extra workflow requirements because presentation quality depends heavily on page-level planning and layout. DOCX, XLSX, PDF, and HTML generation remain supported through the same parser, compiler, and renderer pipeline.

## PPT Generation Workflow

For every new PPT task, create an isolated project directory and keep all task artifacts together:

```text
output/<deck-name>/
  outline.md          # Content plan, one section per slide
  design.md           # Visual system and layout rules
  deck.yml            # Main presentation entry file
  pages/
    001_cover.yml     # One YAML file per slide
    002_agenda.yml
    003_content.yml
```

Do not put the whole deck into one giant `slides:` YAML unless the user explicitly asks for a single-file example. The preferred format is a small main `deck.yml` plus one YAML file per slide under `pages/`.

Before generating or revising any PPT/PPTX YAML, you MUST read `office_suite/guidelines/ppt_layout_system.md` first and follow it. Do not proceed to YAML generation or layout revision before reading it.

### Step 1: Understand Inputs

- Read all user-provided source files first.
- Identify language, audience, page count, required data, tone, and visual constraints.
- If the user gives only a topic, create reasonable content; use browsing only when current or source-specific accuracy is required.
- Decide the content mode:
  - `outline`: the user supplied a page plan, chapter tree, or structured outline.
  - `summary`: the user supplied a long document and wants it distilled into slides.
  - `research`: the user supplied only a topic or sparse requirements and expects content to be developed.
- Decide the visual mode:
  - `creative`: no visual reference; create a suitable design from scenario, audience, and topic.
  - `reference`: user supplied screenshots, a website, images, or a style sample.
  - `template`: user explicitly asked to follow a provided template or existing PPT.
- Record these mode decisions in `outline.md` and `design.md` so later YAML generation has stable instructions.

### Step 2: Write `outline.md`

Persist a page-level outline before writing YAML. Include:

- Deck title and target audience
- Content mode and expansion policy
- Slide count and slide-by-slide story flow
- For each slide: title, key message, content bullets, suggested visual treatment, and any source/citation notes
- Explicit notes for charts, tables, diagrams, images, or callouts

Expansion policy:

- If the user asks to follow provided content exactly, preserve their structure and wording as much as possible. Do not add unsupported claims.
- If the user asks for enrichment, add supporting examples, data, and framing, and mark what was supplemented.
- If the user is silent, stay conservative: clarify structure, condense content for slides, and only add obvious missing structural pages such as cover or closing when appropriate.
- For source-derived decks, every important claim, number, or quote in the outline should trace back to the provided source or a cited URL.

Recommended outline shape:

```markdown
# Presentation Outline

## Context
- Audience:
- Content mode:
- Expansion policy:
- Page count:

## Page 1 [cover]
- Title:
- Key message:
- Content:
- Visual:

## Page 2 [content]
- Title:
- Key message:
- Content:
- Visual:
- Source:
```

### Step 3: Write `design.md`

Persist the visual design before writing YAML. Include:

- Canvas: 16:9, `254mm x 142.875mm`
- Visual mode and reference/template scope, if any
- Typography scale and font choices
- Color palette with exact hex values
- Reusable page patterns: cover, section, content, chart/table, closing
- Grid, margins, spacing, card radius, and image treatment
- Rules for text density, hierarchy, contrast, and alignment
- Theme YAML snippet compatible with the Office Suite DSL `styles:` field
- A task-specific risk checklist: colors to avoid, likely layout failure points, minimum readable font sizes, and any scenario-specific decoration limits

When a visual reference is provided, analyze it by role rather than copying it: color roles, type hierarchy, spacing rhythm, image treatment, table/chart style, and recurring layout patterns. If exact replication is requested, reproduce the user-provided content and layout as closely as the Office Suite DSL allows; otherwise, adapt the visual language to the new content.

### Step 4: Generate YAML Files

Write files in this order:

1. `deck.yml`
2. `pages/001_*.yml`, `pages/002_*.yml`, etc. in slide order

Main file example:

```yaml
version: "4.0"
type: presentation
title: "Presentation Title"
theme: default

styles:
  title:
    font: { family: "Microsoft YaHei UI", size: 34, weight: 700, color: "#0F172A" }
  body:
    font: { family: "Microsoft YaHei UI", size: 16, weight: 400, color: "#334155" }

pages:
  - pages/001_cover.yml
  - pages/002_agenda.yml
```

Page file example:

```yaml
layout: blank
background:
  color: "#FFFFFF"
elements:
  - type: text
    content: "Presentation Title"
    position: { x: 22mm, y: 34mm, width: 160mm, height: 18mm }
    style:
      font: { family: "Microsoft YaHei UI", size: 36, weight: 700, color: "#0F172A" }
```

The parser also accepts legacy single-file documents with top-level `slides:` for backward compatibility.

## Layout Requirements

- Use the 16:9 coordinate system: width `254mm`, height `142.875mm`.
- Never use `190.5mm` as a slide height for 16:9 PPTs.
- Keep `y + height <= 142.875mm` and `x + width <= 254mm`.
- Prefer stable grids and repeated positions across related slides.
- Estimate text box size before writing YAML. Line height is roughly `font size x 1.3`; allocate enough height for all lines.
- Use `wrap: false` or an equivalent custom flag only for text intended to stay on one line; otherwise size text boxes for wrapping.
- Avoid overlapping readable text with shapes, images, or other text.
- Avoid excessive font-size reduction to hide overflow. Condense content or redesign the layout first.
- For content-heavy slides, split into multiple slides instead of crowding the page.
- For centered badges, numbers, chips, and card labels, use explicit text layout fields such as `align: center`, `vertical_align: middle`, and `margin: 0`; do not rely on hand-tuned coordinates.

## Visual Quality Rules

- Use real layout: hierarchy, alignment, rhythm, whitespace, and contrast.
- Make cover, section, and closing pages visually distinct.
- Use images only when they support the page message. Prefer relevant full-bleed or cropped imagery over decorative placeholders.
- Build charts/tables with native DSL elements instead of screenshots.
- Keep palettes controlled: usually 1 primary, 1 accent, neutrals, and optional semantic colors.
- Use consistent title, footer, page number, and recurring navigation placement when present.
- Use several compatible content-page patterns across a deck so pages do not all share the same arrangement.
- For table-of-contents pages, treat the page as navigation/information design, not a plain bullet list.
- If chapter divider pages are used, apply them consistently across all major chapters.
- Keep each content slide centered on one main message. Move secondary detail to another slide rather than shrinking text below readable size.
- In data slides, make the conclusion visually dominant and the chart/table supporting, not the reverse.

## PPT Asset Rules

- Prefer user-provided images and source materials when they are relevant and high quality.
- If external images are needed, choose images that match `design.md` and are directly connected to the slide message.
- Do not replace an image-dependent layout with a generic gradient, solid block, or decorative shape unless the design explicitly calls for it.
- Do not use screenshots of charts or tables when native DSL chart/table elements can express the same information.
- Keep image paths resolvable from the generated project. If assets are local, keep them under the same project directory.

## Build and Convert

```python
from office_suite.dsl.parser import parse_yaml
from office_suite.ir.compiler import compile_document
from office_suite.renderer.pptx.deck import PPTXRenderer

doc = parse_yaml("output/my_deck/deck.yml")
ir_doc = compile_document(doc)
PPTXRenderer().render(ir_doc, "output/my_deck/my_deck.pptx")
```

CLI-style usage:

```bash
python -m office_suite build output/my_deck/deck.yml -o output/my_deck/my_deck.pptx
```

For non-PPT formats, use the matching renderer or conversion helper:

```python
from office_suite.tools.convert import convert_dsl_file

convert_dsl_file("input.yml", "output.docx", "docx")
convert_dsl_file("input.yml", "output.xlsx", "xlsx")
convert_dsl_file("input.yml", "output.pdf", "pdf")
convert_dsl_file("input.yml", "output.html", "html")
```

## PPT Verification

After YAML generation:

1. Parse `deck.yml`.
2. Compile to IR.
3. Compare the generated pages against `outline.md` and `design.md`: page count, slide order, promised module/step/day counts, and any required visual treatments must match unless a documented revision explains the change.
4. Run available validation/lint checks. Prefer the unified quality gate:
   `python -m office_suite.tools.check output/<deck-name>/deck.yml --render pptx --output-dir output/<deck-name>/check`
5. Render PPTX.
6. Fix parse errors, bounds issues, text overflow, occlusion, poor contrast, missing sequence items, outline/page mismatches, and obvious whitespace imbalance.

Warnings about overflow, occlusion, underfilled text boxes, or out-of-bounds content should be treated as real visual defects unless the issue is intentional decoration. After each fix pass, re-run the relevant check or render step until there are no unexpected errors or warnings.

Fix order:

1. Syntax and missing-file errors.
2. Elements outside the slide bounds.
3. Text overflow and unreadable font sizes.
4. Text or data occlusion.
5. Misalignment, inconsistent common elements, and unbalanced whitespace.

When fixing layout, adjust related elements together. For example, if a text box grows, also resize the backing shape or adjacent visual group so the page still looks intentional.

## Supported Formats

- `.pptx` - PowerPoint
- `.docx` - Word
- `.xlsx` - Excel
- `.pdf` - PDF
- `.html` - HTML

## DOCX Generation

Use DOCX when the user asks for a report, proposal, memo, article, contract-style draft, handbook, documentation, or any Word document.

Recommended file organization:

```text
output/<doc-name>/
  source_notes.md       # Optional notes, extracted source material, or drafting plan
  document.yml          # Single YAML source
  <doc-name>.docx
```

Authoring rules:

- Use a single YAML file by default.
- Use `type: document` when the output is primarily a Word document.
- Organize content into logical sections using the existing document/slide-like page structure accepted by the renderer.
- Prefer clear heading hierarchy, concise paragraphs, tables for structured comparisons, and figures only when they support the text.
- Do not apply PPT-specific canvas rules such as one YAML per slide or `254mm x 142.875mm` unless exporting the same content as a presentation.
- Keep styles conservative: readable body font, consistent heading sizes, enough table padding, and strong contrast.

Verification:

- Parse and compile the YAML.
- Run `python -m office_suite.tools.check document.yml --render docx`.
- Open or inspect the rendered document when possible; check heading order, table fit, missing images, and pagination-sensitive content.

## XLSX Generation

Use XLSX when the user asks for spreadsheets, financial models, trackers, schedules, tables, calculators, dashboards, data cleanup, or workbook-style output.

Recommended file organization:

```text
output/<workbook-name>/
  workbook.yml          # Single YAML source
  data/                 # Optional CSV/TSV/source data
  <workbook-name>.xlsx
```

Authoring rules:

- Use a single YAML file by default.
- Use `type: spreadsheet` when the output is primarily an Excel workbook.
- Model data as tables first; use charts only when they clarify trends, comparisons, composition, or variance.
- Preserve numeric types, dates, percentages, and currency semantics instead of writing everything as text.
- Prefer formulas for calculated columns and summary metrics when the workbook should remain editable.
- Keep layouts practical: frozen-style header thinking, clear sheet titles, readable column widths, restrained colors, and consistent number formats.
- Avoid presentation-only decoration. XLSX output should be functional and easy to audit.

Verification:

- Parse and compile the YAML.
- Run `python -m office_suite.tools.check workbook.yml --render xlsx`.
- Check that tables have the expected row/column counts, formulas are present, key numbers are formatted correctly, and charts reference the intended data.

## PDF Generation

Use PDF when the user asks for a fixed-layout handout, export, printable report, certificate, flyer, shareable final document, or a PDF version of a presentation/document.

Recommended file organization:

```text
output/<pdf-name>/
  document.yml          # Single YAML source, or deck.yml for presentation-derived PDF
  <pdf-name>.pdf
```

Authoring rules:

- Use a single YAML file for document-style PDFs.
- If the PDF is exported from a presentation, the PPT multi-file workflow may be used and then rendered to PDF from the compiled IR.
- Treat PDF as fixed layout: explicitly size important blocks, leave print-safe margins, and avoid relying on viewer reflow.
- Use vector-like shapes, native text, tables, and charts where possible.
- Use high-resolution images; avoid blurry screenshots when the content can be recreated with text/table/chart elements.

Verification:

- Parse and compile the YAML.
- Run `python -m office_suite.tools.check document.yml --render pdf`.
- Review page count, clipped content, table overflow, image quality, and whether printable margins are acceptable.

## HTML Generation

Use HTML when the user asks for a web preview, interactive-ish document, browser-readable export, static page, or an HTML version of the generated content.

Recommended file organization:

```text
output/<html-name>/
  page.yml              # Single YAML source
  assets/               # Optional local images or media
  <html-name>.html
```

Authoring rules:

- Use a single YAML file by default.
- Choose `type: presentation` for slide-like HTML sections, or `type: document` for document-like pages.
- Keep assets colocated and use paths that the renderer can resolve.
- Ensure text hierarchy, contrast, and responsive readability; do not assume PPT coordinates will produce a good web page unless the goal is slide preview.
- Prefer semantic structure and native text over rasterized text images.

Verification:

- Parse and compile the YAML.
- Run `python -m office_suite.tools.check page.yml --render html`.
- Open the HTML when possible and check layout, missing assets, text overflow, and mobile/desktop readability.

## Non-PPT Rule

The multi-file `deck.yml` + `pages/` workflow, mandatory `outline.md`, and mandatory `design.md` are preferred for PPT/PPTX only. For DOCX, XLSX, PDF, and HTML, use their format-specific guidance above and keep the existing single-file YAML workflow unless the user explicitly requests otherwise.
