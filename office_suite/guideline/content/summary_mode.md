# Distillation Mode

When the user provides a long document (paper, report, thesis, article) and requests a presentation based on its content, enter distillation mode. The task is **information distillation** -- extracting the cognitive essence from a dense source and reconstituting it in slide-native form.

## Cognitive Basis

Distillation mode applies **information scent theory** (Pirolli & Card, 1999): readers navigate information environments by following perceived value signals. A document's information architecture optimizes for sequential deep reading. A presentation must restructure the same information for **rapid visual scanning** -- the audience should extract the key message of each slide within 3-5 seconds of seeing it.

This requires three transformations:
1. **Abstraction**: Elevate specific arguments to generalizable claims
2. **Compression**: Reduce verbose explanations to essential propositions
3. **Ranking**: Promote the most audience-relevant information to visual salience

## Workflow

### Step 1: Document Decompression

Read the source document systematically. For each section, extract:

| Extraction Layer | What to Capture |
|-----------------|----------------|
| **Claims** | Explicit assertions, findings, conclusions |
| **Evidence** | Data points, statistics, experimental results, case studies |
| **Logic** | Causal chains, comparisons, contrasts, progressions |
| **Novelty** | What the audience would not already know or expect |

Build a **claim-evidence inventory**: a flat list of (claim, supporting evidence) pairs. This inventory is the raw material for slide construction.

### Step 2: Audience Relevance Filtering

Apply the audience cognitive profile from generate_slides.md Phase 1 to filter the inventory:

- **Expert audience**: Retain methodology details, statistical rigor, nuanced findings
- **General audience**: Promote conclusions, simplify mechanisms, add contextual framing
- **Decision-maker audience**: Elevate implications, quantified impact, actionable recommendations

Mark each inventory item as: `retain` / `simplify` / `demote` / `omit`.

### Step 3: Narrative Reconstruction

The document's original structure may not be optimal for presentation. Reconstruct a narrative arc based on the document type:

| Document Type | Presentation Narrative |
|--------------|----------------------|
| Research paper | Problem -> Method -> Finding -> Implication |
| Industry report | Situation -> Trend -> Tension -> Opportunity |
| Technical document | Architecture -> Components -> Behavior -> Tradeoffs |
| Business case | Need -> Analysis -> Solution -> Expected outcome |

The narrative arc defines the **information scent trail** -- the logical path the audience follows across slides. Each slide's key message should create anticipation for the next.

### Step 4: Chunk-to-Slide Assembly

For each slide in the narrative arc:

1. **Select the dominant claim**: The single most important assertion for this narrative position
2. **Attach supporting evidence**: The strongest 2-3 evidence items from the inventory
3. **Choose encoding**: How to present the claim-evidence pair visually
   - Quantitative evidence -> chart element
   - Multi-dimensional comparison -> table element
   - Process/relationship -> shape diagram
   - Conceptual framework -> card grid
4. **Select layout pattern**: Match content structure to attention routing pattern

### Step 5: Write structure contract

Produce `outline.md`:

```markdown
# Presentation Outline

## Cognitive Context
- Audience: [profile]
- Density target: [level]
- Content mode: distilled
- Source: [document name/type]
- Items filtered: [N retained, M simplified, K omitted]

## Narrative Arc
[The reconstructed narrative path through the source material]

## Slide 1 [cover] -- Pattern: cover_center
- Key message: [title derived from the document's core thesis]
- Salience target: [title text]
- Evidence: [visual anchor]

## Slide 2 [content] -- Pattern: [pattern]
- Key message: [dominant claim at this narrative position]
- Chunks:
  1. [claim + evidence pair]
  2. [claim + evidence pair]
- Salience target: [most surprising or impactful chunk]
- Evidence type: [chart | table | diagram | text]
- Source reference: [section/page in original document]

## Slide N [closing] -- Pattern: cover_center
- Key message: [synthesis or implication]
```

### Step 6: Fidelity Rules

- **Distill, do not rewrite**: Preserve the source document's core logic and key findings. Do not introduce claims absent from the source.
- **Data integrity**: Numerical data from the source must be preserved exactly. When rounding for visual display, note the precision level.
- **Attribution**: When the presentation includes claims or data from the source, annotate the source reference in the outline. This supports hyperlink annotation during materialization.

### Step 7: Transition to Visual Design

After outline.md is complete:
1. If design.md has not been produced, complete the visual system design phase first
2. When both contracts exist, proceed to materialization (generate_slides.md Phase 4)
