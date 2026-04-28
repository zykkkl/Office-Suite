# Office Suite 4.0

全媒体融合文档引擎 — 从声明式 YAML DSL 编译到五种文档格式。

```
YAML DSL → Parser → IR Document → Renderer → .pptx / .docx / .xlsx / .pdf / .html
```

类比 LLVM：前端解析设计意图 → 统一中间表示 → 后端渲染到任意格式。180+ 测试，全部通过。

## 快速开始

### 安装

```bash
git clone <repo-url> && cd Office-Suite
pip install -r requirements.txt
```

### 一行命令生成文档

```bash
# 使用内置模板生成五格式文档
py -m office_suite.tools.generate apple_benefits

# 使用自定义 YAML 生成
py -m office_suite.tools.generate my_presentation
```

输出到 `demo_output/<项目名>/`，自动生成 `.pptx`, `.pdf`, `.docx`, `.xlsx`, `.html`。

### Python API

```python
from office_suite.dsl.parser import parse_yaml
from office_suite.ir.compiler import compile_document
from office_suite.renderer.pptx.deck import PPTXRenderer

doc = parse_yaml("presentation.yml")
ir_doc = compile_document(doc)
PPTXRenderer().render(ir_doc, "output.pptx")
```

### 格式转换

```python
from office_suite.tools.convert import convert_dsl_file

convert_dsl_file("input.yml", "output.docx", "docx")
convert_dsl_file("input.yml", "output.xlsx", "xlsx")
convert_dsl_file("input.yml", "output.pdf", "pdf")
convert_dsl_file("input.yml", "output.html", "html")
```

### 质量检查

```bash
py -m office_suite.tools.check deck.yml --render pptx --output-dir output/check
```

## DSL 示例

```yaml
version: "4.0"
type: presentation
theme: default

slides:
  - layout: blank
    elements:
      - type: text
        content: "Hello World"
        position: { x: 50mm, y: 80mm, width: 150mm, height: 20mm }
        style:
          font: { family: "Arial", size: 44, weight: 700, color: "#1E293B" }
```

## 支持格式

| 格式 | 状态 | 渲染器 |
|------|------|--------|
| `.pptx` | 支持 | `renderer/pptx/deck.py` |
| `.docx` | 支持 | `renderer/docx/document.py` |
| `.xlsx` | 支持 | `renderer/xlsx/workbook.py` |
| `.pdf` | 支持 | `renderer/pdf/canvas.py` |
| `.html` | 支持 | `renderer/html/dom.py` |

## 功能亮点

**AI 驱动**: 意图解析、设计建议、质量评审 (`ai/intent.py`, `ai/suggest.py`, `ai/critique.py`)

**动画引擎**: 入场/退出/强调/路径动画，7 种缓动函数，物理动画（弹簧/重力/轨道）(`engine/style/animation.py`)

**艺术字**: 7 种 WordArt 变换映射到 PPTX presetTextWarp (`engine/text/shaping.py`)

**文本布局**: 对齐 + 垂直对齐 + 内边距 (`align`, `vertical_align`, `margin`)

**主题系统**: Fluent / Material 3 / Apple HIG / Universal 预设主题 (`themes/`)

**内置模板**: 12 个高质量模板 — 工作汇报、项目方案、年度报告、产品发布、商业计划书、简历、学术答辩、营销方案等 (`templates/builtins/`)

**组件库**: 图表卡片、统计卡片、时间线、对比表、信息图 (`components/builtins/`)

**多文件演示文稿**: `deck.yml` + `pages/*.yml` 分页管理，适合复杂演示文稿 (`dsl/parser.py` 支持 `pages` 字段)

**统一质量门**: 一键运行解析 → 编译 → 校验 → Lint → 渲染 (`tools/check.py`)

## 项目结构

```
office_suite/
├── dsl/              # YAML/JSON 解析器 + Schema + 验证器
├── ir/               # 中间表示: 编译器、样式级联、优化器、图分析
├── renderer/         # 五格式渲染器 (pptx/docx/xlsx/pdf/html)
├── engine/           # 引擎层
│   ├── layout/       # 约束布局、Flexbox、网格
│   ├── style/        # 颜色、渐变、动画、字体
│   ├── text/         # 富文本、路径文字、文本塑形
│   └── media/        # 图像处理、SVG 处理
├── pipeline/         # 计算图工作流: 节点、调度、历史/产物存储
├── ai/               # AI: 意图解析、设计建议、质量评审
├── components/       # 内置组件注册表 + 5 个组件
├── templates/        # 模板注册表 + 12 个内置模板
├── themes/           # 主题引擎 + 4 个预设主题
├── hub/              # 资源中枢: 注册表、解析器、缓存、多 Provider
└── tools/            # 生成、转换、检查、Lint、预览、批处理
```

## 测试

| 阶段 | 测试数 | 状态 |
|------|--------|------|
| Phase 1 (DSL + IR) | 65 | ✅ |
| Phase 2 (PPTX) | 60 | ✅ |
| Phase 3 (Hub) | 50 | ✅ |
| Phase 4 (DOCX + XLSX) | 24 | ✅ |
| Phase 5 (AI) | 42 | ✅ |
| Phase 6 (Theme + Components) | 57 | ✅ |
| Phase 7 (PDF + HTML) | 30 | ✅ |
| Phase 8 (Animation + WordArt) | 58 | ✅ |
| Phase 9 (Templates) | 64 | ✅ |
| Pipeline | 39 | ✅ |
| **合计 (pytest)** | **180** | **全绿** |

```bash
pytest tests/ -v
```

## 工具脚本

| 命令 | 说明 |
|------|------|
| `py -m office_suite.tools.generate <name>` | 从 YAML 生成 PPTX + PDF |
| `py -m office_suite.tools.check <file> --render <fmt>` | 统一质量门 (解析→编译→校验→Lint→渲染) |
| `py -m office_suite.tools.convert <file> <out> <fmt>` | 格式转换 |
| `py -m office_suite.tools.linter <file>` | 独立 Lint 检查 |
| `py -m office_suite.tools.batch <glob>` | 批量处理 |
| `py -m office_suite.tools.preview <file>` | 启动本地预览 |
| `py demo_all_formats.py` | 端到端五格式演示 |

## 特性分级

| 等级 | 特性 | 状态 |
|------|------|------|
| P0 | 文本、图片、形状、表格、坐标系统、样式级联 | ✅ |
| P1 | 约束布局、Flexbox、动画、艺术字 | ✅ |
| P2 | 视频/音频、滤镜、路径文字、实时预览 | 规划中 |
| P3 | 3D 模型、地图 | 规划中 |

## 文档

- [设计方案](Office_Suite_4.0_设计方案_v2.md) — 完整架构设计
- [实施状态](STATUS.md) — 各阶段详情与测试汇总
- [差距分析](GAP_ANALYSIS_REPORT.md) — 与设计方案的差距分析
- [PPT 布局指南](office_suite/guidelines/ppt_layout_system.md) — 演示文稿布局系统规范
- [Skill 指南](office_suite/SKILL.md) — Agent 工作流与各格式生成规范
