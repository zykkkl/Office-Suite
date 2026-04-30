# Font System

## Selection Principles

1. **Language matching**: When the user's query is in Chinese or requests a Chinese PPT, both Chinese and English fonts need to be specified; otherwise, only English fonts need to be set.
2. **Selection approach**: Prioritize highly readable fonts for body text. Use stylized fonts + special design treatments for titles or special pages.
3. **Name consistency**: **Make sure the font name is exactly consistent, including capitalization and spaces.**

## Recommended Font Families

### Microsoft YaHei UI (Default)

| Role | Size | Weight | Use |
|------|------|--------|-----|
| H1 (Title) | 32-36pt | 700 | Page titles, section headers |
| H2 (Subtitle) | 14-16pt | 700 | Card titles, subheaders |
| Body | 12-13pt | 400 | Descriptions, bullet text |
| Caption | 9-10pt | 400 | Labels, tags, page markers |

### Arial (Numeric/English)

Use for numbers, English text, and technical terms within Chinese presentations.

### STKaiti / Kai (Chinese Serif)

Use for formal presentations, literary content, or when seeking a classical aesthetic.

### SiYuan Song / Source Han Serif

Use for academic, literary, or design-oriented presentations requiring serif Chinese fonts.

## Font Size Scale (Strict 4-Level)

| Level | Size Range | Recommended | Use |
|-------|-----------|-------------|-----|
| H1 | 32-40pt | 36pt | Page titles, chapter headers |
| H2 | 14-18pt | 16pt | Card titles, section headers |
| Body | 12-14pt | 13pt | Descriptions, paragraphs |
| Caption | 9-11pt | 10pt | Labels, tags, metadata |

**Rule**: Never use more than 4 distinct font sizes on a single slide.

## Font Weight

| Weight | Value | Use |
|--------|-------|-----|
| Regular | 400 | Body text, descriptions |
| Bold | 700 | Titles, emphasis, keywords |
| Light | 300 | Decorative text (use sparingly) |

## Color Application

| Role | Dark Theme | Light Theme |
|------|-----------|-------------|
| Primary text | `#E8E4DC` | `#1A1A1A` |
| Secondary text | `#6B7280` | `#666666` |
| Accent | `#C9A84C` | `#1B3A6B` |

## Line Height Calculation

The actual rendered line height of a font is approximately `fontSize x 1.3`:

- Single-line text height = `fontSize x max(lineHeight, 1.3)`
- Multi-line text height = `fontSize x max(lineHeight, 1.3) x lines`

Example: `fontSize=14, lineHeight=1.2` -> single-line height = `14 x 1.3 = 18.2px`

## Text Width Calculation

- Chinese character width: approximately `fontSize`
- English/digit width: approximately `fontSize x 0.5~0.6`
- With letter spacing: total width = `fontSize x chars + letterSpacing x (chars - 1)`

## Font Availability

The following fonts are guaranteed available:

- Microsoft YaHei UI
- Arial
- Arial Bold
- SimSun
- SimHei

For web deployment or PDF export, prefer web-safe fonts or embed fonts.

## Chinese Font Alternatives

| Primary | Alternative 1 | Alternative 2 |
|---------|---------------|---------------|
| Microsoft YaHei UI | SiYuan Hei | Noto Sans SC |
| STKaiti | SiYuan Song | Noto Serif CJK SC |
| SimSun | FZSong | FangSong |
| SimHei | SiYuan Hei | Noto Sans SC |

## Font Pairing Rules

1. **Maximum 2 font families per slide** (1 for titles, 1 for body)
2. **Single font family preferred** for consistency
3. **Contrast through size/weight**, not through multiple font families
4. When mixing Chinese and English, prefer: Microsoft YaHei UI for both, or Microsoft YaHei UI for Chinese + Arial for English/numbers
