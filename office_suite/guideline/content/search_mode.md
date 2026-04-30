# Foraging Mode

When the user provides only a topic and requirements without source documents or pre-built outlines, enter foraging mode. The task is **information foraging** -- actively seeking, evaluating, and synthesizing information from external sources to construct a presentation from scratch.

## Cognitive Basis

Foraging mode applies **information foraging theory** (Pirolli & Card, 1995): organisms adopt strategies that maximize information gain per unit cost. In presentation design, this means:

- **Scent-following**: Prioritize sources with strong relevance signals (authoritative domains, recent dates, high citation counts)
- **Patch exploitation**: Deep-dive into high-value sources rather than skimming many low-value ones
- **Diet selection**: Choose information types (quantitative data, expert opinions, case studies) that maximize persuasive impact for the target audience

## Workflow

### Step 1: Information Foraging

Construct search queries optimized for the target audience's expertise level:

| Audience Level | Search Strategy |
|---------------|----------------|
| Expert | Technical terminology, academic databases, primary sources |
| General | Simplified terms, explainers, authoritative summaries |
| Decision-maker | Quantitative data, market reports, benchmark comparisons |

Foraging priorities:
1. **Quantitative data** -- statistics, measurements, market sizes, growth rates (highest persuasive value per word)
2. **Named examples** -- specific companies, products, people, incidents (concrete anchors for abstract claims)
3. **Expert attributions** -- quotes, findings, predictions from identifiable authorities (credibility transfer)
4. **Comparative frameworks** -- benchmarks, rankings, before/after, competitive matrices (relative positioning)

Record every source's URL for attribution during materialization.

### Step 2: Claim Synthesis

Raw search results are noisy. Synthesize them into a **claim inventory**:

For each cluster of related findings:
1. **Distill the core claim**: What is the single assertion this evidence supports?
2. **Rank evidence strength**: Primary data > expert analysis > secondary reporting > opinion
3. **Identify contradictions**: If sources disagree, note the disagreement and the evidence quality on each side

Target: 3-5 strong claims per intended slide, with at least one quantitative anchor per claim.

### Step 3: Narrative Construction

Without a pre-existing structure, construct a narrative arc from the synthesized claims:

**Discovery narrative** (knowledge-oriented):
Background -> Key Finding -> Implications -> Open Questions

**Persuasion narrative** (decision-oriented):
Problem -> Evidence -> Solution -> Expected Outcome

**Comparison narrative** (evaluation-oriented):
Options -> Evaluation Criteria -> Comparative Analysis -> Recommendation

The narrative arc should create **information scent continuity**: each slide's key message generates curiosity that the next slide satisfies.

### Step 4: Chunk-to-Slide Assembly

For each narrative position:

1. Select the dominant claim from the synthesized inventory
2. Attach the strongest evidence (prioritize quantitative > qualitative)
3. Choose visual encoding (chart, table, diagram, image)
4. Select layout pattern based on content structure
5. Annotate source URLs for attribution

### Step 5: Write structure contract

Produce `outline.md`:

```markdown
# Presentation Outline

## Cognitive Context
- Audience: [profile]
- Density target: [level]
- Content mode: foraged
- Sources consulted: [N sources across M queries]

## Narrative Arc
[The constructed narrative path through synthesized findings]

## Slide 1 [cover] -- Pattern: cover_center
- Key message: [topic-framing statement]
- Salience target: [title text]
- Evidence: [visual anchor]

## Slide 2 [content] -- Pattern: [pattern]
- Key message: [synthesized claim]
- Chunks:
  1. [claim + evidence + source URL]
  2. [claim + evidence + source URL]
- Salience target: [most impactful data point]
- Evidence type: [chart | table | diagram | text]
- Source: [URL]

## Slide N [closing] -- Pattern: cover_center
- Key message: [synthesis or call to action]
```

### Step 6: Source Quality Standards

Every factual claim in the outline must meet these criteria:

- **Traceability**: A specific source URL is recorded
- **Recency**: Data is from the last 3 years unless historical context requires older data
- **Authority**: Source is an established institution, peer-reviewed publication, or recognized expert
- **Specificity**: Claims include concrete numbers rather than vague qualifiers ("significant growth" -> "23% YoY growth")

When sources conflict, present the higher-quality source as the primary claim and note the disagreement in the outline.

### Step 7: Transition to Visual Design

After outline.md is complete:
1. If design.md has not been produced, complete the visual system design phase first
2. When both contracts exist, proceed to materialization (generate_slides.md Phase 4)
