# Shape System

## Shape Type Aliases

Office Suite DSL uses human-readable shape type names. These map to DrawingML preset geometry in the PPTX renderer.

### Basic Shapes

| Shape Type | Alias | Description |
|-----------|-------|-------------|
| rectangle | rect | Rectangle |
| rounded_rectangle | roundRect | Rounded rectangle |
| ellipse | oval, circle | Ellipse |
| triangle | - | Triangle |
| diamond | - | Diamond |
| hexagon | - | Hexagon |
| pentagon | - | Pentagon |
| octagon | - | Octagon |
| star_5 | - | 5-point star |
| star_6 | - | 6-point star |
| star_8 | - | 8-point star |

### Connectors and Lines

| Shape Type | Alias | Description |
|-----------|-------|-------------|
| line | straightConnector1 | Straight line |
| connector_l | bentConnector2 | L-shaped connector |
| connector_z | bentConnector3 | Z-shaped connector |
| arc | curvedConnector2 | Simple arc |

### Arrow Shapes

| Shape Type | Description |
|-----------|-------------|
| arrow_right | Right arrow |
| arrow_left | Left arrow |
| arrow_up | Up arrow |
| arrow_down | Down arrow |
| arrow_left_right | Left-right arrow |
| arrow_quad | Quad arrow |

### Callout Shapes

| Shape Type | Description |
|-----------|-------------|
| callout_rect | Rectangular callout |
| callout_round | Rounded callout |
| callout_cloud | Cloud callout |

### Special Shapes

| Shape Type | Description |
|-----------|-------------|
| donut | Donut / ring |
| heart | Heart |
| lightning | Lightning bolt |
| sun | Sun |
| moon | Moon |
| cloud | Cloud |
| frame | Frame |
| bracket_left | Left bracket |
| bracket_right | Right bracket |
| brace_left | Left brace |
| brace_right | Right brace |

### Flowchart Shapes

| Shape Type | Description |
|-----------|-------------|
| flow_process | Process |
| flow_decision | Decision |
| flow_terminal | Terminal |
| flow_data | Data (I/O) |
| flow_document | Document |
| flow_predefined | Predefined process |

### Custom Shapes

For shapes not in the preset list, use `custom` with SVG path data:

```yaml
- type: shape
  shape_type: custom
  position: { x: 20mm, y: 42mm, width: 50mm, height: 30mm }
  extra:
    path: "M0 0 L50 0 L50 30 L0 30 Z"
```

## Shape Adjustments

Some shapes support adjustment parameters via `extra.adjustments`:

```yaml
- type: shape
  shape_type: rounded_rectangle
  position: { x: 20mm, y: 42mm, width: 68mm, height: 72mm }
  extra:
    adjustments: [16667]  # Corner radius in 1/100000 units
```

## Common Shape Configurations

### Card Container

```yaml
- type: shape
  shape_type: rounded_rectangle
  position: { x: 20mm, y: 42mm, width: 68mm, height: 72mm }
  style:
    fill: { color: "#12182B" }
    border: { color: "#1E2642", width: 1 }
```

### Divider Line

```yaml
- type: shape
  shape_type: rectangle
  position: { x: 20mm, y: 34mm, width: 40mm, height: 0.5mm }
  style: { fill: { color: "#C9A84C" } }
```

### Badge (Circle)

```yaml
- type: shape
  shape_type: ellipse
  position: { x: 28mm, y: 71mm, width: 14mm, height: 14mm }
  style:
    fill: { color: "#12182B" }
    border: { color: "#C9A84C", width: 2 }
```

### Timeline Node

```yaml
- type: shape
  shape_type: ellipse
  position: { x: 28mm, y: 71mm, width: 14mm, height: 14mm }
  style:
    fill: { color: "#C9A84C" }
    border: { color: "#C9A84C", width: 1 }
```

## DrawingML Mapping

The Office Suite renderer maps DSL shape types to DrawingML preset names:

| DSL Type | DrawingML Name |
|---------|---------------|
| rectangle | rect |
| rounded_rectangle | roundRect |
| ellipse | ellipse |
| triangle | triangle |
| diamond | diamond |
| hexagon | hexagon |
| pentagon | pentagon |
| octagon | octagon |
| star_5 | star5 |
| arrow_right | rightArrow |
| donut | donut |
| heart | heart |

For shapes not explicitly mapped, the renderer will attempt to use the DSL type name directly as the DrawingML preset name.
