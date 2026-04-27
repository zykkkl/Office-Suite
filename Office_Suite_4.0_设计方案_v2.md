# Office Suite 4.0 — 全媒体融合文档引擎设计方案 v2

> **核心观念进化：从「文档生成器」到「内容操作系统」**
>
> 🔶 v2 优化标注：`[优化]` = 新增/重写，`[调整]` = 修改原有内容，`[删除]` = 移除的内容

---

## 一、设计哲学

**不是「调库生成文件」，而是「编译设计意图到任意文档格式」。**

```
                    ┌─────────────┐
                    │  Design IR   │  ← 中间表示层（核心创新）
                    └──────┬──────┘
           ┌───────────┬───┴───┬───────────┐
           ▼           ▼       ▼           ▼
        .pptx       .docx    .xlsx       .pdf    .html
```

类比：LLVM 编译器 — 前端解析设计意图 → IR 统一表示 → 后端渲染到任意格式。

```
传统方式：代码 → 调 API → 输出文件（设计是附属品）
本方案：  设计意图 → 引擎计算 → 渲染输出（代码是表达手段）

传统 Office：    人 → 打字/贴图 → 文件
本方案：         人 → 意图 → 引擎自动编排一切资源 → 文件
```

[优化] **补充核心设计约束，避免过度工程：**

> **三不原则**
> 1. 不做运行时平台 — 本方案是编译器/构建工具，不是服务端运行时
> 2. 不做通用工作流引擎 — 仅支持文档生成流水线，不追求 Airflow 级调度能力
> 3. 不做 WYSISYG 编辑器 — DSL 是主要输入方式，预览是辅助验证手段

---

## 二、全景架构

```
office-suite/
│
├── SKILL.md                              # 路由入口
│
├── dsl/                                  # 第一层：设计语言
│   ├── __init__.py
│   ├── schema.py                         # DSL Schema 定义
│   ├── parser.py                         # YAML/JSON → IR 解析器
│   └── validator.py                      # 设计约束校验
│
├── ir/                                   # 第二层：中间表示 [优化] 提前到 workflow 之前
│   ├── __init__.py
│   ├── types.py                          # IR 节点类型 + 包含约束 [优化] 原 nodes.py
│   ├── graph.py                          # 依赖图 & 层级树
│   ├── layout_spec.py                    # 布局规格（绝对的/相对的/约束的） [优化] 新增
│   ├── style_spec.py                     # 样式规格（级联规则定义） [优化] 新增
│   ├── resolver.py                       # 约束求解器
│   ├── optimizer.py                      # IR 优化
│   └── diff.py                           # 设计差异比较
│
├── engine/                               # 第三层：计算引擎 [调整] 精简层级
│   ├── layout/                           # 布局引擎
│   │   ├── constraint.py               # 约束求解（Cassowary）
│   │   ├── grid.py                     # 栅格系统
│   │   └── flex.py                     # 弹性布局（Flexbox）
│   ├── style/                           # 样式引擎
│   │   ├── cascade.py                  # 样式级联
│   │   ├── color.py                    # 色彩空间（OKLCH）
│   │   ├── gradient.py                 # 渐变系统
│   │   ├── typography.py               # 排版
│   │   └── animation.py                # 动画引擎
│   ├── text/                            # 文本引擎
│   │   ├── shaping.py                  # 文字塑形（WordArt）
│   │   ├── path_text.py               # 路径文字
│   │   └── rich_text.py               # 富文本
│   └── media/                           # 媒体处理
│       ├── image_proc.py               # 图片处理
│       └── svg_proc.py                 # SVG 处理 [调整] 移除 video/audio_proc，视频音频处理推迟到后期
│
├── hub/                                  # 资源中枢
│   ├── __init__.py
│   ├── registry.py                      # 资源提供者注册表
│   ├── resolver.py                      # 资源解析器
│   ├── cache.py                         # 资源缓存
│   └── providers/                       # 资源提供者
│       ├── mcp_provider.py             # MCP 服务器
│       ├── skill_provider.py           # 其他 Skill
│       ├── ai_provider.py              # AI 生成资源
│       └── local_provider.py           # 本地文件 [调整] 合并 web_provider/data_provider 到各 provider 内
│
├── pipeline/                             # 流水线 [调整] 原 workflow/ 重命名，简化
│   ├── __init__.py
│   ├── core/
│   │   ├── graph.py                     # DAG 图结构
│   │   ├── scheduler.py                 # 拓扑排序 + 并发调度
│   │   └── context.py                   # 执行上下文
│   ├── nodes/                            # 节点类型库 [调整] 精简
│   │   ├── data/
│   │   │   ├── fetch.py
│   │   │   └── transform.py
│   │   ├── compute/
│   │   │   ├── skill_invoke.py
│   │   │   ├── mcp_call.py
│   │   │   └── ai_generate.py
│   │   ├── design/
│   │   │   ├── layout.py
│   │   │   └── style.py
│   │   ├── render/
│   │   │   ├── to_pptx.py
│   │   │   ├── to_docx.py
│   │   │   ├── to_xlsx.py
│   │   │   ├── to_pdf.py
│   │   │   └── to_html.py
│   │   └── control/
│   │       ├── condition.py
│   │       ├── parallel.py
│   │       └── retry.py                 # [调整] 合并原 retry/fallback/gate/checkpoint
│   └── store/
│       ├── artifact_store.py
│       └── history_store.py
│
├── ai/                                  # AI 设计助手
│   ├── __init__.py
│   ├── intent.py                        # NL → 设计意图解析
│   ├── suggest.py                       # 设计建议引擎
│   └── critique.py                      # 设计质量评审
│
├── renderer/                            # 格式渲染器
│   ├── base.py                          # [优化] 新增：渲染器基类 + 能力声明接口
│   ├── capability_map.py                # [优化] 新增：IR 特性 → 渲染器能力映射表
│   ├── pptx/
│   │   ├── deck.py
│   │   ├── slide.py
│   │   ├── shape.py
│   │   ├── animation.py
│   │   ├── transition.py
│   │   ├── master.py
│   │   └── com_backend.py
│   ├── docx/
│   │   ├── document.py
│   │   ├── section.py
│   │   ├── block.py
│   │   └── style.py
│   ├── xlsx/
│   │   ├── workbook.py
│   │   ├── sheet.py
│   │   ├── chart.py
│   │   └── conditional.py
│   ├── pdf/
│   │   ├── canvas.py
│   │   └── font.py
│   └── html/
│       ├── dom.py
│       └── css.py
│
├── components/                          # 可复用组件库
│   ├── registry.py
│   └── builtins/
│       ├── charts/
│       ├── diagrams/
│       ├── cards/
│       └── infographics/
│
├── themes/                              # 主题系统
│   ├── engine.py
│   ├── material3.py
│   ├── fluent.py
│   ├── apple_hig.py
│   └── custom/
│
├── assets/
│   ├── fonts/
│   ├── icons/
│   └── templates/
│       ├── business/
│       ├── academic/
│       └── creative/
│
├── tools/
│   ├── preview.py                       # 实时预览
│   ├── linter.py                        # 设计规范检查
│   ├── convert.py                       # 格式互转
│   └── batch.py                         # 批量生成
│
└── tests/
    ├── test_dsl_parser.py               # [优化] 新增：DSL 解析测试
    ├── test_ir_constraints.py           # [优化] 新增：IR 包含约束测试
    ├── test_ir_to_pptx.py               # [优化] 新增：IR→PPTX 映射测试
    ├── test_layout.py
    ├── test_render.py
    └── fixtures/
```

[优化] **架构调整说明：**

| 变更 | 原方案 | 调整后 | 理由 |
|------|--------|--------|------|
| ir/ 位置 | 在 workflow 后 | 提前到 workflow 前 | IR 是核心抽象，应在流水线之前定义 |
| workflow → pipeline | workflow/ 命名 | pipeline/ | 避免暗示通用工作流引擎 |
| 节点类型精简 | 6 类 20+ 节点 | 4 类 12 节点 | 去掉通知节点、合并控制节点，MVP 不需要 |
| 中间件链移除 | 7 层中间件 | 仅保留 retry | 熔断/限流/追踪是运行时关注点，构建工具不需要 |
| video/audio_proc | 包含 | 移除 | 媒体嵌入可后期支持，核心先做图片+SVG |
| 触发器系统 | 6 种触发器 | 移除 | 触发器是外部编排器职责，不属于文档引擎 |
| 渲染器基类 | 无 | 新增 base.py + capability_map | 优雅降级的基础 |

---

## 三、设计语言（DSL）

**声明式 YAML 定义文档，而非命令式代码。**

### 核心 DSL 示例

```yaml
# demo.presentation.yml
version: "4.0"
type: presentation
theme: corporate

# 数据源绑定
data:
  revenue:
    source: quarterly.csv
    columns: [Q1, Q2, Q3, Q4]
  growth:
    formula: (revenue.Q4 - revenue.Q1) / revenue.Q1 * 100

# 全局样式
styles:
  title:
    font: { family: "Microsoft YaHei UI", size: 44, weight: 700 }
    fill: { gradient: { type: linear, angle: 135, stops: ["#2563EB", "#7C3AED"] } }
    shadow: { blur: 16, offset: [0, 4], color: "#2563EB30" }
    text_effect: { transform: arch_up, outline: { color: "#FFFFFF40", width: 1 } }

slides:
  - layout: blank
    background: { gradient: { type: radial, stops: ["#0F172A", "#1E293B"] } }
    elements:
      - type: image
        source: mcp__unsplash
        query: "dark tech abstract"
        size: { width: 100%, height: 100% }
        filter: duotone(primary, surface)    # [优化] 见下方降级说明
        opacity: 0.3
        animation: { type: scale_slow, duration: 20, repeat: infinite }

      - type: text
        content: "Office Suite 4.0"
        style: title
        position: { bottom: 3.5, center: true }  # [优化] 见下方坐标映射

      - type: video               # [调整] 标注为 P2 特性，MVP 不支持
        source: mcp__pexels_video
        query: "abstract particles motion"
        loop: true
        muted: true
        opacity: 0.15
        position: background
```

[优化] **DSL 特性分级：**

| 特性 | 等级 | 说明 |
|------|------|------|
| 文本、图片、形状、表格 | P0 | MVP 必须支持 |
| position 绝对/相对坐标 | P0 | MVP 必须支持 |
| 样式级联 + 主题 | P0 | MVP 必须支持 |
| 约束布局（Cassowary） | P1 | 第二批支持 |
| Flexbox 布局 | P1 | 第二批支持 |
| 动画 | P1 | 第二批支持 |
| 艺术字变换 | P1 | 第二批支持 |
| Filter（duotone 等） | P2 | 优先级低，见降级策略 |
| 视频/音频嵌入 | P2 | 后期支持 |
| 3D 模型 / 地图 | P3 | 远期，视需求决定 |
| 路径文字 | P2 | 后期支持 |

### 资源引用语法

| 语法 | 示例 | 说明 |
|------|------|------|
| `mcp__unsplash` | `source: mcp__unsplash, query: "nature"` | MCP 服务器获取 |
| `ai__generate` | `source: ai__generate, prompt: "..."` | AI 生成 |
| `skill__matplotlib` | `source: skill__matplotlib, data: ...` | 其他 Skill 产出 |
| `file://` | `source: file://logo.png` | 本地文件 |

---

## 四、中间表示（IR）

### [优化] IR 类型系统 + 包含约束

原方案仅列了枚举，没有定义节点之间的合法组合关系。这是导致渲染器映射混乱的根源。

```python
class NodeType(Enum):
    DOCUMENT = "document"
    SLIDE = "slide"
    SECTION = "section"
    SHAPE = "shape"
    TEXT = "text"
    IMAGE = "image"
    CHART = "chart"
    TABLE = "table"
    GROUP = "group"
    VIDEO = "video"       # P2
    AUDIO = "audio"       # P2
    MODEL_3D = "3d_model" # P3
    MAP = "map"           # P3
    CODE = "code"         # P2
    DIAGRAM = "diagram"   # P1

# [优化] 新增：类型包含规则 — 哪些节点可以包含哪些子节点
CONTAINMENT_RULES = {
    NodeType.DOCUMENT: [NodeType.SLIDE, NodeType.SECTION],
    NodeType.SECTION:  [NodeType.SLIDE],
    NodeType.SLIDE:    [NodeType.SHAPE, NodeType.TEXT, NodeType.IMAGE,
                        NodeType.CHART, NodeType.TABLE, NodeType.GROUP,
                        NodeType.VIDEO, NodeType.DIAGRAM],  # 根据等级过滤
    NodeType.GROUP:    [NodeType.SHAPE, NodeType.TEXT, NodeType.IMAGE,
                        NodeType.CHART, NodeType.TABLE, NodeType.DIAGRAM],
    # 其他类型为叶子节点，不可包含子节点
}

# [优化] 新增：类型属性约束 — 每种节点必须/可选的属性
REQUIRED_PROPS = {
    NodeType.TEXT:  ["content"],
    NodeType.IMAGE: ["source"],
    NodeType.CHART: ["data_ref", "chart_type"],
    NodeType.TABLE: ["data_ref"],
    NodeType.SLIDE: ["layout"],
}
```

### 位置系统

- **绝对坐标**（mm）
- **相对坐标**（百分比）
- **约束求解**（Cassowary 算法，同 iOS AutoLayout）— P1
- **栅格**（12/24 列）— P1
- **弹性**（Flexbox 语义）— P1

[优化] **P0 仅支持绝对坐标 + 相对坐标。** 约束/栅格/Flex 推迟到 P1。

### [优化] 坐标映射规则（新增）

DSL 中的位置描述必须明确映射到目标格式的坐标系统：

```
DSL position 规范：
  position:
    x: 20mm | 10% | center
    y: 15mm | 20% | top
    width: 80mm | 60%
    height: 40mm | auto       # auto = 根据内容计算

映射规则：
  mm  → PPTX: * 36000 (EMU)     DOCX: * 1440 (Twips)    PDF: 直接使用
  %   → 相对于父容器尺寸计算后再走 mm 映射
  auto → 渲染器自行计算（文本根据字号+换行，图片根据原始比例）
  center → (parent_width - self_width) / 2
```

### 样式级联

```
theme → document → slide → element → inline
优先级递增，支持 !important 覆盖。
```

### 色彩空间

使用 **OKLCH**（感知均匀的色彩空间），比 HEX/RGB 更适合设计。自动处理对比度、无障碍适配。

[优化] **P0 先用 sRGB / HEX，OKLCH 作为 P1 增强特性。** 理由：
- 主流渲染库（PptxGenJS, python-docx）只接受 HEX/RGB
- OKLCH → sRGB 转换可以作为引擎层的透明转换
- 避免在 MVP 阶段同时解决色彩空间转换和渲染器对接

---

## 五、资源中枢（Hub）

**核心创新：Office Suite 不再自己找资源，而是通过中枢从任何地方获取资源。**

### MCP 集成能力

| 资源类型 | MCP 来源 | Skill 联动 | AI 生成 |
|---------|---------|-----------|--------|
| **图片** | Unsplash / Pexels / DALL-E | matplotlib / seaborn | DALL-E 3 / SD / MiniMax |
| **视频** | Pexels / Runway | — | Runway / Pika / Kling |
| **音频** | — | — | TTS / ElevenLabs |
| **图表** | ECharts | matplotlib / chart skill | 智能图表 |
| **流程图** | Mermaid | architecture-design | — |
| **3D 模型** | Sketchfab | — | AI 3D 生成 |
| **地图** | Google Maps / Mapbox | — | — |
| **代码** | GitHub | code-review | — |
| **数据** | API / DB / Web Search | research / statistical | — |
| **文案** | Web Search | deep-research / scientific-writing | GPT / Claude |

[优化] **资源获取降级策略（新增）：**

资源中枢必须处理获取失败的情况，不能让整个文档生成因为一张图片挂掉：

```python
class ResourceResolution:
    """资源解析结果"""

    @dataclass
    class Result:
        value: Any              # 成功时的资源
        fallback_used: bool     # 是否使用了降级
        fallback_reason: str    # 降级原因

    # 降级策略链：
    # 1. 主资源获取
    # 2. 缓存中的历史版本
    # 3. 占位符资源（带标记，后续可替换）
    # 4. 空白占位 + 警告日志
```

| 失败场景 | 降级行为 |
|---------|---------|
| MCP 图片 API 超时 | 使用缓存的同查询历史图片，或灰色占位图 + 文字标注 |
| AI 生成质量差/格式错 | 回退到本地模板，标记需人工审核 |
| 数据源不可达 | 使用 `data:` 字段中的内联后备数据，或跳过该图表 |
| 本地文件不存在 | 生成警告，使用占位符 |

---

## 六、流水线（原工作流引擎）

[调整] **核心简化：**

| 原方案 | 调整后 | 理由 |
|--------|--------|------|
| 6 种触发器 | 移除 | 触发是外部编排器（Claude/Cron）的职责 |
| 7 层中间件链 | 仅保留 retry + timeout | 熔断/限流/追踪是运行时平台关注点 |
| gate 审批门 | 移除 | 交互式审批在 Claude 对话中完成 |
| checkpoint 断点续跑 | 移除 | 文档生成一般 <5min，不需要断点续跑 |
| 可视化监控面板 | 移至 P2 | 非核心 |
| 通知节点 | 移除 | 使用 Claude 自身能力通知 |

### 设计理念

**不是「脚本按顺序跑」，是「声明式 DAG 编排」。**

```
传统脚本：     A → B → C → D → 输出（线性、脆弱）
本方案：      声明依赖关系 → 自动拓扑排序 → 并行调度 → 汇聚输出
```

### 流水线 DSL 示例

```yaml
name: "研究 → 演示 全自动流水线"

config:
  timeout: 600s
  retry: { max: 3, backoff: exponential }
  parallelism: 4

graph:
  # 阶段 1：研究（并行扇出）
  research:
    type: parallel
    nodes:
      literature_search:
        type: skill_invoke
        skill: deep-research
        params: { query: "${vars.topic}" }

      paper_collection:
        type: skill_invoke
        skill: paper-lookup
        params: { query: "${vars.topic}", limit: 20 }

  # 阶段 2：内容生成
  content_generation:
    depends_on: [research]
    type: parallel
    nodes:
      key_findings:
        type: ai_generate
        model: claude-sonnet-4-6
        prompt: "从研究中提取关键发现：${research.literature_search.output}"

      cover_image:
        type: ai_generate
        provider: mcp__minimax
        prompt: "${vars.topic} abstract cover art"

  # 阶段 3：多格式渲染
  render:
    depends_on: [content_generation]
    type: parallel
    nodes:
      render_pptx: { type: render, format: pptx }
      render_pdf: { type: render, format: pdf }
      render_html: { type: render, format: html }
```

### 节点类型 [调整] 精简

| 类别 | 节点 | 说明 |
|------|------|------|
| **数据** | fetch / transform | 获取、处理数据 |
| **计算** | skill_invoke / mcp_call / ai_generate | 调用外部能力 |
| **设计** | layout / style | 文档编排 |
| **渲染** | to_pptx / to_docx / to_xlsx / to_pdf / to_html | 格式输出 |
| **控制** | condition / parallel / retry | 流程控制 |

---

## 七、动画引擎 [调整] 降为 P1

[调整] **动画引擎整体从核心架构中降级为 P1 特性。** 理由：
- 仅 PPTX 渲染器需要动画
- 动画是"锦上添花"，不影响文档内容正确性
- PPTX 动画 XML 极其复杂，先做内容正确，再做动画精美

### 缓动函数

| 类型 | 说明 |
|------|------|
| `linear` | 线性 |
| `ease_in` | 渐入 |
| `ease_out` | 渐出 |
| `spring(1, 0.5, 10)` | 物理弹簧 |
| `bounce` | 弹跳 |
| `elastic` | 弹性 |
| `back` | 回拉 |

### 预设动画效果

| 类别 | 效果 |
|------|------|
| **入场** | slide_up / slide_down / scale_in / rotate_in / flip_in / typewriter / morph |
| **退出** | fade_out / shrink_out / fly_out |
| **强调** | pulse / shake / glow_pulse / breathe / float |
| **路径** | arc / spiral / wave_path |

### 物理动画

- **弹簧**: `spring(target, stiffness=100, damping=10, mass=1)`
- **重力 + 弹跳**: `gravity(fall_height, bounce_count=3, decay=0.6)`
- **轨道运动**: `orbit(center, radius, speed=1)`

[优化] **动画→PPTX 映射约束（新增）：**

```python
# PPTX 动画模型的限制：
# 1. 不支持真正的物理弹簧 — 必须预计算为关键帧
# 2. 并行动画最多在同一元素上叠加 4 层
# 3. 路径动画在 PPTX 中是有限的自定义路径点集
# 4. 无限循环动画 (repeat: infinite) 在 PPTX 中为 repeatUntilNextClick

ANIMATION_FALLBACK = {
    "spring": "ease_out",           # 弹簧 → 渐出
    "bounce": "ease_out_bounce",    # Python 预计算关键帧后写入
    "orbit": "custom_path",         # 预计算为 PPTX 自定义路径
    "infinite": "until_next_click", # 无限循环 → 直到下次点击
}
```

---

## 八、艺术字 & 文本引擎 [调整] 降为 P1

### WordArt 变换

| 变形 | 说明 | PPTX 支持 | DOCX 支持 |
|------|------|-----------|-----------|
| arch / arch_up / arch_down | 弧形变形 | ✅ 原生 | ❌ 降级为普通文本 |
| wave / wave_double | 波浪 | ✅ 原生 | ❌ 降级 |
| inflate / deflate | 膨胀/收缩 | ✅ 原生 | ❌ 降级 |
| chevron | V 形 | ✅ 原生 | ❌ 降级 |
| circle / button / triangle | 几何变形 | ✅ 原生 | ❌ 降级 |

[优化] **新增渲染器能力声明 + 优雅降级：**

```python
class RendererCapability(Protocol):
    """每个渲染器必须声明自己支持的 IR 特性"""

    supported_node_types: set[NodeType]
    supported_layout_modes: set[str]        # {"absolute", "relative", "grid", ...}
    supported_text_transforms: set[str]     # {"arch", "wave", ...}
    supported_animations: set[str]          # {"slide_up", "fade_in", ...}
    supported_effects: set[str]             # {"shadow", "glow", "duotone", ...}

    def get_fallback(self, feature: str) -> str:
        """不支持的特性如何降级"""
        ...

# 示例：PPTX 渲染器能力
PPTX_CAPABILITY = RendererCapability(
    supported_node_types={TEXT, IMAGE, SHAPE, CHART, TABLE, GROUP, VIDEO},
    supported_text_transforms={"arch", "arch_up", "wave", "circle", ...},
    supported_animations={"slide_up", "fade_in", "scale_in", ...},
    supported_effects={"shadow", "glow", "gradient_fill"},
)

# 示例：DOCX 渲染器能力
DOCX_CAPABILITY = RendererCapability(
    supported_node_types={TEXT, IMAGE, TABLE},
    supported_text_transforms=set(),  # 不支持艺术字
    supported_animations=set(),       # 不支持动画
    supported_effects={"shadow"},     # 仅支持基础阴影
)
```

### 文本效果

- 渐变填充
- 描边（颜色/宽度/虚线）
- 阴影 / 发光 / 倒影
- 斜面浮雕
- 字距 / 词距
- 路径文字（沿曲线排列）— P2

---

## 九、AI 设计助手

### 意图解析

```
输入: "做一个科技感的季度汇报 PPT，深色主题，重点突出数据图表"
输出: DesignBrief(
    type="presentation",
    style="tech_dark",
    emphasis=["charts", "data_visualization"],
    mood=["professional", "modern", "data_driven"],
)
```

### 设计建议

- **自动布局**: 根据内容推荐最佳布局
- **配色方案**: 根据情绪/场景推荐配色
- **动画推荐**: 根据元素类型和上下文推荐动画 — P1
- **设计评审**: 对比度/对齐/层次/一致性自动检查

### 终极场景

```python
# 一句话生成完整季度汇报
deck = await office.create(
    description="Q4 季度汇报，科技感深色，突出营收增长",
    data="quarterly_report.xlsx",
    style="tech_dark",
    auto={
        "cover": "AI 生成封面",
        "charts": "自动生成图表",
        "insights": "AI 总结洞察",
        "icons": "AI 生成图标",
        "animations": "自动动画",         # P1
        "speaker_notes": "AI 生成演讲备注",
    }
)
```

---

## 十、主题系统

内置四大设计系统：

| 主题 | 来源 | 特点 |
|------|------|------|
| Material Design 3 | Google | Material You 动态配色 |
| Fluent Design | Microsoft | 桌面原生感 |
| Apple HIG | Apple | 简洁/排版/留白 |
| Tailwind | 社区 | 原子化 CSS 工具类 |

主题可继承、覆盖、混合，支持从种子色自动生成完整配色系统。

[优化] **P0 仅实现 Fluent（与 PPTX 生态最贴近）+ 一套通用主题。** Material/HIG/Tailwind 为 P1。

---

## 十一、前端：HTML 实时预览 [调整] 降为 P2

[调整] **实时预览从核心架构降为 P2。** 理由：
- 核心价值是"DSL 输入 → 文件输出"，不是"所见即所得编辑"
- WebSocket + 双向同步是独立的前端工程，工作量可匹敌后端
- P0 阶段用 "生成 → 打开文件验证" 即可

P2 再实现：
- DSL 修改 → 实时刷新
- 点击元素 → 高亮对应 DSL
- 拖拽元素 → 自动更新位置

---

## 十二、技术对比

| 维度 | python-pptx | pptxgenjs | 本方案 |
|------|-------------|-----------|--------|
| **定义方式** | 命令式代码 | 命令式代码 | 声明式 DSL + 代码 |
| **布局** | 绝对坐标 | 绝对坐标 | 约束求解 + 栅格 + Flex |
| **样式** | 手动设置 | 手动设置 | 级联 + 主题 + 令牌 |
| **动画** | 不支持 | 不支持 | 关键帧 + 物理弹簧 |
| **艺术字** | XML 注入 | 不支持 | 完整 WordArt + 路径文字 |
| **色彩** | HEX | HEX | OKLCH 感知均匀 |
| **资源来源** | 手动 | 手动 | MCP + Skill + AI + Web 统一中枢 |
| **数据绑定** | 无 | 无 | 变量 → 图表/表格 |
| **组件化** | 无 | 无 | 注册表 + 预设库 |
| **工作流** | 无 | 无 | DAG 编排 + 并行调度 |
| **AI 辅助** | 无 | 无 | 意图解析 + 设计建议 |
| **多格式** | 仅 PPTX | 仅 PPTX | PPTX/DOCX/XLSX/PDF/HTML |
| **预览** | 需打开 Office | 需打开 Office | 实时预览 (P2) |
| **降级策略** | 无 | 无 | 渲染器能力声明 + 优雅降级 |

---

## 十三、与现有 Skill 的关系

```
                    ┌──────────────────────────────┐
                    │     Office Suite 4.0          │
                    │  (Content Operating System)   │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
         ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
         │ 输入层   │         │ 处理层   │         │ 输出层   │
         └────┬────┘         └────┬────┘         └────┬────┘
              │                    │                    │
   ┌──────────┼──────────┐        │           ┌────────┼────────┐
   │          │          │        │           │        │        │
┌──▼──┐  ┌───▼───┐  ┌───▼──┐  ┌──▼──┐   ┌───▼──┐ ┌──▼──┐ ┌──▼──┐
│MCP  │  │Skills │  │AI Gen│  │Engine│   │.pptx │ │.docx│ │.pdf │
│     │  │       │  │      │  │     │   │      │ │     │ │     │
│搜索  │  │研究    │  │图片   │  │布局  │   │动画   │ │排版  │ │矢量  │
│图片  │  │分析    │  │视频   │  │样式  │   │艺术字 │ │表格  │ │精确  │
│视频  │  │可视化  │  │文案   │  │文本  │   │母版   │ │图表  │ │布局  │
│数据  │  │写作    │  │图表   │  │媒体  │   │切换   │ │引用  │ │      │
│代码  │  │代码    │  │3D    │  │数据  │   │      │ │      │ │      │
└─────┘  └───────┘  └──────┘  └─────┘   └──────┘ └─────┘ └─────┘
```

---

## 十四、实施路线 [优化] 重新规划

[优化] **核心调整：**
1. 时间估算从 16 天调整为 30 天，增加缓冲
2. 每个阶段有明确的验收标准
3. Phase 0 增加技术验证环节——先跑通最小闭环
4. 采用增量交付——每个 Phase 结束都能产出可用功能
5. 渲染器按优先级拆分——先 PPTX，后 DOCX/XLSX，再 PDF/HTML

| Phase | 内容 | 天数 | 验收标准 |
|-------|------|------|---------|
| **Phase 0** | 基础设施 + 技术验证 | 2 天 | ① YAML → IR 解析通过 ② IR → PPTX 渲染出"Hello World"页面 ③ 打开 PPTX 文件确认内容正确 |
| **Phase 1** | DSL + IR 核心 | 3 天 | ① DSL 包含/属性约束校验生效 ② 文本+图片+形状+表格 IR 节点完整 ③ position mm/% 映射到 EMU 正确 ④ 样式级联 3 层生效 |
| **Phase 2** | PPTX 渲染器（核心） | 5 天 | ① 母版布局渲染正确 ② 图表/表格数据绑定生效 ③ 渐变/阴影/主题色输出正确 ④ 附：IR→PPTX 映射测试 20+ 用例通过 |
| **Phase 3** | 资源中枢 + 基础流水线 | 3 天 | ① MCP 图片资源获取并嵌入 PPTX ② 本地文件资源解析 ③ 资源获取失败时降级到占位符 ④ 简单 DAG（3 节点串行）调度成功 |
| **Phase 4** | DOCX + XLSX 渲染器 | 4 天 | ① DOCX：标题/段落/表格/图片/样式级联 ② XLSX：Sheet/数据/图表/条件格式 ③ 各渲染器 capability 声明 + 降级路径 |
| **Phase 5** | AI 意图解析 + 设计建议 | 3 天 | ① 自然语言 → DesignBrief 解析 ② 自动布局推荐 ③ 配色方案推荐 ④ 对比度/对齐自动检查 |
| **Phase 6** | 主题 + 组件库 | 3 天 | ① Fluent 主题完整可用 ② 通用主题完整可用 ③ 内置 5+ 组件（图表/卡片/时间线/对比/信息图） ④ 组件注册/调用 |
| **Phase 7** | PDF + HTML 渲染器 | 3 天 | ① PDF：矢量文字+精确布局 ② HTML：CSS 渲染+预览可用 ③ 格式互转（PPTX→PDF / PPTX→HTML） |
| **Phase 8** | 动画 + 艺术字 | 4 天 | ① PPTX 入场/退出/强调动画渲染 ② WordArt 变换渲染 ③ 缓动函数→PPTX 关键帧映射 ④ 物理动画预计算 |
| **Phase 9** | 模板库 + 打磨 | 3 天 | ① 10+ 业务模板 ② 端到端测试覆盖 ③ 性能基准（100 页 PPTX <30s） |
| **总计** | | **~33 天** | |

[优化] **Phase 0 为什么增加技术验证：**

> 原方案最大的风险是"铺了很大的架构，但 DSL→渲染器的映射没跑通"。Phase 0 强制要求在写任何业务代码之前，先用硬编码的 IR 节点通过 PptxGenJS 生成一个能打开的 PPTX。如果这一步失败，说明技术选型或映射思路有问题，需要立即调整，而不是做到 Phase 4 才发现。

---

> **核心创新摘要**

> 1. **Design IR** — 统一的中间表示，解耦设计和渲染
> 2. **IR 包含约束** — [优化] 类型系统定义合法组合，渲染前校验
> 3. **IR→渲染器能力映射** — [优化] 每个渲染器声明支持能力，不支持的优雅降级
> 4. **资源中枢** — MCP + Skill + AI + Web 统一资源获取
> 5. **资源降级策略** — [优化] 获取失败时链式降级，不阻塞整体输出
> 6. **声明式 DSL** — YAML 定义文档，而非命令式代码
> 7. **DSL 特性分级** — [优化] P0/P1/P2/P3 优先级，MVP 只做 P0
> 8. **流水线 DAG** — 简化版工作流，去掉了不必要的运行时特性
> 9. **约束求解** — Cassowary 算法（P1）
> 10. **OKLCH 色彩** — 感知均匀色彩空间（P1），P0 先用 HEX
> 11. **物理动画** — 弹簧/重力/轨道（P1），预计算为关键帧
> 12. **AI 全流程** — 意图解析 → 设计建议 → 内容生成 → 质量评审
> 13. **多格式** — PPTX/DOCX/XLSX/PDF/HTML 统一 IR 渲染
> 14. **坐标映射规范** — [优化] position DSL → 各格式坐标的明确转换规则

---

> **v1 → v2 主要优化汇总**

| # | 优化项 | 问题 | 解决方案 |
|---|--------|------|---------|
| 1 | 时间估算 | 16 天严重低估 | 调整为 33 天，每阶段有验收标准 |
| 2 | Phase 0 技术验证 | 没有验证 DSL→渲染映射可行性 | 强制先跑通 "Hello World PPTX" |
| 3 | IR 包含约束 | 仅列枚举，无合法组合定义 | 新增 CONTAINMENT_RULES + REQUIRED_PROPS |
| 4 | 渲染器能力声明 | 无降级机制 | 新增 RendererCapability + fallback |
| 5 | DSL 特性分级 | 所有特性一视同仁 | P0/P1/P2/P3 分级，MVP 只做 P0 |
| 6 | 过度工程化 | 触发器/中间件/检查点/通知面板 | 删除，保留核心 DAG 调度 |
| 7 | 资源降级 | 获取失败无处理 | 新增 4 级降级链 |
| 8 | 坐标映射 | position 到 EMU 无规范 | 新增 mm/% → EMU/Twips 映射规则 |
| 9 | 动画→PPTX 映射 | 未说明物理动画如何转 PPTX | 新增 ANIMATION_FALLBACK 映射表 |
| 10 | OKLCH 时序 | MVP 阶段做色彩空间转换 | P0 用 HEX，P1 加 OKLCH 透明转换 |
| 11 | 预览优先级 | 列为核心功能 | 降为 P2 |
| 12 | 验收标准 | 无 | 每阶段增加明确验收标准 |
