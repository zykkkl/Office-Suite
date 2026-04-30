# Container Design Mode

When the user provides an existing presentation as a template, enter container design mode. The task is **structural extraction** -- identifying the template's reusable visual containers and content frameworks, then filling them with new content.

**This mode must only be entered when the user explicitly requests template usage.** Reading this file for non-template tasks is prohibited.

## Cognitive Basis

Container design applies **schema theory** (Bartlett, 1932): the audience perceives new content through pre-existing structural expectations. A template establishes a visual schema -- consistent spatial positions, recurring elements, predictable hierarchy. When new content fills these established containers, the audience's processing cost drops because the structure is already familiar.

The key distinction: the template provides **containers** (structural frames), not **content** (information). The container's spatial position, size, and styling are preserved. The content within is entirely new.

## Workflow

### Step 1: Template Ingestion

**User-uploaded PPTX template**:
1. Convert the PPTX to Office Suite YAML DSL
2. Generate visual screenshots for review
3. Read the converted deck.yml and all page YAML files

**Preset template**:
1. Read the template's deck.yml
2. Read all page YAML files under pages/

### Step 2: Structural Decomposition

Analyze the template's page anatomy. Every page decomposes into:

| Layer | Description | Reuse Policy |
|-------|-------------|-------------|
| **Fixed elements** | Navigation bars, logos, page numbers, decorative frames | Copy verbatim -- do not modify position, size, or style |
| **Title scaffold** | Page title position, font, size, alignment | Preserve position and style; replace text content |
| **Content frame** | The bounding box where variable content lives | Preserve bounds; all new content must fit within |
| **Decorative accents** | Color bands, divider lines, corner elements | Copy verbatim |

For each page type in the template, document this decomposition.

### Step 3: Element Inventory

Create a **fixed element catalog** -- every element that appears on multiple pages with consistent attributes:

```markdown
## Fixed Element Catalog

### Navigation Bar
- Type: shape (rectangle)
- Position: x:0mm, y:0mm, width:254mm, height:8mm
- Fill: bg_primary
- Content: [chapter titles as text elements]

### Page Number
- Type: text
- Position: x:196mm, y:128mm, width:38mm, height:6mm
- Style: Arial, 10pt, 400, text_muted
- Alignment: right

### Logo
- Type: image
- Position: x:220mm, y:4mm, width:24mm, height:8mm
```

During generation, these elements are **invariant** -- they appear on every applicable page with identical attributes.

### Step 4: Content Frame Analysis

For each content page type, define the **content frame** -- the spatial region where new content is placed:

```markdown
## Content Frame: Standard Content Page
- Bounds: x:20mm, y:40mm, width:214mm, height:78mm
- Title area: x:20mm, y:32mm, width:214mm, height:8mm
- Body area: x:20mm, y:42mm, width:214mm, height:72mm
- Constraints: All new content must fit within body area
```

### Step 5: Style Parameter Extraction

Extract the template's visual parameters and map to Office Suite tokens:

| Parameter | Source | Extraction Method |
|-----------|--------|------------------|
| Colors | Page backgrounds, card fills, text colors, accent elements | Map to 6-token system |
| Typography | Title fonts, body fonts, size hierarchy | Map to 4-level scale |
| Card parameters | Corner radius, border style, fill | Map to card system |
| Spacing | Margins, gaps, padding | Map to spacing rhythm |

### Step 6: Write style contract

Produce `design.md`:

```markdown
# Style Contract

## Template Context
- Design mode: container
- Source: [template file path or "user-uploaded"]
- Decomposition: [number of page types identified]

## Fixed Element Catalog
[Complete catalog with positions and attributes]

## Content Frames
[Per-page-type content frame definitions]

## Color Palette
| Token | Hex | Source in template |
|-------|-----|--------------------|

## Typography
| Level | Family | Size | Weight | Source in template |
|-------|--------|------|--------|--------------------|

## Layout Patterns
[Which template page structures map to which layout patterns]

## Risk Checklist
- [ ] 6 colors maximum
- [ ] 4 font sizes per slide maximum
- [ ] Body text minimum 12pt
- [ ] Card radius 3mm consistently
- [ ] Fixed elements copied verbatim
- [ ] Content within content frame bounds
```

### Step 7: Template Fidelity Rules

- **Fixed elements are invariant**: Navigation bars, logos, page numbers, decorative frames must be copied exactly. Do not adjust positions, sizes, colors, or fonts.
- **Content frames are boundaries**: All new content must fit within the defined content frame. Do not extend content into fixed element regions.
- **Layout diversity**: The same template page structure should not appear on more than 2 consecutive pages. Select among the template's page types based on content needs.
- **No structural inversion**: Do not change the template's layout direction (e.g., horizontal to vertical), remove fixed elements, or significantly alter content frame bounds.

### Step 8: Transition

After design.md is complete:
1. If outline.md has not been produced, complete the information architecture phase
2. When both contracts exist, proceed to materialization
