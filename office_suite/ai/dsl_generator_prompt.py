"""AI DSL 生成器 — 高质量 Prompt

用户输入自然语言描述，AI 自动生成符合设计规范的 YAML DSL。

设计系统数据来自 office_suite.design.tokens，不内联硬编码。
模板示例从 office_suite.templates.registry 动态加载。

使用方式：
    from office_suite.ai.dsl_generator_prompt import build_prompt
    prompt = build_prompt(user_input, style="corporate")
    # 将 prompt 发送给 AI，获取 YAML DSL 输出
"""

from ..design.tokens import PALETTE, TYPOGRAPHY, SPACING, GRID, LAYOUTS


# ============================================================
# 设计系统（从 tokens 动态生成）
# ============================================================

def _build_design_system() -> str:
    """从设计令牌生成设计系统文档"""

    # 配色表
    palette_rows = ["| 风格 | 主色 | 辅助色 | 背景 | 文字 |",
                    "|------|------|--------|------|------|"]
    for name, colors in PALETTE.items():
        palette_rows.append(
            f"| {name} | {colors['primary']} | {colors['secondary']} | {colors['bg']} | {colors['text']} |"
        )
    palette_table = "\n".join(palette_rows)

    # 字体表
    font_rows = ["| 角色 | 字号 | 字重 |",
                 "|------|------|------|"]
    for role, spec in TYPOGRAPHY.items():
        font_rows.append(f"| {role} | {spec.size} | {spec.weight} |")
    font_table = "\n".join(font_rows)

    # 布局表
    layout_rows = ["| 布局 | 区域 | x | y | width | height |",
                   "|------|------|---|---|-------|--------|"]
    for layout_name, zones in LAYOUTS.items():
        for zone_name, zone in zones.items():
            layout_rows.append(
                f"| {layout_name} | {zone_name} | {zone.x}mm | {zone.y}mm | {zone.width}mm | {zone.height}mm |"
            )
    layout_table = "\n".join(layout_rows)

    return f"""## 设计系统

### 配色方案

{palette_table}

### 字体规范

{font_table}

### 间距规范

- 页面边距: {SPACING.page_margin_x}mm x {SPACING.page_margin_y}mm
- 元素间距: {SPACING.element_gap}mm
- 段落间距: {SPACING.paragraph_gap}mm
- 内边距: {SPACING.container_padding}mm

### 幻灯片尺寸

{GRID.width}mm x {GRID.height}mm (16:9, {GRID.columns} 列网格)

重要：所有元素的 y + height 必须 <= {GRID.height}mm，x + width 必须 <= {GRID.width}mm。

### 布局区域

{layout_table}
"""


# ============================================================
# 模板示例（从注册表动态加载）
# ============================================================

def _build_template_examples() -> str:
    """从模板注册表加载实际 YAML 内容作为 few-shot 示例"""
    from ..templates.registry import list_templates

    templates = list_templates()
    if not templates:
        return ""

    # 按 category 分组，每类取 1-2 个代表性模板
    by_category: dict[str, list] = {}
    for t in templates:
        by_category.setdefault(t.category, []).append(t)

    sections = []

    # 封面页示例（取 2 个代表性风格）
    cover_examples = []
    for name in ("cover_corporate", "cover_editorial"):
        t = next((t for t in templates if t.name == name), None)
        if t and t.content:
            cover_examples.append(f"### {t.display_name} (`{t.name}`)\n\n```yaml\n{t.content.strip()}\n```")

    if cover_examples:
        sections.append("## 封面页示例\n\n" + "\n\n".join(cover_examples))

    # 内容页示例（从其他内置模板取 1 个）
    content_templates = [t for t in by_category.get("business", []) if not t.name.startswith("cover_")]
    if content_templates:
        t = content_templates[0]
        if t.content:
            sections.append(f"## 内容页示例\n\n### {t.display_name} (`{t.name}`)\n\n```yaml\n{t.content.strip()}\n```")

    return "\n\n".join(sections)


# ============================================================
# 版式模式库（教 AI 理解常见布局模式）
# ============================================================

LAYOUT_PATTERNS = """
## 常用布局模式

以下是经过验证的布局模式，直接复用即可。

### 形状类型速查

可用 shape 值：`rect`, `round_rect`, `ellipse`, `circle`, `triangle`, `diamond`, `pentagon`, `hexagon`, `star_5`, `cross`, `arrow_right`, `arrow_left`

### 数据卡片行

```yaml
# 3 个等宽数据卡片，水平排列
- type: shape
  shape: round_rect
  position: { x: 25mm, y: 32mm, width: 58mm, height: 38mm }
  style:
    fill: { color: "#EFF6FF" }
    border: { color: "#BFDBFE", width: 1 }
- type: text
  content: "95"
  position: { x: 25mm, y: 34mm, width: 58mm, height: 16mm }
  style:
    font: { size: 36, weight: 700, color: "#1E40AF" }
  extra: { align: center }
- type: text
  content: "千卡 / 每颗"
  position: { x: 25mm, y: 50mm, width: 58mm, height: 8mm }
  style:
    font: { size: 12, color: "#64748B" }
  extra: { align: center }
```

### 信息卡片（带编号）

```yaml
# 左侧编号 + 右侧标题和正文的卡片
- type: shape
  shape: round_rect
  position: { x: 25mm, y: 32mm, width: 90mm, height: 50mm }
  style:
    fill: { color: "#FFFFFF" }
    shadow: { blur: 6, offset: [0, 2], color: "#00000010" }
    border: { color: "#E2E8F0", width: 1 }
- type: text
  content: "01"
  position: { x: 30mm, y: 35mm, width: 12mm, height: 8mm }
  style:
    font: { size: 16, weight: 600, color: "#DC2626" }
- type: text
  content: "标题"
  position: { x: 44mm, y: 35mm, width: 50mm, height: 8mm }
  style:
    font: { size: 16, weight: 700, color: "#1E293B" }
- type: text
  content: "正文内容描述..."
  position: { x: 30mm, y: 45mm, width: 80mm, height: 32mm }
  style:
    font: { size: 12, color: "#475569" }
```

### 三栏分类

```yaml
# 三栏等宽布局，每栏有彩色标题条
- type: shape
  shape: round_rect
  position: { x: 25mm, y: 32mm, width: 66mm, height: 100mm }
  style:
    fill: { color: "#F8FAFC" }
    border: { color: "#E2E8F0", width: 1 }
- type: shape
  shape: rect
  position: { x: 25mm, y: 32mm, width: 66mm, height: 7mm }
  style:
    fill: { color: "#1E40AF" }
- type: text
  content: "类别标题"
  position: { x: 25mm, y: 32mm, width: 66mm, height: 7mm }
  style:
    font: { size: 11, weight: 600, color: "#FFFFFF" }
  extra: { align: center }
```

### 时间轴

```yaml
# 横向时间轴：主线 + 节点 + 说明
- type: shape
  shape: rect
  position: { x: 40mm, y: 45mm, width: 180mm, height: 1.5mm }
  style:
    fill: { color: "#BFDBFE" }
- type: shape
  shape: round_rect
  position: { x: 40mm, y: 38mm, width: 10mm, height: 10mm }
  style:
    fill: { color: "#1E40AF" }
- type: text
  content: "阶段名称"
  position: { x: 25mm, y: 52mm, width: 40mm, height: 7mm }
  style:
    font: { size: 14, weight: 700, color: "#1E40AF" }
- type: text
  content: "具体事项说明"
  position: { x: 25mm, y: 60mm, width: 40mm, height: 30mm }
  style:
    font: { size: 11, color: "#334155" }
```

### 背景渐变

```yaml
# 深色渐变背景 + 装饰色块
background_board:
  layers:
    - type: shape
      shape: rect
      position: { x: 0, y: 0, width: 100%, height: 100% }
      style:
        fill: { color: "#0F172A" }
    - type: shape
      shape: rect
      position: { x: 0, y: 0, width: 100%, height: 40% }
      style:
        fill: { gradient: { type: linear, angle: 135, stops: ["#1E40AF", "#3B82F6"] } }
```

### 表格

```yaml
- type: table
  position: { x: 25mm, y: 86mm, width: 200mm, height: 48mm }
  extra:
    columns:
      - { header: "列名", width: 25% }
      - { header: "数值", width: 20% }
    data:
      - ["项目 A", "100"]
      - ["项目 B", "200"]
```

### 结束页

```yaml
# 深色背景 + 居中大字
background_board:
  layers:
    - type: shape
      shape: rect
      position: { x: 0, y: 0, width: 100%, height: 100% }
      style:
        fill: { gradient: { type: linear, angle: 135, stops: ["#0F172A", "#1E293B"] } }
elements:
  - type: text
    content: "谢谢"
    position: { x: 40mm, y: 40mm, width: 180mm, height: 25mm }
    style:
      font: { size: 44, weight: 700, color: "#FFFFFF" }
  - type: text
    content: "联系方式说明"
    position: { x: 40mm, y: 75mm, width: 180mm, height: 10mm }
    style:
      font: { size: 18, color: "#94A3B8" }
```

### 图表（柱状图 + 内联数据）

```yaml
- type: chart
  chart_type: bar
  position: { x: 25mm, y: 40mm, width: 200mm, height: 90mm }
  extra:
    categories: ["Q1", "Q2", "Q3", "Q4"]
    series:
      - name: "营收"
        values: [8000, 9500, 10500, 12000]
      - name: "利润"
        values: [1200, 1800, 2100, 2400]
    title: "季度趋势"
    legend: true
    colors: ["#1E40AF", "#60A5FA"]
```

### 图表（饼图）

```yaml
- type: chart
  chart_type: pie
  position: { x: 50mm, y: 35mm, width: 120mm, height: 95mm }
  extra:
    categories: ["国内", "海外", "其他"]
    series:
      - name: "收入构成"
        values: [40, 55, 5]
    title: "收入构成"
    colors: ["#1E40AF", "#3B82F6", "#93C5FD"]
```

### 动画（入场淡入）

```yaml
- type: text
  content: "标题"
  position: { x: 30mm, y: 40mm, width: 194mm, height: 25mm }
  style:
    font: { size: 36, weight: 700, color: "#0F172A" }
  animation:
    type: entry
    effect: fade
    trigger: on_click
    duration: 0.5
```

### 引用/金句

```yaml
# 居中大字引用 + 来源
- type: text
  content: ""好的设计是尽可能少的设计""
  position: { x: 40mm, y: 35mm, width: 174mm, height: 30mm }
  style:
    font: { size: 28, weight: 400, italic: true, color: "#1E293B" }
  extra: { align: center }
- type: shape
  shape: rect
  position: { x: 115mm, y: 70mm, width: 24mm, height: 1.5mm }
  style:
    fill: { color: "#1E40AF" }
- type: text
  content: "— Dieter Rams"
  position: { x: 40mm, y: 78mm, width: 174mm, height: 8mm }
  style:
    font: { size: 14, color: "#64748B" }
  extra: { align: center }
```

### 双栏对比

```yaml
# 左右两栏对比布局
- type: text
  content: "改造前 vs 改造后"
  position: { x: 25mm, y: 10mm, width: 200mm, height: 14mm }
  style:
    font: { size: 28, weight: 700, color: "#0F172A" }
# 左栏
- type: shape
  shape: round_rect
  position: { x: 25mm, y: 32mm, width: 98mm, height: 100mm }
  style:
    fill: { color: "#FEF2F2" }
    border: { color: "#FECACA", width: 1 }
- type: text
  content: "改造前"
  position: { x: 25mm, y: 35mm, width: 98mm, height: 8mm }
  style:
    font: { size: 16, weight: 700, color: "#DC2626" }
  extra: { align: center }
# 右栏
- type: shape
  shape: round_rect
  position: { x: 131mm, y: 32mm, width: 98mm, height: 100mm }
  style:
    fill: { color: "#F0FDF4" }
    border: { color: "#BBF7D0", width: 1 }
- type: text
  content: "改造后"
  position: { x: 131mm, y: 35mm, width: 98mm, height: 8mm }
  style:
    font: { size: 16, weight: 700, color: "#16A34A" }
  extra: { align: center }
```

### 装饰性几何背景

```yaml
# 深色背景 + 半透明几何装饰
background_board:
  layers:
    - type: shape
      shape: rect
      position: { x: 0, y: 0, width: 100%, height: 100% }
      style:
        fill: { color: "#0F172A" }
    - type: shape
      shape: circle
      position: { x: 160mm, y: -40mm, width: 220mm, height: 220mm }
      style:
        fill: { color: "#FFFFFF", opacity: 0.03 }
    - type: shape
      shape: circle
      position: { x: 190mm, y: 70mm, width: 160mm, height: 160mm }
      style:
        fill: { color: "#FFFFFF", opacity: 0.05 }
    - type: shape
      shape: rect
      position: { x: 30mm, y: 90mm, width: 50mm, height: 1mm }
      style:
        fill: { color: "#3B82F6", opacity: 0.4 }
```

### 图文混排（左图右文）

```yaml
- type: image
  source: "photo.jpg"
  position: { x: 25mm, y: 25mm, width: 100mm, height: 100mm }
  extra:
    fit: cover
    filter:
      type: duotone
      highlight: "#DBEAFE"
      shadow: "#1E40AF"
- type: text
  content: "标题"
  position: { x: 135mm, y: 30mm, width: 94mm, height: 14mm }
  style:
    font: { size: 24, weight: 700, color: "#0F172A" }
- type: text
  content: "正文内容..."
  position: { x: 135mm, y: 48mm, width: 94mm, height: 70mm }
  style:
    font: { size: 14, color: "#334155" }
```

### 发光效果（Glow）

```yaml
# 卡片外发光 — 用于强调重要内容
- type: shape
  shape: round_rect
  position: { x: 40mm, y: 30mm, width: 174mm, height: 50mm }
  style:
    fill: { color: "#FFFFFF" }
    glow: { radius: 8, color: "#3B82F6", opacity: 0.3 }
    border: { color: "#BFDBFE", width: 1 }
- type: text
  content: "重点数据"
  position: { x: 40mm, y: 32mm, width: 174mm, height: 14mm }
  style:
    font: { size: 24, weight: 700, color: "#1E40AF" }
  extra: { align: center }

# 发光参数说明：
#   radius: 发光半径（pt），常用 4-12
#   color: 发光颜色，一般与主色同色系
#   opacity: 发光透明度 0-1，常用 0.2-0.5
```

### 文字变形（WordArt）

```yaml
# 拱形文字 — 适合标题装饰
- type: text
  content: "年度报告"
  position: { x: 40mm, y: 20mm, width: 174mm, height: 30mm }
  style:
    font: { size: 40, weight: 700, color: "#1E40AF" }
    text_effect: { transform: arch, bend: 50 }

# 可用的 transform 类型：
#   arch        — 拱形（向下弯曲）
#   arch_up     — 拱形（向上弯曲）
#   wave        — 波浪
#   circle      — 环形
#   slant_up    — 向上倾斜
#   slant_down  — 向下倾斜
#   triangle    — 三角形
#   chevron_up  — 人字形（上）
#   chevron_down — 人字形（下）
#   button      — 按钮形
#   deflate     — 收缩
#   inflate     — 膨胀
#   fade_up     — 上渐隐
#   fade_down   — 下渐隐
```

### 边框虚线样式

```yaml
# 实线边框 — 正式感
- type: shape
  shape: round_rect
  position: { x: 25mm, y: 30mm, width: 98mm, height: 40mm }
  style:
    fill: { color: "#FFFFFF" }
    border: { color: "#1E40AF", width: 2, dash: solid }

# 虚线边框 — 轻松感/待填充区域
- type: shape
  shape: round_rect
  position: { x: 131mm, y: 30mm, width: 98mm, height: 40mm }
  style:
    fill: { color: "#F8FAFC" }
    border: { color: "#94A3B8", width: 1, dash: dashed }

# 点线边框 — 精致装饰
- type: shape
  shape: round_rect
  position: { x: 25mm, y: 74mm, width: 204mm, height: 40mm }
  style:
    fill: { color: "#FFFBEB" }
    border: { color: "#D97706", width: 1, dash: dotted }
```

### 文本排版控制

```yaml
# 完整的文本排版示例
- type: text
  content: "正文段落内容..."
  position: { x: 30mm, y: 40mm, width: 194mm, height: 80mm }
  style:
    font: { size: 14, color: "#334155", family: "Microsoft YaHei UI" }
  extra:
    align: justify
    vertical_align: top
    margins: { left: 4, right: 4, top: 3, bottom: 3 }
    line_spacing: 1.5
    indent: 8

# extra 文本排版参数：
#   align: left | center | right | justify
#   vertical_align: top | middle | bottom
#   margin: 统一边距（mm）
#   margins: { left, right, top, bottom } 分别设置（mm）
#   line_spacing: 行距倍数（1.0=单倍, 1.5=1.5倍, 2.0=双倍）
#   indent: 首行缩进（mm）
```

### 高级动画

```yaml
# 入场动画组合：标题先淡入，内容后滑入
- type: text
  content: "页面标题"
  position: { x: 30mm, y: 10mm, width: 194mm, height: 20mm }
  style:
    font: { size: 28, weight: 700, color: "#0F172A" }
  animation:
    type: entry
    effect: fade_in
    trigger: on_click
    duration: 0.5
    easing: ease_out

- type: text
  content: "内容要点"
  position: { x: 30mm, y: 35mm, width: 194mm, height: 60mm }
  style:
    font: { size: 14, color: "#334155" }
  animation:
    type: entry
    effect: slide_up
    trigger: after_previous
    delay: 0.3
    duration: 0.6
    easing: ease_in_out

# 入场效果（type: entry）：
#   fade, fade_in, slide_up, slide_down, slide_left, slide_right,
#   zoom_in, zoom_out, fly_in, wipe_up, wipe_down, wipe_left, wipe_right

# 退出效果（type: exit）：
#   fade_out, slide_out_up, slide_out_down

# 强调效果（type: emphasis）：
#   pulse, grow, shrink, spin_emphasis

# 触发器（trigger）：
#   on_click — 点击时播放
#   with_previous — 与上一动画同时
#   after_previous — 上一动画完成后

# 缓动（easing）：
#   linear, ease_in, ease_out, ease_in_out
```

### 图片滤镜组合

```yaml
# 双色调（品牌色覆盖）
- type: image
  source: "photo.jpg"
  position: { x: 25mm, y: 25mm, width: 100mm, height: 100mm }
  extra:
    fit: cover
    filter:
      type: duotone
      highlight: "#DBEAFE"
      shadow: "#1E40AF"

# 灰度（庄重/复古）
- type: image
  source: "photo.jpg"
  position: { x: 25mm, y: 25mm, width: 100mm, height: 100mm }
  extra:
    fit: contain
    filter:
      type: grayscale

# 模糊背景图（文字前景清晰）
- type: image
  source: "bg.jpg"
  position: { x: 0, y: 0, width: 254mm, height: 142.875mm }
  extra:
    fit: cover
    filter:
      type: blur
      radius: 12

# 亮度调节
- type: image
  source: "photo.jpg"
  position: { x: 25mm, y: 25mm, width: 200mm, height: 100mm }
  extra:
    fit: cover
    filter:
      type: brightness
      value: 0.7

# 可用滤镜类型：
#   duotone   — 双色调（需要 highlight + shadow 颜色）
#   grayscale — 灰度
#   biLevel   — 黑白二值化
#   blur      — 模糊（需要 radius 参数）
#   opacity   — 透明度（需要 value 0-1）
#   brightness — 亮度（需要 value，<1 变暗，>1 变亮）
#   contrast  — 对比度（需要 value）
```

### 图表样式定制

```yaml
# 柱状图 + 自定义样式
- type: chart
  chart_type: bar
  position: { x: 25mm, y: 30mm, width: 200mm, height: 90mm }
  extra:
    categories: ["Q1", "Q2", "Q3", "Q4"]
    series:
      - name: "营收"
        values: [8000, 9500, 10500, 12000]
      - name: "利润"
        values: [1200, 1800, 2100, 2400]
    title: "季度趋势"
    legend: true
    colors: ["#1E40AF", "#60A5FA"]
    # 图表样式定制
    title_size: 14
    title_color: "#0F172A"
    label_size: 9
    label_color: "#475569"

# 饼图 + 自定义样式
- type: chart
  chart_type: pie
  position: { x: 50mm, y: 35mm, width: 120mm, height: 95mm }
  extra:
    categories: ["国内", "海外", "其他"]
    series:
      - name: "收入构成"
        values: [40, 55, 5]
    title: "收入构成"
    colors: ["#1E40AF", "#3B82F6", "#93C5FD"]
    title_size: 16
    title_color: "#1E40AF"
    label_size: 11

# 环形图（doughnut）
- type: chart
  chart_type: doughnut
  position: { x: 70mm, y: 30mm, width: 100mm, height: 95mm }
  extra:
    categories: ["直接", "间接", "其他"]
    series:
      - name: "成本构成"
        values: [55, 30, 15]
    title: "成本构成"
    colors: ["#DC2626", "#F59E0B", "#94A3B8"]

# 可用 chart_type：bar, line, pie, doughnut, area, scatter
# 示例：chart_type: area   chart_type: scatter
# 样式参数：
#   title_size: 标题字号（默认 14）
#   title_color: 标题颜色（默认 #0F172A）
#   label_size: 标签字号（默认 9）
#   label_color: 标签颜色（默认 #475569）
```

### 数据驱动（data_ref）

```yaml
# 在文档级别定义数据，多个图表/表格引用
data:
  revenue:
    - ["Q1", 8000]
    - ["Q2", 9500]
    - ["Q3", 10500]
    - ["Q4", 12000]

slides:
  - layout: blank
    elements:
      - type: table
        data_ref: revenue
        position: { x: 25mm, y: 30mm, width: 200mm, height: 50mm }
        extra:
          columns:
            - { header: "季度", width: 30% }
            - { header: "营收（万）", width: 70% }
```

### 拼图布局 A（2x3 网格，左列合并）

```yaml
# 布局示意：
# ┌──────────┬──────────┐
# │          │  A  │  B  │
# │  大卡片  ├─────┼─────┤
# │          │  C  │  D  │
# └──────────┴─────┴─────┘
# 间距 4mm，边距 25mm
# 列: 25+100+4+63+4+63 = 259 → 调整: 25+98+4+60.5+4+60.5 = 252

# 大卡片（左侧合并 2 行）
- type: shape
  shape: round_rect
  position: { x: 25mm, y: 25mm, width: 98mm, height: 108mm }
  style:
    fill: { color: "#EFF6FF" }
    border: { color: "#BFDBFE", width: 1 }
- type: text
  content: "核心指标"
  position: { x: 30mm, y: 30mm, width: 88mm, height: 10mm }
  style:
    font: { size: 18, weight: 700, color: "#1E40AF" }
- type: text
  content: "详细说明..."
  position: { x: 30mm, y: 42mm, width: 88mm, height: 85mm }
  style:
    font: { size: 13, color: "#334155" }

# 右上 A
- type: shape
  shape: round_rect
  position: { x: 127mm, y: 25mm, width: 60.5mm, height: 52mm }
  style:
    fill: { color: "#F0FDF4" }
    border: { color: "#BBF7D0", width: 1 }
- type: text
  content: "指标 A"
  position: { x: 131mm, y: 29mm, width: 52mm, height: 8mm }
  style:
    font: { size: 14, weight: 600, color: "#16A34A" }
- type: text
  content: "1,280"
  position: { x: 131mm, y: 40mm, width: 52mm, height: 14mm }
  style:
    font: { size: 28, weight: 700, color: "#15803D" }

# 右上 B
- type: shape
  shape: round_rect
  position: { x: 191.5mm, y: 25mm, width: 60.5mm, height: 52mm }
  style:
    fill: { color: "#FEF2F2" }
    border: { color: "#FECACA", width: 1 }
- type: text
  content: "指标 B"
  position: { x: 195.5mm, y: 29mm, width: 52mm, height: 8mm }
  style:
    font: { size: 14, weight: 600, color: "#DC2626" }
- type: text
  content: "86%"
  position: { x: 195.5mm, y: 40mm, width: 52mm, height: 14mm }
  style:
    font: { size: 28, weight: 700, color: "#B91C1C" }

# 右下 C
- type: shape
  shape: round_rect
  position: { x: 127mm, y: 81mm, width: 60.5mm, height: 52mm }
  style:
    fill: { color: "#FFF7ED" }
    border: { color: "#FED7AA", width: 1 }
- type: text
  content: "指标 C"
  position: { x: 131mm, y: 85mm, width: 52mm, height: 8mm }
  style:
    font: { size: 14, weight: 600, color: "#EA580C" }

# 右下 D
- type: shape
  shape: round_rect
  position: { x: 191.5mm, y: 81mm, width: 60.5mm, height: 52mm }
  style:
    fill: { color: "#FAF5FF" }
    border: { color: "#E9D5FF", width: 1 }
- type: text
  content: "指标 D"
  position: { x: 195.5mm, y: 85mm, width: 52mm, height: 8mm }
  style:
    font: { size: 14, weight: 600, color: "#7C3AED" }
```

### 拼图布局 B（不等宽三栏）

```yaml
# 布局示意：
# ┌────────┬────────────┬────────┐
# │  窄栏  │   宽主栏   │  窄栏  │
# │  50mm  │   104mm    │  50mm  │
# └────────┴────────────┴────────┘

# 左栏
- type: shape
  shape: round_rect
  position: { x: 25mm, y: 25mm, width: 50mm, height: 108mm }
  style:
    fill: { color: "#1E40AF" }
- type: text
  content: "导航"
  position: { x: 25mm, y: 30mm, width: 50mm, height: 8mm }
  style:
    font: { size: 14, weight: 600, color: "#FFFFFF" }
  extra: { align: center }

# 中间主栏
- type: shape
  shape: round_rect
  position: { x: 79mm, y: 25mm, width: 104mm, height: 108mm }
  style:
    fill: { color: "#FFFFFF" }
    shadow: { blur: 8, offset: [0, 2], color: "#00000010" }
    border: { color: "#E2E8F0", width: 1 }
- type: text
  content: "主要内容"
  position: { x: 85mm, y: 30mm, width: 92mm, height: 8mm }
  style:
    font: { size: 18, weight: 700, color: "#0F172A" }

# 右栏
- type: shape
  shape: round_rect
  position: { x: 187mm, y: 25mm, width: 42mm, height: 108mm }
  style:
    fill: { color: "#F8FAFC" }
    border: { color: "#E2E8F0", width: 1 }
- type: text
  content: "侧栏"
  position: { x: 187mm, y: 30mm, width: 42mm, height: 8mm }
  style:
    font: { size: 12, weight: 600, color: "#64748B" }
  extra: { align: center }
```

### 拼图布局 C（瀑布流/多图拼接）

```yaml
# 布局示意：
# ┌────────┬────────┬────────┐
# │  图1   │  图2   │  图3   │  高 45mm
# │ 大图   │        │        │
# ├────────┼────────┴────────┤
# │  图4   │     图5         │  高 55mm
# │        │     大图        │
# └────────┴─────────────────┘
# 间距 3mm

- type: shape
  shape: rect
  position: { x: 25mm, y: 20mm, width: 66mm, height: 45mm }
  style:
    fill: { color: "#DBEAFE" }
- type: shape
  shape: rect
  position: { x: 94mm, y: 20mm, width: 66mm, height: 45mm }
  style:
    fill: { color: "#BFDBFE" }
- type: shape
  shape: rect
  position: { x: 163mm, y: 20mm, width: 66mm, height: 45mm }
  style:
    fill: { color: "#93C5FD" }
- type: shape
  shape: rect
  position: { x: 25mm, y: 68mm, width: 66mm, height: 55mm }
  style:
    fill: { color: "#60A5FA" }
- type: shape
  shape: rect
  position: { x: 94mm, y: 68mm, width: 135mm, height: 55mm }
  style:
    fill: { color: "#3B82F6" }
```

### 拼图布局 D（仪表盘：图表 + 指标卡混合）

```yaml
# 布局示意：
# ┌─────────────────────────┬────────┐
# │        图表区域          │ 指标1  │
# │        140mm x 60mm     │ 60mm   │
# ├─────────────────────────┼────────┤
# │  指标2  │  指标3 │ 指标4 │ 指标5  │
# └─────────┴────────┴──────┴────────┘

# 图表
- type: chart
  chart_type: bar
  position: { x: 25mm, y: 20mm, width: 139mm, height: 60mm }
  extra:
    categories: ["Q1", "Q2", "Q3", "Q4"]
    series:
      - name: "营收"
        values: [80, 95, 105, 120]
    colors: ["#1E40AF"]

# 右侧指标卡 1
- type: shape
  shape: round_rect
  position: { x: 168mm, y: 20mm, width: 61mm, height: 60mm }
  style:
    fill: { color: "#EFF6FF" }
    border: { color: "#BFDBFE", width: 1 }
- type: text
  content: "120"
  position: { x: 168mm, y: 28mm, width: 61mm, height: 16mm }
  style:
    font: { size: 32, weight: 700, color: "#1E40AF" }
  extra: { align: center }
- type: text
  content: "当季营收（万）"
  position: { x: 168mm, y: 46mm, width: 61mm, height: 7mm }
  style:
    font: { size: 10, color: "#64748B" }
  extra: { align: center }

# 底部指标卡 2-4
- type: shape
  shape: round_rect
  position: { x: 25mm, y: 84mm, width: 44mm, height: 44mm }
  style:
    fill: { color: "#F0FDF4" }
    border: { color: "#BBF7D0", width: 1 }
- type: text
  content: "+23%"
  position: { x: 25mm, y: 92mm, width: 44mm, height: 12mm }
  style:
    font: { size: 22, weight: 700, color: "#16A34A" }
  extra: { align: center }
- type: text
  content: "增长率"
  position: { x: 25mm, y: 106mm, width: 44mm, height: 6mm }
  style:
    font: { size: 10, color: "#64748B" }
  extra: { align: center }

- type: shape
  shape: round_rect
  position: { x: 73mm, y: 84mm, width: 44mm, height: 44mm }
  style:
    fill: { color: "#FFF7ED" }
    border: { color: "#FED7AA", width: 1 }
- type: text
  content: "92%"
  position: { x: 73mm, y: 92mm, width: 44mm, height: 12mm }
  style:
    font: { size: 22, weight: 700, color: "#EA580C" }
  extra: { align: center }
- type: text
  content: "留存率"
  position: { x: 73mm, y: 106mm, width: 44mm, height: 6mm }
  style:
    font: { size: 10, color: "#64748B" }
  extra: { align: center }

- type: shape
  shape: round_rect
  position: { x: 121mm, y: 84mm, width: 44mm, height: 44mm }
  style:
    fill: { color: "#FAF5FF" }
    border: { color: "#E9D5FF", width: 1 }
- type: text
  content: "35%"
  position: { x: 121mm, y: 92mm, width: 44mm, height: 12mm }
  style:
    font: { size: 22, weight: 700, color: "#7C3AED" }
  extra: { align: center }
- type: text
  content: "新客户"
  position: { x: 121mm, y: 106mm, width: 44mm, height: 6mm }
  style:
    font: { size: 10, color: "#64748B" }
  extra: { align: center }

# 底部右侧指标卡 5
- type: shape
  shape: round_rect
  position: { x: 169mm, y: 84mm, width: 60mm, height: 44mm }
  style:
    fill: { color: "#FEF2F2" }
    border: { color: "#FECACA", width: 1 }
- type: text
  content: "18%"
  position: { x: 169mm, y: 92mm, width: 60mm, height: 12mm }
  style:
    font: { size: 22, weight: 700, color: "#DC2626" }
  extra: { align: center }
- type: text
  content: "利润率"
  position: { x: 169mm, y: 106mm, width: 60mm, height: 6mm }
  style:
    font: { size: 10, color: "#64748B" }
  extra: { align: center }
```
"""


# ============================================================
# 组合引擎（教 AI 自由组合基元）
# ============================================================

COMBINATORIAL_ENGINE = """
## 样式组合规则

不要局限于上面的示例。通过以下基元的自由组合，可以生成无限种样式。

### 配色组合矩阵

同一布局 + 不同配色 = 完全不同的视觉效果：

| 风格 | 背景 | 标题色 | 正文色 | 强调色 | 适用场景 |
|------|------|--------|--------|--------|---------|
| 商务蓝 | #FFFFFF | #0F172A | #334155 | #1E40AF | 正式汇报 |
| 深色科技 | #0B0F19 | #FFFFFF | #94A3B8 | #8B5CF6 | 技术发布 |
| 清新绿 | #F0FDF4 | #064E3B | #334155 | #059669 | 环保健康 |
| 暖橙 | #FFFBEB | #1C1917 | #44403C | #D97706 | 活力营销 |
| 优雅金 | #064E3B | #FFFFFF | #A7F3D0 | #D4AF37 | 高端品牌 |
| 中国红 | #7F1D1D | #FEE2E2 | #FCA5A5 | #DC2626 | 传统文化 |
| 极简灰 | #FFFFFF | #111827 | #6B7280 | #374151 | 学术技术 |
| 撞色粉 | #18181B | #FFFFFF | #A1A1AA | #E11D48 | 创意潮流 |

### 字号层次公式

标题与正文的字号比决定视觉冲击力：

| 层次 | 比例 | 标题 | 副标题 | 正文 | 注释 | 效果 |
|------|------|------|--------|------|------|------|
| 强对比 | 3:1 | 44 | 20 | 14 | 10 | 冲击力强 |
| 中对比 | 2:1 | 36 | 18 | 16 | 12 | 平衡舒适 |
| 弱对比 | 1.5:1 | 28 | 20 | 18 | 14 | 内敛克制 |

### 阴影层次搭配

| 元素类型 | 阴影 | 参数 |
|----------|------|------|
| 页面背景 | 无 | — |
| 大卡片 | lg | blur:8, offset:[0,4] |
| 小卡片 | card | blur:6, offset:[0,2] |
| 悬浮按钮 | elevated | blur:12, offset:[0,6] |
| 内嵌元素 | sm | blur:2, offset:[0,1] |

### 圆角搭配

| 风格 | 卡片圆角 | 按钮圆角 | 分隔线 |
|------|---------|---------|--------|
| 商务 | 2mm (md) | 1mm (sm) | 直线 |
| 科技 | 4mm (lg) | 4mm (lg) | 渐变线 |
| 柔和 | 8mm (xl) | 8mm (xl) | 虚线 |
| 极简 | 0mm (none) | 0mm | 细实线 |

### 背景层次叠加

背景由多层叠加构成，每层独立控制：

```yaml
background_board:
  layers:
    # 第 1 层：底色
    - type: shape
      shape: rect
      position: { x: 0, y: 0, width: 100%, height: 100% }
      style:
        fill: { color: "#0F172A" }
    # 第 2 层：半透明渐变（制造层次感）
    - type: shape
      shape: rect
      position: { x: 0, y: 0, width: 100%, height: 40% }
      style:
        fill: { gradient: { type: linear, angle: 135, stops: ["#1E40AF", "#3B82F6"] }, opacity: 0.8 }
    # 第 3 层：装饰几何（圆形/线条）
    - type: shape
      shape: circle
      position: { x: 160mm, y: -30mm, width: 180mm, height: 180mm }
      style:
        fill: { color: "#FFFFFF", opacity: 0.03 }
    # 第 4 层：细节点缀
    - type: shape
      shape: rect
      position: { x: 30mm, y: 90mm, width: 40mm, height: 1mm }
      style:
        fill: { color: "#60A5FA", opacity: 0.5 }
```

### 卡片变体矩阵

同一张卡片，通过改变填充/边框/阴影，产生不同质感：

| 变体 | 填充 | 边框 | 阴影 | 效果 |
|------|------|------|------|------|
| 浅色实底 | #F8FAFC | #E2E8F0, 1px | 无 | 干净简洁 |
| 纯白悬浮 | #FFFFFF | 无 | blur:8, [0,4] | 浮动感 |
| 透明玻璃 | #FFFFFF, opacity:0.6 | #FFFFFF, 1px | blur:12, [0,4] | 毛玻璃 |
| 深色卡片 | #1E293B | #334155, 1px | 无 | 沉稳内敛 |
| 彩色底 | #EFF6FF | #BFDBFE, 1px | 无 | 活泼轻快 |
| 渐变底 | gradient:135deg | 无 | blur:6, [0,2] | 高级感 |

### 发光效果搭配

| 场景 | 发光色 | 半径 | 透明度 | 效果 |
|------|--------|------|--------|------|
| 强调主卡片 | 与主色同系 | 8 | 0.3 | 吸引视线 |
| 按钮/CTA | 对比色 | 6 | 0.4 | 突出交互 |
| 深色背景装饰 | 亮色 | 12 | 0.2 | 氛围光晕 |
| 禁用/次要 | 灰色 | 4 | 0.15 | 柔和提示 |

### 文字变形搭配

| 场景 | 变形类型 | bend | 效果 |
|------|---------|------|------|
| 封面大标题 | arch | 50 | 拱形庄重 |
| 活动海报 | wave | 40 | 波浪动感 |
| 品牌标志 | circle | 60 | 环形聚焦 |
| 科技演示 | slant_up | 30 | 倾斜前进感 |
| 创意封面 | inflate | 50 | 膨胀立体感 |
| 简约装饰 | deflate | 40 | 收缩精致感 |

### 边框风格搭配

| 风格 | dash | width | 适用场景 |
|------|------|-------|---------|
| 正式商务 | solid | 1-2 | 正文卡片 |
| 待填充区域 | dashed | 1 | 占位提示 |
| 精致装饰 | dotted | 1 | 装饰分隔 |
| 强调边框 | solid | 3 | 重要卡片 |
| 虚线分隔 | dashed | 0.5 | 区域划分 |

### 动画节奏搭配

| 场景 | 入场 | 触发 | 时长 | 缓动 | 效果 |
|------|------|------|------|------|------|
| 标题登场 | fade_in | on_click | 0.5s | ease_out | 沉稳大气 |
| 逐步揭示 | slide_up | after_previous | 0.4s | ease_in_out | 引导视线 |
| 数据强调 | zoom_in | with_previous | 0.3s | ease_out | 突出重点 |
| 平滑过渡 | wipe_right | after_previous | 0.6s | linear | 自然流畅 |
| 退出转场 | fade_out | on_click | 0.3s | ease_in | 干净退出 |

### 图片滤镜搭配

| 场景 | 滤镜 | 参数 | 效果 |
|------|------|------|------|
| 品牌色覆盖 | duotone | 主色+辅色 | 统一视觉 |
| 庄重/黑白 | grayscale | — | 经典质感 |
| 背景模糊 | blur | radius:12 | 突出前景文字 |
| 暗角效果 | brightness | value:0.6 | 聚焦中心 |
| 高对比度 | contrast | value:1.5 | 视觉冲击 |
| 半透明叠加 | opacity | value:0.3 | 水印效果 |

### 图表风格搭配

| 场景 | chart_type | colors | title_size | 效果 |
|------|-----------|--------|------------|------|
| 正式汇报 | bar | 蓝色系 | 14 | 专业稳重 |
| 趋势分析 | line | 渐变蓝 | 12 | 简洁清晰 |
| 占比展示 | pie | 3色对比 | 16 | 直观醒目 |
| 环形占比 | doughnut | 暖色系 | 14 | 时尚现代 |
| 面积趋势 | area | 半透明蓝 | 12 | 层次丰富 |

### 组合示例：同一内容 × 不同风格

只需替换配色和阴影，布局完全复用：

```yaml
# 风格 A：商务蓝（正式汇报）
style:
  font: { size: 36, weight: 700, color: "#0F172A" }
  fill: { color: "#FFFFFF" }
  shadow: { blur: 4, offset: [0, 2], color: "#00000008" }

# 风格 B：深色科技（技术发布）
style:
  font: { size: 36, weight: 700, color: "#FFFFFF" }
  fill: { color: "#111827" }
  shadow: { blur: 8, offset: [0, 4], color: "#8B5CF620" }
  glow: { radius: 10, color: "#8B5CF6", opacity: 0.2 }

# 风格 C：中国红（传统文化）
style:
  font: { size: 36, weight: 700, color: "#FEE2E2" }
  fill: { color: "#7F1D1D" }
  shadow: { blur: 6, offset: [0, 2], color: "#DC262630" }

# 风格 D：极简灰（学术技术）
style:
  font: { size: 36, weight: 400, color: "#111827" }
  fill: { color: "#FFFFFF" }
  border: { color: "#E5E7EB", width: 1, dash: solid }
```
"""


# ============================================================
# 设计原则
# ============================================================

DESIGN_PRINCIPLES = """
## 设计原则

### 1. 对齐 (Alignment)
- 所有元素必须沿网格线对齐
- 标题左对齐，内容保持一致的左边距
- 数字和文字基线对齐
- 卡片之间的间距保持一致（常用 4mm）

### 2. 对比 (Contrast)
- 标题与正文字号比 >= 2:1
- 重要内容使用主色或加粗
- 背景与文字对比度 >= 4.5:1
- 使用阴影/发光制造层次对比

### 3. 重复 (Repetition)
- 同类元素使用相同样式
- 颜色、字体、间距保持一致
- 每页最多 3 种颜色
- 全篇动画风格统一（要么全淡入，要么全滑入）

### 4. 亲密性 (Proximity)
- 相关内容靠近放置
- 不相关内容保持距离
- 标题与内容之间距离 < 标题与上一元素之间距离

### 5. 留白 (White Space)
- 页面内容占比 <= 70%
- 每页核心信息点 <= 3 个
- 避免文字密集堆砌
- 卡片内部保持充足内边距（>= 3mm）

### 6. 视觉层次 (Visual Hierarchy)
- 主标题 > 副标题 > 正文 > 注释
- 使用大小、颜色、粗细建立层次
- 引导视线从左上到右下流动
- 使用 glow/shadow 将注意力引导到重要内容

### 7. 效果克制 (Effect Restraint)
- 每页最多 1-2 种效果类型（如 shadow + gradient，或 glow + animation）
- 不要给所有元素都加发光效果，只用于强调
- 动画不要过度使用，每页 2-4 个动画元素足够
- 深色背景用浅色发光，浅色背景用深色阴影

### 8. 色彩和谐 (Color Harmony)
- 同一页面的颜色饱和度保持一致
- 渐变色使用相邻色或同色系
- 强调色只用于关键信息，面积 <= 10%
- 背景色与内容色保持足够对比
"""


# ============================================================
# 输出规范
# ============================================================

OUTPUT_SPEC = """
## 输出规范

### YAML DSL 格式

```yaml
version: "4.0"
type: presentation
style_preset: corporate

# 全局数据（可选，供 data_ref 引用）
data:
  key_name:
    - ["列1", "列2", "列3"]
    - ["值1", "值2", "值3"]

slides:
  - layout: blank
    background_board:
      layers:
        - type: shape
          shape: rect
          position: { x: 0, y: 0, width: 100%, height: 100% }
          style:
            fill: { color: "#1E40AF" }
    elements:
      - type: text
        content: "标题"
        position: { x: 30mm, y: 40mm, width: 194mm, height: 25mm }
        style:
          font: { size: 44, weight: 700, color: "#FFFFFF" }
```

### 元素类型

| 类型 | 必需字段 | 可选字段 |
|------|---------|---------|
| text | content, position | style, extra, animation |
| shape | position | shape, style, extra, animation |
| image | source, position | extra.fit, extra.filter |
| table | position | extra.columns, extra.data, data_ref |
| chart | chart_type, position | extra, data_ref |

### 位置格式

```yaml
position: { x: 30mm, y: 40mm, width: 194mm, height: 25mm }
```

所有尺寸用 mm。x + width <= 254mm，y + height <= 142.875mm。

### 样式格式（完整）

```yaml
style:
  font:
    size: 18
    weight: 400        # 100-900，常用 400/600/700
    color: "#334155"
    family: "Microsoft YaHei UI"
    italic: false
  fill:
    color: "#FFFFFF"
    opacity: 0.9
    gradient:          # 渐变填充（与 color 二选一）
      type: linear     # linear | radial
      angle: 135       # linear 时的角度 0-360
      stops: ["#1E40AF", "#3B82F6"]
  shadow:
    blur: 4            # 模糊半径 pt
    offset: [0, 2]     # [x, y] 偏移 pt
    color: "#00000010" # 阴影颜色（含透明度）
    opacity: 0.5       # 阴影透明度 0-1
    angle: 45          # 阴影角度
  border:
    color: "#E2E8F0"
    width: 1           # 边框宽度 pt
    dash: solid        # solid | dashed | dotted
  glow:                # 发光效果
    radius: 6          # 发光半径 pt
    color: "#3B82F6"   # 发光颜色
    opacity: 0.35      # 发光透明度 0-1
  text_effect:         # 文字变形（WordArt）
    transform: arch    # 变形类型（见文字变形章节）
    bend: 50           # 弯曲程度
```

### extra 格式

```yaml
extra:
  # 文本排版
  align: center                    # left | center | right | justify
  vertical_align: middle           # top | middle | bottom
  margin: 3                       # 统一边距 mm
  margins: { left: 4, right: 4, top: 3, bottom: 3 }
  line_spacing: 1.5               # 行距倍数
  indent: 8                       # 首行缩进 mm

  # 图片
  fit: cover                       # cover | contain | stretch
  filter:
    type: duotone                  # duotone | grayscale | biLevel | blur | opacity | brightness | contrast
    highlight: "#FFFFFF"           # duotone 专用
    shadow: "#1E293B"              # duotone 专用
    radius: 12                     # blur 专用
    value: 0.7                     # opacity/brightness/contrast 专用

  # 表格
  columns:
    - { header: "列名", width: 25% }
  data:
    - ["值1", "值2"]

  # 图表
  categories: ["Q1", "Q2", "Q3", "Q4"]
  series:
    - name: "系列名"
      values: [80, 95, 105, 120]
  title: "图表标题"
  legend: true
  colors: ["#1E40AF", "#60A5FA"]
  title_size: 14
  title_color: "#0F172A"
  label_size: 9
  label_color: "#475569"
```

### 动画格式

```yaml
animation:
  type: entry        # entry | exit | emphasis
  effect: fade_in    # 效果名（见动画章节）
  trigger: on_click  # on_click | with_previous | after_previous
  delay: 0.3         # 延迟秒数
  duration: 0.5      # 持续秒数
  easing: ease_out   # linear | ease_in | ease_out | ease_in_out
```

### 数据引用

```yaml
# 在文档顶层定义 data，元素通过 data_ref 引用
data:
  sales:
    - ["Q1", 8000]
    - ["Q2", 9500]

# 元素中引用
- type: table
  data_ref: sales
  position: { x: 25mm, y: 30mm, width: 200mm, height: 50mm }
  extra:
    columns:
      - { header: "季度", width: 30% }
      - { header: "营收", width: 70% }
```
"""


# ============================================================
# 生成规则
# ============================================================

GENERATION_RULES = """
## 生成规则

1. **封面页**：使用 background_board + 大标题 + 副标题 + 有主题意义的视觉构图；不要套用固定居中模板
2. **内容页**：每页 <= 3 个核心信息点，先根据主题选择自定义构图；卡片/表格/图表只是可选容器，不是默认布局
3. **结束页**：做成海报式收束或主题视觉回响；不要默认深色渐变 + 居中文字 + 装饰几何
4. **风格一致**：全篇使用同一 style_preset，颜色、字体保持一致
5. **边界约束**：所有元素 y + height <= 142.875mm，x + width <= 254mm
6. **留白充足**：页面内容占比 <= 70%，避免拥挤
7. **视觉层次**：用比例、裁切、留白、对比、注释线、数据尺度建立层次；glow/shadow/gradient 只能辅助，不能代替设计
8. **动画节奏**：标题淡入 → 内容滑入 → 数据缩放，引导观众注意力
9. **图文配合**：图片必须服务信息或氛围；背景图片可使用 overlay/opacity/blur 保证文字可读，避免纯黑遮挡层
10. **直接输出**：输出完整 YAML，不要省略，不要解释
11. **反模板**：6 页以上 PPT 至少使用 5 种不同构图；不要连续复用“标题 + 分割线 + 等宽卡片”的骨架；除非内容是目录/清单，否则全 deck 不超过 2 页卡片网格

## 视觉层次清单

每页幻灯片应包含以下至少 3 个层次：

| 层次 | 元素 | 效果 |
|------|------|------|
| 背景层 | background_board (渐变/纯色/几何) | 氛围 |
| 结构层 | 页边距、书脊、路径、轴线、注释线、图像裁切 | 组织视线 |
| 内容层 | 标题、关键句、图表、卡片、注释、图片、图解 | 信息 |
| 强调层 | 大数字、尺度对比、强裁切、留白、加粗标题 | 焦点 |
| 动画层 | 入场/退出效果 | 节奏 |

## 输出要求

1. 输出完整的 YAML DSL 代码，用 ```yaml ... ``` 包裹
2. 所有尺寸使用 mm 单位
3. 颜色使用 HEX 格式
4. 确保 YAML 语法正确，可直接解析
5. 每页至少有 1 个语义视觉钩子（图像裁切、注释图解、时间线、数据海报、对比轴、引用海报、流程场、主题图标等）
6. 封面和结束页必须使用 background_board
"""


# ============================================================
# Prompt 模板
# ============================================================

USER_PROMPT_TEMPLATE = """
## 用户输入

**风格偏好**：{style}

**内容描述**：
{content}

请根据以上内容，生成完整的 PPT YAML DSL 代码。
"""


# ============================================================
# 构建 Prompt
# ============================================================

def build_prompt(
    content: str,
    style: str = "corporate",
    include_design_system: bool = True,
) -> str:
    """构建完整的 AI 生成 Prompt

    Args:
        content: 用户输入的内容描述
        style: 风格偏好 (corporate/editorial/creative/minimal/tech/elegant/flat/chinese/warm)
        include_design_system: 是否包含设计系统（首次使用时需要）

    Returns:
        完整的 prompt 字符串
    """
    parts = ["你是一个专业的 PPT 设计专家，擅长将商业内容转化为高质量的演示文稿。"]
    parts.append("你的任务是根据用户输入的内容，生成符合设计规范的 YAML DSL 代码。")

    if include_design_system:
        parts.append(_build_design_system())
        parts.append(_build_template_examples())
        parts.append(LAYOUT_PATTERNS)
        parts.append(COMBINATORIAL_ENGINE)
        parts.append(DESIGN_PRINCIPLES)
        parts.append(OUTPUT_SPEC)

    parts.append(GENERATION_RULES)

    user = USER_PROMPT_TEMPLATE.format(style=style, content=content)
    parts.append(user)

    return "\n\n".join(parts)


def build_messages(
    content: str,
    style: str = "corporate",
    include_design_system: bool = True,
) -> list[dict[str, str]]:
    """构建消息列表（适用于 OpenAI / Claude API）

    Args:
        content: 用户输入的内容描述
        style: 风格偏好
        include_design_system: 是否包含设计系统

    Returns:
        消息列表 [{"role": "system", "content": ...}, {"role": "user", "content": ...}]
    """
    system_parts = ["你是一个专业的 PPT 设计专家，擅长将商业内容转化为高质量的演示文稿。"]
    system_parts.append("你的任务是根据用户输入的内容，生成符合设计规范的 YAML DSL 代码。")

    if include_design_system:
        system_parts.append(_build_design_system())
        system_parts.append(_build_template_examples())
        system_parts.append(LAYOUT_PATTERNS)
        system_parts.append(COMBINATORIAL_ENGINE)
        system_parts.append(DESIGN_PRINCIPLES)
        system_parts.append(OUTPUT_SPEC)

    system_parts.append(GENERATION_RULES)

    user = USER_PROMPT_TEMPLATE.format(style=style, content=content)

    return [
        {"role": "system", "content": "\n\n".join(system_parts)},
        {"role": "user", "content": user},
    ]


# ============================================================
# 快捷函数
# ============================================================

def generate_ppt_prompt(
    title: str,
    points: list[str],
    style: str = "corporate",
    has_chart: bool = False,
    chart_data: str = "",
) -> str:
    """快速生成 PPT Prompt

    Args:
        title: PPT 主题
        points: 要点列表
        style: 风格
        has_chart: 是否包含图表
        chart_data: 图表数据描述

    Returns:
        prompt 字符串
    """
    content_lines = [f"**主题**：{title}", "", "**要点**："]
    for i, point in enumerate(points, 1):
        content_lines.append(f"{i}. {point}")

    if has_chart and chart_data:
        content_lines.extend(["", "**数据**：", chart_data])

    content = "\n".join(content_lines)
    return build_prompt(content, style)


# ============================================================
# 示例
# ============================================================

EXAMPLES = {
    "quarterly_report": {
        "input": """
主题：2026 Q2 季度经营报告
风格：专业商务
要点：
- 总营收 1.2 亿元，同比增长 23%
- 海外市场贡献 60%，成为主要增长引擎
- 利润率提升至 18%，成本控制效果显著
- 新客户增长 35%，客户留存率 92%

数据：
- 季度营收趋势：Q1 8000万, Q2 9500万, Q3 1.05亿, Q4 1.2亿
- 收入构成：国内 40%, 海外 60%
""",
        "style": "corporate",
    },
    "product_launch": {
        "input": """
主题：新一代智能手表发布
风格：创意科技
要点：
- 全新设计语言，更轻薄更时尚
- 健康监测全面升级，新增血氧、睡眠分析
- 续航提升 50%，支持 7 天超长待机
- 首发价 1999 元，性价比王者

数据：
- 与竞品对比：续航 7天 vs 竞品 3天, 重量 36g vs 竞品 48g
""",
        "style": "creative",
    },
    "tech_sharing": {
        "input": """
主题：微服务架构设计实践
风格：极简技术
要点：
- 单体架构的痛点：部署慢、扩展难、技术栈锁定
- 微服务拆分原则：单一职责、自治、松耦合
- 服务治理：注册发现、负载均衡、熔断降级
- 实战案例：电商系统拆分 20+ 服务，部署频率提升 10 倍
""",
        "style": "minimal",
    },
}


if __name__ == "__main__":
    example = EXAMPLES["quarterly_report"]
    prompt = build_prompt(example["input"], example["style"])
    print(prompt[:3000])
    print("...")
    print(f"\n总长度: {len(prompt)} 字符")
