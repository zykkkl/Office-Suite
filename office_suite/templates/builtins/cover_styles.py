"""封面页风格模板 — 基于主流 PPT 设计趋势

参考来源：1ppt.com、优品PPT、SlidesCarnival、Slidesgo

提供 8 种视觉风格的封面页：
  - corporate: 商务蓝，渐变 + 几何装饰
  - editorial: 深色大气，色块 + 白字
  - creative: 创意撞色，左侧色条 + 大标题
  - minimal: 极简留白，白色 + 细节点缀
  - tech: 科技感，深色 + 渐变光效
  - elegant: 优雅质感，深绿/酒红 + 金色点缀
  - flat: 扁平清新，明亮色块 + 圆角
  - chinese: 中国风，传统配色 + 纹样装饰
"""

from ..registry import TemplateInfo, register_template


# ============================================================
# Corporate 商务蓝
# ============================================================

register_template(TemplateInfo(
    name="cover_corporate",
    display_name="封面 — 商务蓝",
    category="business",
    doc_type="presentation",
    description="经典商务封面，蓝色渐变背景 + 几何圆形装饰 + 分隔线，适合正式汇报、项目方案。",
    variables={
        "title": "年度经营报告",
        "subtitle": "2026 年度总结与展望",
        "author": "汇报部门",
        "date": "2026年4月",
        "primary_color": "#1E40AF",
        "secondary_color": "#3B82F6",
    },
    tags=["封面", "商务", "蓝色", "正式"],
    content='''version: "4.0"
type: presentation

slides:
  - layout: blank
    background_board:
      background:
        type: linear_gradient
        angle: 135
        stops: ["{{primary_color}}", "{{secondary_color}}"]
      ornament:
        - type: shape
          shape_type: circle
          style: { fill: { color: "#FFFFFF", opacity: 0.05 } }
          position: { x: 160mm, y: -40mm, width: 220mm, height: 220mm }
        - type: shape
          shape_type: circle
          style: { fill: { color: "#FFFFFF", opacity: 0.03 } }
          position: { x: 190mm, y: 70mm, width: 160mm, height: 160mm }
    elements:
      - type: text
        content: "{{title}}"
        position: { x: 30mm, y: 42mm, width: 160mm, height: 28mm }
        style:
          font: { size: 42, weight: 700, color: "#FFFFFF" }
      - type: text
        content: "{{subtitle}}"
        position: { x: 30mm, y: 74mm, width: 160mm, height: 10mm }
        style:
          font: { size: 18, color: "#DBEAFE" }
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "#FFFFFF", opacity: 0.3 } }
        position: { x: 30mm, y: 94mm, width: 40mm, height: 1mm }
      - type: text
        content: "{{author}}  |  {{date}}"
        position: { x: 30mm, y: 104mm, width: 160mm, height: 8mm }
        style:
          font: { size: 14, color: "#BFDBFE" }
''',
))


# ============================================================
# Editorial 深色大气
# ============================================================

register_template(TemplateInfo(
    name="cover_editorial",
    display_name="封面 — 深色大气",
    category="business",
    doc_type="presentation",
    description="深色背景 + 白色大标题 + 底部色条，简洁有力，适合汇报、演讲、发布会。",
    variables={
        "title": "战略规划方案",
        "subtitle": "三年发展目标与实施路径",
        "author": "战略发展部",
        "accent_color": "#2563EB",
    },
    tags=["封面", "深色", "大气", "简洁"],
    content='''version: "4.0"
type: presentation

slides:
  - layout: blank
    background_board:
      background:
        type: color
        color: "#0F172A"
      ornament:
        type: color
        color: "{{accent_color}}"
        position: { x: 0mm, y: 126mm, width: 254mm, height: 4mm }
    elements:
      - type: text
        content: "{{title}}"
        position: { x: 30mm, y: 40mm, width: 194mm, height: 28mm }
        style:
          font: { size: 44, weight: 700, color: "#FFFFFF" }
      - type: text
        content: "{{subtitle}}"
        position: { x: 30mm, y: 72mm, width: 194mm, height: 10mm }
        style:
          font: { size: 18, color: "#94A3B8" }
      - type: text
        content: "{{author}}"
        position: { x: 30mm, y: 112mm, width: 100mm, height: 8mm }
        style:
          font: { size: 14, color: "#64748B" }
''',
))


# ============================================================
# Creative 创意撞色
# ============================================================

register_template(TemplateInfo(
    name="cover_creative",
    display_name="封面 — 创意撞色",
    category="creative",
    doc_type="presentation",
    description="深色背景 + 左侧醒目色条装饰，视觉冲击力强，适合产品发布、创意提案。",
    variables={
        "title": "新品发布会",
        "subtitle": "重新定义智能体验",
        "accent_color": "#E11D48",
        "author": "产品团队",
    },
    tags=["封面", "创意", "撞色", "产品"],
    content='''version: "4.0"
type: presentation

slides:
  - layout: blank
    background_board:
      background:
        type: color
        color: "#18181B"
      ornament:
        - type: shape
          shape_type: rectangle
          style: { fill: { color: "{{accent_color}}" } }
          position: { x: 0mm, y: 0mm, width: 8mm, height: 142.875mm }
        - type: shape
          shape_type: rectangle
          style: { fill: { color: "{{accent_color}}", opacity: 0.12 } }
          position: { x: 8mm, y: 0mm, width: 55mm, height: 142.875mm }
    elements:
      - type: text
        content: "{{title}}"
        position: { x: 20mm, y: 35mm, width: 210mm, height: 30mm }
        style:
          font: { size: 48, weight: 700, color: "#FFFFFF" }
      - type: text
        content: "{{subtitle}}"
        position: { x: 20mm, y: 70mm, width: 210mm, height: 10mm }
        style:
          font: { size: 20, color: "#A1A1AA" }
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "{{accent_color}}" } }
        position: { x: 20mm, y: 88mm, width: 24mm, height: 2mm }
      - type: text
        content: "{{author}}"
        position: { x: 20mm, y: 100mm, width: 100mm, height: 8mm }
        style:
          font: { size: 14, color: "#71717A" }
''',
))


# ============================================================
# Minimal 极简留白
# ============================================================

register_template(TemplateInfo(
    name="cover_minimal",
    display_name="封面 — 极简留白",
    category="business",
    doc_type="presentation",
    description="白色背景 + 大量留白 + 细色条点缀，克制优雅，适合学术、技术分享、内部沟通。",
    variables={
        "title": "技术架构设计",
        "subtitle": "微服务实践与演进",
        "author": "技术团队",
        "date": "2026.04",
        "accent_color": "#2563EB",
    },
    tags=["封面", "极简", "留白", "学术"],
    content='''version: "4.0"
type: presentation

slides:
  - layout: blank
    background_board:
      background:
        type: color
        color: "#FFFFFF"
      ornament:
        type: shape
        shape_type: rectangle
        style: { fill: { color: "#F1F5F9" } }
        position: { x: 0mm, y: 130mm, width: 254mm, height: 12.875mm }
    elements:
      - type: text
        content: "{{title}}"
        position: { x: 30mm, y: 38mm, width: 194mm, height: 28mm }
        style:
          font: { size: 40, weight: 700, color: "#0F172A" }
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "{{accent_color}}" } }
        position: { x: 30mm, y: 70mm, width: 16mm, height: 2mm }
      - type: text
        content: "{{subtitle}}"
        position: { x: 30mm, y: 80mm, width: 194mm, height: 10mm }
        style:
          font: { size: 18, color: "#64748B" }
      - type: text
        content: "{{author}}"
        position: { x: 30mm, y: 132mm, width: 80mm, height: 8mm }
        style:
          font: { size: 12, color: "#94A3B8" }
      - type: text
        content: "{{date}}"
        position: { x: 200mm, y: 132mm, width: 50mm, height: 8mm }
        style:
          font: { size: 12, color: "#94A3B8", align: right }
''',
))


# ============================================================
# Tech 科技感
# ============================================================

register_template(TemplateInfo(
    name="cover_tech",
    display_name="封面 — 科技感",
    category="creative",
    doc_type="presentation",
    description="深色背景 + 渐变光效 + 几何线条，科技感十足，适合技术发布、数据报告。",
    variables={
        "title": "AI 平台架构",
        "subtitle": "下一代智能基础设施",
        "author": "技术架构组",
        "accent_color": "#8B5CF6",
        "accent_color2": "#06B6D4",
    },
    tags=["封面", "科技", "深色", "渐变"],
    content='''version: "4.0"
type: presentation

slides:
  - layout: blank
    background_board:
      background:
        type: color
        color: "#0B0F19"
      ornament:
        - type: shape
          shape_type: rectangle
          style: { fill: { color: "{{accent_color}}", opacity: 0.08 } }
          position: { x: 0mm, y: 0mm, width: 254mm, height: 70mm }
        - type: shape
          shape_type: rectangle
          style: { fill: { color: "{{accent_color2}}", opacity: 0.05 } }
          position: { x: 0mm, y: 70mm, width: 254mm, height: 72.875mm }
        - type: shape
          shape_type: rectangle
          style: { fill: { color: "{{accent_color}}", opacity: 0.4 } }
          position: { x: 30mm, y: 90mm, width: 50mm, height: 1mm }
    elements:
      - type: text
        content: "{{title}}"
        position: { x: 30mm, y: 38mm, width: 194mm, height: 28mm }
        style:
          font: { size: 44, weight: 700, color: "#FFFFFF" }
      - type: text
        content: "{{subtitle}}"
        position: { x: 30mm, y: 70mm, width: 194mm, height: 10mm }
        style:
          font: { size: 18, color: "#818CF8" }
      - type: text
        content: "{{author}}"
        position: { x: 30mm, y: 100mm, width: 160mm, height: 8mm }
        style:
          font: { size: 14, color: "#475569" }
''',
))


# ============================================================
# Elegant 优雅质感
# ============================================================

register_template(TemplateInfo(
    name="cover_elegant",
    display_name="封面 — 优雅质感",
    category="business",
    doc_type="presentation",
    description="深绿/酒红背景 + 金色点缀，高级质感，适合高端商务、品牌展示、投资路演。",
    variables={
        "title": "品牌战略报告",
        "subtitle": "高端市场定位与增长策略",
        "author": "品牌战略部",
        "bg_color": "#064E3B",
        "accent_color": "#D4AF37",
    },
    tags=["封面", "优雅", "高端", "质感"],
    content='''version: "4.0"
type: presentation

slides:
  - layout: blank
    background_board:
      background:
        type: color
        color: "{{bg_color}}"
      ornament:
        - type: shape
          shape_type: rectangle
          style: { fill: { color: "{{accent_color}}", opacity: 0.15 } }
          position: { x: 20mm, y: 20mm, width: 214mm, height: 102.875mm }
    elements:
      - type: text
        content: "{{title}}"
        position: { x: 30mm, y: 40mm, width: 194mm, height: 28mm }
        style:
          font: { size: 42, weight: 700, color: "#FFFFFF" }
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "{{accent_color}}" } }
        position: { x: 30mm, y: 72mm, width: 30mm, height: 1mm }
      - type: text
        content: "{{subtitle}}"
        position: { x: 30mm, y: 80mm, width: 194mm, height: 10mm }
        style:
          font: { size: 16, color: "#A7F3D0" }
      - type: text
        content: "{{author}}"
        position: { x: 30mm, y: 110mm, width: 100mm, height: 8mm }
        style:
          font: { size: 12, color: "#6EE7B7" }
''',
))


# ============================================================
# Flat 扁平清新
# ============================================================

register_template(TemplateInfo(
    name="cover_flat",
    display_name="封面 — 扁平清新",
    category="business",
    doc_type="presentation",
    description="明亮色块 + 圆角几何 + 清新配色，年轻活力，适合团队汇报、内部分享。",
    variables={
        "title": "季度工作汇报",
        "subtitle": "团队协作与成果展示",
        "author": "产品组",
        "primary_color": "#0EA5E9",
        "secondary_color": "#38BDF8",
    },
    tags=["封面", "扁平", "清新", "活力"],
    content='''version: "4.0"
type: presentation

slides:
  - layout: blank
    background_board:
      background:
        type: color
        color: "#F0F9FF"
      ornament:
        - type: shape
          shape_type: rounded_rectangle
          style: { fill: { color: "{{primary_color}}" } }
          position: { x: 160mm, y: -20mm, width: 120mm, height: 180mm }
        - type: shape
          shape_type: rounded_rectangle
          style: { fill: { color: "{{secondary_color}}", opacity: 0.3 } }
          position: { x: 180mm, y: 40mm, width: 100mm, height: 120mm }
    elements:
      - type: text
        content: "{{title}}"
        position: { x: 25mm, y: 40mm, width: 130mm, height: 28mm }
        style:
          font: { size: 38, weight: 700, color: "#0C4A6E" }
      - type: text
        content: "{{subtitle}}"
        position: { x: 25mm, y: 72mm, width: 130mm, height: 10mm }
        style:
          font: { size: 16, color: "#0369A1" }
      - type: text
        content: "{{author}}"
        position: { x: 25mm, y: 100mm, width: 100mm, height: 8mm }
        style:
          font: { size: 14, color: "#7DD3FC" }
''',
))


# ============================================================
# Chinese 中国风
# ============================================================

register_template(TemplateInfo(
    name="cover_chinese",
    display_name="封面 — 中国风",
    category="creative",
    doc_type="presentation",
    description="传统中国红 + 纹样装饰 + 竖排标题，文化底蕴，适合传统文化、节日庆典、国潮品牌。",
    variables={
        "title": "年度盛典",
        "subtitle": "回顾与展望",
        "author": "组委会",
        "bg_color": "#7F1D1D",
        "accent_color": "#DC2626",
    },
    tags=["封面", "中国风", "传统", "红色"],
    content='''version: "4.0"
type: presentation

slides:
  - layout: blank
    background_board:
      background:
        type: color
        color: "{{bg_color}}"
      ornament:
        - type: shape
          shape_type: rectangle
          style: { fill: { color: "{{accent_color}}", opacity: 0.2 } }
          position: { x: 0mm, y: 0mm, width: 4mm, height: 142.875mm }
        - type: shape
          shape_type: rectangle
          style: { fill: { color: "{{accent_color}}", opacity: 0.2 } }
          position: { x: 250mm, y: 0mm, width: 4mm, height: 142.875mm }
        - type: shape
          shape_type: rectangle
          style: { fill: { color: "#DC2626", opacity: 0.1 } }
          position: { x: 4mm, y: 0mm, width: 246mm, height: 2mm }
        - type: shape
          shape_type: rectangle
          style: { fill: { color: "#DC2626", opacity: 0.1 } }
          position: { x: 4mm, y: 140.875mm, width: 246mm, height: 2mm }
    elements:
      - type: text
        content: "{{title}}"
        position: { x: 80mm, y: 35mm, width: 94mm, height: 35mm }
        style:
          font: { size: 48, weight: 700, color: "#FEE2E2" }
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "#DC2626" } }
        position: { x: 115mm, y: 75mm, width: 24mm, height: 1mm }
      - type: text
        content: "{{subtitle}}"
        position: { x: 80mm, y: 82mm, width: 94mm, height: 10mm }
        style:
          font: { size: 16, color: "#FCA5A5" }
      - type: text
        content: "{{author}}"
        position: { x: 80mm, y: 105mm, width: 94mm, height: 8mm }
        style:
          font: { size: 12, color: "#F87171", align: center }
''',
))
