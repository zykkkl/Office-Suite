# Office Suite 4.0

## 概述

全媒体融合文档引擎 — 从声明式 DSL 编译到任意文档格式。

## 核心流程

```
YAML DSL → Parser → IR Document → Renderer → .pptx / .docx / .xlsx / .pdf / .html
```

## 使用方式

### 直接调用

```python
from office_suite.dsl.parser import parse_yaml
from office_suite.ir.compiler import compile_document
from office_suite.renderer.pptx.deck import PPTXRenderer

# 1. 解析 DSL
doc = parse_yaml("presentation.yml")

# 2. 编译为 IR
ir_doc = compile_document(doc)

# 3. 渲染
renderer = PPTXRenderer()
renderer.render(ir_doc, "output.pptx")
```

### CLI

```bash
python -m office_suite build input.yml -o output.pptx
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

## 特性分级

| 等级 | 特性 |
|------|------|
| P0 (MVP) | 文本、图片、形状、表格、绝对/相对坐标、样式级联 |
| P1 | 约束布局、Flexbox、动画、艺术字、OKLCH 色彩 |
| P2 | 视频/音频、滤镜、路径文字、实时预览 |
| P3 | 3D 模型、地图 |

## 支持格式

- `.pptx` — PowerPoint (Phase 2 完善)
- `.docx` — Word (Phase 4)
- `.xlsx` — Excel (Phase 4)
- `.pdf` — PDF (Phase 7)
- `.html` — HTML (Phase 7)
