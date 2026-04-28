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

## 坐标系说明

**幻灯片尺寸（16:9）：254mm × 142.875mm（10" × 5.625"）**

| 轴 | 范围 | 说明 |
|----|------|------|
| x  | 0 ~ 254mm | 水平方向，从左到右 |
| y  | 0 ~ 142.875mm | 垂直方向，从上到下 |

> ⚠️ 注意：`y + height` 必须 ≤ 142.875mm，否则内容会超出幻灯片底部。
> 190.5mm 是 4:3 幻灯片的高度，**不要**用于 16:9 布局。

## Stack 布局容器

避免手动计算 y 坐标，使用 `layout: stack` 让子元素自动纵向排列：

### Slide 级别 Stack

```yaml
slides:
  - layout: stack
    background:
      color: "#FFFFFF"
      spacing: 8        # 元素间距，默认 8mm
      padding_top: 15   # 上边距，默认 15mm
      padding_left: 30  # 左边距，默认 30mm
      content_width: 194 # 内容宽度，默认 194mm
    elements:
      - type: text
        content: "标题"     # 不需要写 position，自动排列
      - type: text
        content: "正文内容" # 自动接在标题下方
```

### 元素级别 Stack（Group 容器）

```yaml
- type: group
  position: { x: 20mm, y: 30mm, width: 214mm, height: 100mm }
  extra:
    layout: stack
    spacing: 5
    padding_top: 10
    padding_left: 10
    content_width: 190
  children:
    - type: text
      content: "第一行"
    - type: text
      content: "第二行"
```

### 规则

- 没有 `position` 的元素自动进入 stack 流
- 有 `position` 的元素保持绝对定位，不参与 stack 排列
- stack 不会裁剪内容，超出容器的部分仍然渲染（配合越界警告排查）

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
