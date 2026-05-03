# Structure Contract Template

This document defines the reusable structure for an Office Suite presentation. Use this template when creating `outline.md` for any generation task.

## Structure Contract Rules

1. **One message per slide** -- Each slide precisely conveys one core idea
2. **Page types must be explicit** -- Every page has a type: cover, table_of_contents, chapter, content, closing
3. **Composition assignment** -- Every page specifies a custom composition family and visual hook; templates are references, not constraints
4. **Chapter consistency** -- Either all chapters have transition pages or none do

## Slide Type Inventory

| Type | Role | Typical Count |
|------|------|---------------|
| cover | Title + organization + visual anchor | 1 |
| table_of_contents | Chapter overview / navigation | 0-1 |
| chapter | Chapter divider with number + title | 0-N (per chapter) |
| content | Main content slides | 8-20 |
| closing | Summary / call to action / contact | 1 |

**Target total**: 10-25 pages for a standard presentation.

## Composition Assignment Guide

### Cover and Closing Pages

| Composition | Use When |
|-------------|----------|
| `editorial_opener` | Cover/chapter with art-directed image, object, or visual field |
| `closing_poster` | Closing with sparse memorable call-to-action |

### Content Pages

| Composition | Use When |
|-------------|----------|
| `annotated_artifact` | One object/image/screenshot/diagram carries the explanation |
| `data_poster` | One metric or conclusion should dominate |
| `narrative_timeline` | Events, origin, process, or journey |
| `comparison_axis` | Two sides, tradeoffs, before/after, or contrast |
| `quote_wall` | A quote or voice needs emotional weight |
| `process_field` | Methods or steps should feel integrated rather than boxed |
| `magazine_spread` | Editorial explanation with headline, image/figure, and margin notes |
| `map_or_hub` | Factors, stakeholders, ecosystem, or relationships |
| `card_grid` | Equal-weight inventories only; not the default for content pages |

## Content Density Rules

- **One message per slide**: Each page answers one question
- **Maximum text**: 40-50 Chinese characters or ~80 English words per slide body
- **Data points**: 3-6 key indicators per page
- **Visual priority**: Charts, tables, structured graphics over pure text
- **Evidence support**: Every argument backed by data, chart, or named source

## Page Marker Convention

All pages (except cover) include a page marker:
- Position: `x: 196mm, y: 128mm, width: 38mm, height: 6mm`
- Alignment: right
- Font: Arial, 10pt, 400 weight, `text_muted` color
- Format: "NN / TT" (current page / total pages)

## Outline Format Template

```markdown
# Presentation Outline

## Context
- Audience: [target audience description]
- Content mode: [outline | summary | search]
- Expansion policy: [strict | enrich | conservative]
- Page count: [N]

## Page 1 [cover] -- Layout: cover_center
- Title: [presentation title]
- Key message: [subtitle or tagline]
- Content: [speaker, date, organization]
- Visual: [description of visual treatment]

## Page 2 [table_of_contents] -- Layout: card_grid_2x2
- Title: [TOC heading]
- Key message: [chapter overview]
- Content:
  1. Chapter One Title
  2. Chapter Two Title
  3. ...

## Page 3 [chapter] -- Layout: cover_center
- Title: [chapter number and name]
- Key message: [chapter subtitle]
- Visual: [decorative treatment]

## Page 4 [content] -- Layout: [pattern_name]
- Title: [conclusion sentence]
- Key message: [one-sentence core message]
- Content:
  - [point 1]
  - [point 2]
  - [point 3]
- Visual: [chart type, image description, or layout notes]
- Source: [URL or reference]

## Page x [closing] -- Layout: cover_center
- Title: [closing title]
- Key message: [core takeaway or call to action]
```

## Cross-Reference Patterns

- Financial/forecast slides form a self-contained series, ordered logically (past -> present -> projection)
- Technical comparison slides reference advantages established in positioning slides
- Appendix slides provide evidence backing for arguments in the main narrative
