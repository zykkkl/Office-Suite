"""个人简历模板"""

from ..registry import TemplateInfo, register_template

register_template(TemplateInfo(
    name="resume",
    display_name="个人简历",
    category="creative",
    doc_type="presentation",
    description="适用于个人简历、自我介绍、求职展示，包含教育背景、工作经验、技能特长。",
    variables={
        "name": "姓名",
        "title_role": "求职意向",
        "primary_color": "#0078D4",
        "email": "email@example.com",
        "phone": "138-0000-0000",
        "education": "教育背景：\n\nXX 大学 / XX 专业 / 硕士\n2020 - 2023\n\nXX 大学 / XX 专业 / 学士\n2016 - 2020",
        "experience": "工作经验：\n\nXX 公司 / 高级工程师\n2023 - 至今\n- 负责 XX 系统架构设计\n- 带领团队完成 XX 项目\n- 性能优化，效率提升 40%",
        "skills": "核心技能：\n\n编程语言：Python / Go / TypeScript\n框架：React / FastAPI / gRPC\n工具：Docker / K8s / AWS",
        "project_rows": "3",
        "projects": '[["项目", "角色", "成果"], ["项目A", "技术负责人", "用户增长200%"], ["项目B", "核心开发", "性能提升50%"]]',
    },
    tags=["简历", "求职", "自我介绍"],
    content='''version: "4.0"
type: presentation
theme: fluent

styles:
  title:
    font: { size: 36, weight: 700, color: "#FFFFFF" }
    fill: { color: "{{primary_color}}" }
  heading:
    font: { size: 24, weight: 700, color: "#0F172A" }
  body:
    font: { size: 14, color: "#334155" }

slides:
  - layout: blank
    elements:
      - type: shape
        shape_type: rounded_rectangle
        style: { fill: { color: "{{primary_color}}" } }
        position: { x: 0mm, y: 0mm, width: 254mm, height: 80mm }
      - type: text
        content: "{{name}}"
        style: title
        position: { x: 30mm, y: 15mm, width: 194mm, height: 20mm }
      - type: text
        content: "{{title_role}} | {{email}} | {{phone}}"
        style: { font: { size: 14, color: "#FFFFFF" } }
        position: { x: 30mm, y: 45mm, width: 194mm, height: 10mm }

  - layout: blank
    elements:
      - type: text
        content: "教育背景"
        style: heading
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
      - type: text
        content: "{{education}}"
        style: body
        position: { x: 20mm, y: 35mm, width: 214mm, height: 140mm }

  - layout: blank
    elements:
      - type: text
        content: "工作经验"
        style: heading
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
      - type: text
        content: "{{experience}}"
        style: body
        position: { x: 20mm, y: 35mm, width: 214mm, height: 140mm }

  - layout: blank
    elements:
      - type: text
        content: "核心技能"
        style: heading
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
      - type: text
        content: "{{skills}}"
        style: body
        position: { x: 20mm, y: 35mm, width: 214mm, height: 140mm }

  - layout: blank
    elements:
      - type: text
        content: "项目经历"
        style: heading
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
      - type: table
        rows: {{project_rows}}
        cols: 3
        data: {{projects}}
        position: { x: 20mm, y: 30mm, width: 214mm, height: 100mm }
''',
))
