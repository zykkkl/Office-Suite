# Zero-Based Design Mode

When no visual reference exists, design the visual system from first principles. The visual system is derived entirely from the cognitive context -- audience profile, topic semantics, and information density requirements.

## Cognitive Basis

Zero-based design applies **semantic color mapping** and **typographic hierarchy theory**:

- **Semantic color mapping**: Colors carry cultural and psychological associations. The chosen palette should reinforce the presentation's emotional tone -- authority (deep neutrals), innovation (unexpected accent choices), urgency (warm saturated tones), calm (cool desaturated tones).
- **Typographic hierarchy**: Font size ratios create visual priority. The eye targets the highest-contrast element first. A 2.5:1 size ratio between H1 and Body creates clear dominance; ratios below 1.5:1 cause the audience to search for the hierarchy.

## Workflow

### Step 1: Scenario Profile Selection

Read the profile that best matches the presentation's domain:

| Profile | Domain |
|---------|--------|
| `profiles/general.md` | Default for unmatched scenarios |
| `profiles/academic.md` | Research, thesis defense, conferences |
| `profiles/business_insight.md` | Market analysis, consulting, equity research |
| `profiles/education.md` | Teaching, training, courseware |
| `profiles/promotion.md` | Brand launches, marketing, creative showcases |
| `profiles/strategic.md` | Business plans, fundraising, strategic planning |
| `profiles/work_report.md` | Work summaries, performance reviews, government reports |

The profile provides domain-specific constraints (density targets, prohibited patterns, narrative conventions). All dimensions below default to the profile's guidance unless the user provides explicit overrides.

### Step 2: Color Palette Derivation

The 6-color token system is mandatory. Derive actual hex values through this decision chain:

**Step 2a -- Determine emotional temperature**:
| Temperature | Association | Palette Tendency |
|------------|-------------|-----------------|
| Cool-authoritative | Trust, stability, professionalism | Deep blues, blue-grays, navy |
| Warm-confident | Energy, optimism, ambition | Amber, copper, deep reds |
| Neutral-refined | Sophistication, balance, restraint | Charcoal, stone, cream |
| Dark-dramatic | Premium, focus, immersion | Near-black backgrounds, light text |

**Step 2b -- Select the accent color** (the salience beacon):
The accent color is the highest-contrast element on the canvas. It should:
- Have a clear semantic association with the topic (e.g., green for sustainability, amber for finance)
- Create sufficient contrast against both `bg_primary` and `bg_surface` (WCAG AA minimum)
- Not be blue/cyan unless the topic specifically warrants it (blue is the most overused default in presentations)

**Step 2c -- Derive the remaining tokens from the accent**:
- `bg_primary`: Derived from the temperature (dark for dramatic, light for refined)
- `bg_surface`: Slightly elevated from `bg_primary` (lighter in light themes, marginally lighter in dark themes)
- `border`: Low-contrast boundary (just enough to perceive the edge)
- `text_primary`: Maximum contrast against `bg_primary`
- `text_muted`: ~40% opacity of `text_primary` against `bg_primary`

### Step 3: Typography Configuration

Select fonts from `format/fonts.md` available list:

| Role | Selection Criteria |
|------|-------------------|
| Titles (H1/H2) | High x-height, clear letterforms at large sizes, distinctive personality |
| Body | Maximum readability at 12-13pt, neutral personality, proven screen performance |
| Numeric/Arial | Tabular figures preferred, clear digit distinction (0/O, 1/l/I) |

When the presentation is in Chinese, specify both Chinese and English font families.

Typography rhythm across the deck:
- H1 at 36pt on cover/chapter pages, 32pt on content pages
- H2 at 16pt consistently
- Body at 13pt for balanced density, 12pt for dense content
- Caption at 10pt consistently

### Step 4: Layout Pattern Strategy

Select 3-5 layout patterns from the library that provide sufficient variety for the deck's page count:

- **Rule of non-repetition**: The same layout pattern should not appear on more than 2 consecutive content pages
- **Progressive complexity**: Earlier content pages use simpler patterns (title_body, split_50_50), later pages can use more complex patterns (panel_with_grid, card_grid_3x2)
- **Climactic moments**: Key data pages or turning points can use dedicated patterns that break the established rhythm

### Step 5: Write style contract

Produce `design.md`:

```markdown
# Style Contract

## Cognitive Context
- Audience: [profile]
- Density target: [level]
- Design mode: zero-based
- Profile baseline: [profile file name]

## Color Palette
| Token | Hex | Semantic Role |
|-------|-----|--------------|
| bg_primary | #... | Page ground |
| bg_surface | #... | Card ground |
| border | #... | Boundary signal |
| accent | #... | Attention attractor |
| text_primary | #... | Primary meaning |
| text_muted | #... | Metadata |

## Typography
| Level | Family | Size | Weight | Role |
|-------|--------|------|--------|------|
| H1 | ... | 36pt | 700 | Salience anchor |
| H2 | ... | 16pt | 700 | Category label |
| Body | ... | 13pt | 400 | Evidence carrier |
| Caption | ... | 10pt | 400 | Metadata layer |

## Layout Patterns
[List selected patterns and their intended use]

## Spacing
[Standard rhythm or overrides]

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
