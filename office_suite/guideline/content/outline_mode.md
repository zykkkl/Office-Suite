# Architectural Mode

When the user provides a structured outline (page-by-page plan, chapter tree, or topic hierarchy), enter architectural mode. The existing structure becomes the **information architecture** -- the skeleton onto which visual and cognitive design is applied.

## Cognitive Basis

Architectural mode operates on **schema mapping**: the user has already invested cognitive effort into structuring their ideas. The task is to preserve this structure's logical integrity while translating it into a slide-native format that exploits spatial layout, visual hierarchy, and dual-channel encoding.

## Workflow

### Step 1: Structure Analysis

Classify the user's outline by completeness level:

| Level | Characteristics | Action |
|-------|----------------|--------|
| **Complete** | Per-page titles, content points, and page types specified | Map directly to slide specifications |
| **Semi-structured** | Chapter divisions and key points, no per-page allocation | Allocate points to pages, determine page types |
| **Hierarchical** | Topics and subtopics only | Decompose into page-level chunks, assign layout patterns |

Extract from the outline:
- Total information volume (number of distinct claims, data points, topics)
- Logical dependency chain (which points require prior context)
- Implicit structural needs (does the content require a TOC? chapter transitions?)

### Step 2: Expansion Policy

Determine the user's stance on content modification:

**Strict fidelity** (user explicitly says "follow my outline exactly" / "don't add or remove"):
- Preserve every point from the original outline verbatim
- Only perform structural mapping (assign page types, layout patterns)
- If cover/closing pages are absent, ask the user whether to add them

**Enrichment** (user explicitly says "expand" / "add detail" / "enrich"):
- Supplement the outline with supporting evidence, data, examples
- Mark all supplemented content with `[supplemented]` in the outline
- The user's original points remain the structural backbone

**Conservative** (no explicit instruction -- the default):
- Preserve the user's structure faithfully
- Suggest adding obviously missing structural pages (cover, closing)
- Do not expand body content unprompted

### Step 3: Chunk-to-Slide Mapping

For each content point in the user's outline, determine:

1. **Chunk grouping**: Which points form a coherent information unit that fits one slide's working memory budget?
   - Rule: One slide = one key message = one dominant cognitive chunk
   - Supporting evidence (data, examples, sub-points) forms sub-chunks within the slide

2. **Saliency assignment**: Which chunk should be the pre-attentive target (the thing the eye sees first)?
   - Typically the key metric, the conclusion, or the most surprising finding

3. **Composition selection**: Which custom composition best routes attention for this content? Use templates only as syntax/spacing references.

| Content Structure | Recommended Composition |
|------------------|-------------------------|
| Single narrative thread | `magazine_spread` or sparse editorial text |
| Two parallel concepts | `comparison_axis` |
| Three comparable options | `process_field` or asymmetric trio |
| Four feature/benefit pairs | `card_grid` only if equal weight is essential |
| Six categories or items | `card_grid` only for inventories; otherwise split into two slides or use a map/hub |
| Sequential process steps | `narrative_timeline` |
| Person/team with attributes | `annotated_artifact` or profile spread |
| Dataset with internal structure | `data_poster`, chart, or `map_or_hub` |

4. **Evidence type**: What visual evidence supports the key message?
   - Quantitative comparison -> chart
   - Multi-attribute comparison -> table
   - Process/relationship -> shape+text diagram
   - Spatial/geographic -> image

### Step 4: Write structure contract

Produce `outline.md` using this format:

```markdown
# Presentation Outline

## Cognitive Context
- Audience: [profile]
- Density target: [sparse | balanced | dense | saturated]
- Content mode: architectural
- Expansion policy: [strict | enrich | conservative]

## Narrative Arc
[2-3 sentences describing the emotional and logical progression across the deck]

## Slide 1 [cover] -- Pattern: cover_center
- Key message: [the single sentence the audience should remember]
- Salience target: [title text]
- Evidence: [visual anchor -- image, brand mark, decorative treatment]

## Slide 2 [content] -- Pattern: card_grid_2x2
- Key message: [one-sentence conclusion]
- Chunks:
  1. [chunk 1 -- one concept]
  2. [chunk 2]
  3. [chunk 3]
  4. [chunk 4]
- Salience target: [which chunk dominates visual attention]
- Evidence type: [chart | table | diagram | image | text]

## Slide N [closing] -- Pattern: cover_center
- Key message: [call to action or final takeaway]
```

### Step 5: Transition to Visual Design

After outline.md is complete:
1. If design.md has not been produced, complete the visual system design phase first
2. When both contracts exist, proceed to materialization (generate_slides.md Phase 4)
