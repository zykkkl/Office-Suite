# Analogical Design Mode

When the user provides visual references (images, websites, screenshots), enter analogical design mode. The task is **analogical transfer** -- extracting abstract visual principles from the reference source and mapping them onto Office Suite's design token system.

## Cognitive Basis

Analogical design applies **structure mapping theory** (Gentner, 1983): effective analogy transfers relational structure, not surface features. The goal is NOT to replicate the reference pixel-by-pixel. The goal is to identify the reference's underlying design logic (hierarchy strategy, color relationships, spatial organization) and express that logic through Office Suite's constraints.

Surface features (specific hex values, exact pixel positions) are rarely transferable. Relational structures (the ratio between title and body size, the contrast between primary and secondary colors, the rhythm of spacing) are universally transferable.

## Workflow

### Step 1: Define Transfer Scope

Determine what to extract from the reference:

| Scope | What Transfers | What Does Not |
|-------|---------------|---------------|
| Style only | Color relationships, typography hierarchy, visual tone | Layout structure, content |
| Style + layout | Above + spatial organization patterns | Specific content, element counts |
| Full replication | Everything including content | -- (requires explicit user request) |

Default scope (when user does not specify): style + layout.

### Step 2: Visual Principle Extraction

Analyze the reference source across these dimensions. For each dimension, extract the **principle** (the why), not just the parameter (the what).

**2a -- Color relationship analysis**:
- How many distinct color roles exist? (Not how many colors -- how many functional roles)
- What is the contrast strategy? (High contrast for emphasis? Low contrast for subtlety?)
- What is the temperature? (Warm/cool/neutral)
- Where does the eye land first? (What color creates the highest salience?)

**2b -- Typographic hierarchy analysis**:
- What is the size ratio between the largest and smallest text? (Indicates hierarchy intensity)
- Is weight contrast or size contrast the primary hierarchy driver?
- What is the text density per visual unit?
- Are there distinctive treatments (all-caps, letter spacing, serif/sans contrast)?

**2c -- Spatial organization analysis**:
- What is the margin-to-content ratio? (Generous margins = premium feel; tight margins = information density)
- How is content grouped? (Cards, whitespace, lines, color blocks)
- What is the visual rhythm? (Even grid? Asymmetric? Editorial?)
- What reading path does the layout suggest? (Z-pattern, F-pattern, center-out, linear)

**2d -- Visual tone analysis**:
- First impression in 3 words (e.g., "clean corporate authority")
- Dominant visual weight (text-heavy? image-heavy? balanced?)
- Decoration strategy (zero decoration? functional decoration? decorative elements?)

### Step 3: Map to Office Suite Tokens

Transfer extracted principles into Office Suite's 6-token system:

| Reference Dimension | Office Suite Token | Mapping Rule |
|-------------------|-------------------|-------------|
| Dominant background | `bg_primary` | Map the reference's page ground color |
| Container/panel fill | `bg_surface` | Map with ~10% brightness offset from bg_primary |
| Separating lines/borders | `border` | Map the reference's lowest-contrast structural color |
| Highest-salience color | `accent` | Map the color that creates the strongest eye-catch |
| Primary text | `text_primary` | Maximum contrast against bg_primary |
| Secondary text | `text_muted` | ~40% contrast of text_primary |

Map typographic hierarchy to the 4-level scale:

| Reference Level | Office Suite Level | Size (pt) |
|----------------|-------------------|-----------|
| Cover/hero title | H1 | 32-36 |
| Section/card title | H2 | 14-16 |
| Body/paragraph | Body | 12-13 |
| Label/metadata | Caption | 9-10 |

### Step 4: Identify Design Anchor

If the reference belongs to a recognizable design lineage, note it:

| Lineage | Characteristics |
|---------|----------------|
| Swiss International | Grid-based, sans-serif, high contrast, minimal decoration |
| Editorial/Magazine | Asymmetric layouts, image-text tension, generous whitespace |
| Consulting firm | Dense text, conclusion-first titles, zero decoration, chart-heavy |
| Tech keynote | Large imagery, minimal text, dramatic lighting, oversized typography |
| Academic | Structured, chart-centric, complete annotations, restrained palette |

The lineage serves as a **design compass** -- when specific decisions are ambiguous, the lineage's principles provide tiebreaking guidance.

### Step 5: Write style contract

Produce `design.md`:

```markdown
# Style Contract

## Transfer Context
- Design mode: analogical
- Reference scope: [style | style+layout | full replication]
- Design lineage: [lineage name, if identifiable]
- Transfer notes: [what aspects of the reference are being preserved and why]

## Visual Principle Extraction
[Summarize the 4 analysis dimensions and the extracted principles]

## Color Palette
| Token | Hex | Derivation from reference |
|-------|-----|--------------------------|
| bg_primary | #... | [how derived] |
| bg_surface | #... | [how derived] |
| border | #... | [how derived] |
| accent | #... | [how derived] |
| text_primary | #... | [how derived] |
| text_muted | #... | [how derived] |

## Typography
| Level | Family | Size | Weight | Reference correspondence |
|-------|--------|------|--------|-------------------------|

## Layout Patterns
[Which patterns from the library approximate the reference's spatial organization]

## Risk Checklist
- [ ] 6 colors maximum
- [ ] 4 font sizes per slide maximum
- [ ] Body text minimum 12pt
- [ ] Card radius 3mm consistently
- [ ] Page marker: x:196mm, y:128mm, w:38mm, align:right
```

### Step 6: Transition

After design.md is complete:
1. If outline.md has not been produced, complete the information architecture phase
2. When both contracts exist, proceed to materialization
