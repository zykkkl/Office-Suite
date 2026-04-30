# Office Suite DSL Format Specification

## Coordinate System and Units

- Canvas: 16:9, width: 254mm, height: 142.875mm
- Origin: top-left corner (0, 0)
- Units: mm (millimeters)
- Position: `{ x, y, width, height }` where x/y are absolute positions from origin
- Constraints: `x + width <= 254mm`, `y + height <= 142.875mm`

## Multi-File Structure

Office Suite DSL uses a multi-file structure for presentations:

```text
project/
  deck.yml              # Main entry file (title, theme, styles, page list)
  pages/                # Page file directory
    001_cover.yml       # One YAML file per slide
    002_content.yml
    003_chart.yml
```

## Main Entry File (deck.yml)

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

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| version | string | Yes | DSL version, currently "4.0" |
| type | string | Yes | Document type: "presentation", "document", "spreadsheet" |
| title | string | Yes | Document title |
| theme | string | No | Theme name, "default" if omitted |
| styles | object | No | Named style definitions |
| pages | array | Yes | Page file path list (relative to main file) |
| style_preset | string | No | Design token preset name |
| data | object | No | Global data bindings |

### Style Definitions

Styles define reusable text styles:

```yaml
styles:
  h1:
    font: { family: "Microsoft YaHei UI", size: 36, weight: 700, color: "#C9A84C" }
    text_effect:
      shadow: { blur: 8, offset: [0, 2], color: "#000000" }
```

## Page File (pages/001_cover.yml)

```yaml
layout: blank
background:
  color: "#0A0E1A"
elements:
  - type: text
    content: "Title Text"
    position: { x: 20mm, y: 16mm, width: 160mm, height: 14mm }
    align: left
    vertical_align: middle
    margin: 0
    style:
      font: { family: "Microsoft YaHei UI", size: 36, weight: 700, color: "#C9A84C" }
```

### Page Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| layout | string | Yes | Page layout: "blank" (default, use elements) |
| background | object | No | Background style |
| background.color | string | No | Background color (hex) |
| elements | array | Yes | Element list |

## Element Types

### Text Element

```yaml
- type: text
  content: "Text content"
  position: { x: 20mm, y: 16mm, width: 160mm, height: 14mm }
  align: left
  vertical_align: middle
  margin: 0
  style:
    font: { family: "Microsoft YaHei UI", size: 36, weight: 700, color: "#C9A84C" }
    text_effect:
      shadow: { blur: 8, offset: [0, 2], color: "#000000" }
      stroke: { color: "#FF0000", width: 2.0, dash: "solid" }
      reflection: { opacity: 50, distance: 3, blur: 2, direction: 5400000 }
      bevel: { type: "relaxedInset", width: 3, height: 3 }
      letter_spacing: 1.5
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| content | string | - | Text content (required) |
| position | object | - | Position and size `{x, y, width, height}` |
| align | string | left | Horizontal alignment: left, center, right |
| vertical_align | string | top | Vertical alignment: top, middle, bottom |
| margin | number | 0 | Internal margin (mm) |
| style_ref | string | null | Reference to named style |
| style | object | null | Inline style definition |

**Style Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| font.family | string | null | Font family |
| font.size | number | null | Font size (pt) |
| font.weight | number | null | Font weight (400=regular, 700=bold) |
| font.color | string | null | Text color (hex) |
| text_effect.shadow | object | null | Text shadow |
| text_effect.stroke | object | null | Text outline stroke |
| text_effect.reflection | object | null | Reflection effect |
| text_effect.bevel | object | null | Bevel/emboss effect |
| text_effect.letter_spacing | number | null | Letter spacing (pt) |
| text_effect.word_spacing | number | null | Word spacing (pt) |

### Shape Element

```yaml
- type: shape
  shape_type: rounded_rectangle
  position: { x: 20mm, y: 42mm, width: 68mm, height: 72mm }
  style:
    fill: { color: "#12182B" }
    border: { color: "#1E2642", width: 1 }
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| shape_type | string | - | Shape type (required, see shapes.md) |
| position | object | - | Position and size |
| style | object | null | Shape style |

**Style Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| fill.color | string | null | Fill color (hex) |
| fill_gradient | object | null | Gradient fill |
| fill_opacity | number | null | Fill opacity (0-1) |
| border.color | string | null | Border color |
| border.width | number | null | Border width (pt) |
| shadow | object | null | Shape shadow |

### Image Element

```yaml
- type: image
  source: "path/to/image.png"
  position: { x: 20mm, y: 42mm, width: 100mm, height: 80mm }
  style:
    filter: { type: "grayscale", amount: 0.8 }
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| source | string | - | Image file path or URL (required) |
| position | object | - | Position and size |
| style | object | null | Image style |

**Style Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| filter.type | string | null | Filter type: grayscale, blur, opacity, brightness, contrast |
| filter.amount | number | null | Filter amount (0-1) |

### Chart Element

```yaml
- type: chart
  chart_type: bar
  position: { x: 20mm, y: 42mm, width: 120mm, height: 80mm }
  data_ref: "sales_data"
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| chart_type | string | - | Chart type: bar, line, pie, area, scatter (required) |
| data_ref | string | - | Reference to global data |
| position | object | - | Position and size |

### Table Element

```yaml
- type: table
  position: { x: 20mm, y: 42mm, width: 120mm, height: 80mm }
  data_ref: "table_data"
```

### Group Element

Groups multiple elements for positioning:

```yaml
- type: group
  position: { x: 20mm, y: 42mm, width: 100mm, height: 80mm }
  children:
    - type: shape
      ...
    - type: text
      ...
```

### Path Text Element

```yaml
- type: text
  content: "Curved Text"
  position: { x: 20mm, y: 42mm, width: 100mm, height: 80mm }
  path_text:
    path_type: arc
    radius: 100.0
    bend: 50.0
```

**Path Text Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| path_type | string | "arc" | Path type: arc, arch_up, wave, circle, button, chevron, custom, etc. |
| radius | number | 100.0 | Arc radius (mm) |
| bend | number | 50.0 | Bend amount (0-100) |
| custom_path | string | "" | SVG path data for custom paths |

## Animation Support

```yaml
elements:
  - type: text
    content: "Animated"
    animations:
      - anim_type: entry
        effect: fade
        trigger: on_click
        duration: 0.5
        delay: 0.0
        easing: ease_out
```

**Animation Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| anim_type | string | "entry" | Type: entry, exit, emphasis, motion_path |
| effect | string | "fade" | Effect name |
| trigger | string | "on_click" | Trigger: on_click, with_previous, after_previous |
| duration | number | 0.5 | Duration (seconds) |
| delay | number | 0.0 | Delay (seconds) |
| easing | string | "ease_out" | Easing function |
| repeat | number | 0 | Repeat count (0=once, -1=infinite) |

## Background Layers (Background Board)

```yaml
background:
  color: "#0A0E1A"
  layers:
    - type: image
      source: "bg.png"
      fit: cover
      opacity: 0.3
    - type: gradient
      stops: [{color: "#000000", position: 0}, {color: "#0A0E1A", position: 1}]
      direction: top_to_bottom
```

## Global Data

```yaml
data:
  sales_data:
    - { label: "Q1", value: 120 }
    - { label: "Q2", value: 150 }
```

Referenced via `data_ref` in chart/table elements.

## Style Inheritance

Styles cascade in order:
1. Theme default styles
2. Named style (via `style_ref`)
3. Slide-level styles
4. Element inline styles

All style fields are optional. `null` or omitted fields inherit from parent.

## Rich Text Support

For inline styling within text content:

```yaml
- type: text
  content: |
    <span style="color:#FF0000">Red</span> and <strong>bold</strong>
  style:
    font: { family: "Microsoft YaHei UI", size: 16 }
```

Supported HTML tags: `<span>`, `<strong>`, `<em>`, `<u>`, `<s>`, `<br>`

## Validation Constraints

| Field | Constraint |
|-------|-----------|
| position.x + position.width | <= 254mm |
| position.y + position.height | <= 142.875mm |
| fill_opacity | 0 <= value <= 1 |
| font.size | >= 1pt |
| font.weight | 100-900 |

## Example: Complete Page

```yaml
layout: blank
background:
  color: "#0A0E1A"
elements:
  # Title
  - type: text
    content: "Chapter Title"
    position: { x: 20mm, y: 16mm, width: 160mm, height: 14mm }
    align: left
    vertical_align: middle
    margin: 0
    style:
      font: { family: "Microsoft YaHei UI", size: 36, weight: 700, color: "#C9A84C" }

  # Divider
  - type: shape
    shape_type: rectangle
    position: { x: 20mm, y: 34mm, width: 40mm, height: 0.5mm }
    style: { fill: { color: "#C9A84C" } }

  # Card
  - type: shape
    shape_type: rounded_rectangle
    position: { x: 20mm, y: 42mm, width: 68mm, height: 68mm }
    style:
      fill: { color: "#12182B" }
      border: { color: "#1E2642", width: 1 }

  # Card Title
  - type: text
    content: "Section Title"
    position: { x: 28mm, y: 48mm, width: 52mm, height: 10mm }
    align: center
    vertical_align: middle
    margin: 0
    style:
      font: { family: "Microsoft YaHei UI", size: 16, weight: 700, color: "#E8E4DC" }

  # Card Body
  - type: text
    content: "Description text goes here..."
    position: { x: 28mm, y: 60mm, width: 52mm, height: 40mm }
    align: left
    vertical_align: top
    style:
      font: { family: "Microsoft YaHei UI", size: 13, weight: 400, color: "#E8E4DC" }

  # Page Marker
  - type: text
    content: "01 / 08"
    position: { x: 196mm, y: 128mm, width: 38mm, height: 6mm }
    align: right
    vertical_align: middle
    margin: 0
    style:
      font: { family: "Arial", size: 10, weight: 400, color: "#6B7280" }
```
