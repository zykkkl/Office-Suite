"""DSL → IR 编译器 — 将 DSL Document 编译为 IRDocument

核心职责：
1. 将 DSL 文档类型安全地转换为 IR 节点树
2. 解析坐标（mm/% → mm 绝对值）
3. 样式级联（theme → document → slide → element → inline）
4. 保留原始 DSL 路径用于调试

数据流：
  YAML 文件 → dsl/parser.py::parse_yaml() → Document 对象
  Document  → [本文件]::compile_document() → IRDocument 树
  IRDocument → renderer/pptx/deck.py::PPTXRenderer.render() → .pptx 文件

坐标映射规则（设计方案第四章）：
  mm  → PPTX: × 36000 (EMU)    DOCX: × 1440 (Twips)    PDF: 直接使用
  %   → 相对于父容器尺寸计算后再走 mm 映射
  auto → 渲染器自行计算（文本根据字号+换行，图片根据原始比例）
  center → (parent_width - self_width) / 2
"""

from typing import Any

from ..dsl.parser import parse_style
from ..dsl.schema import (
    Document,
    Element,
    PositionSpec,
    Slide,
    StyleSpec,
)
from .cascade import cascade_style, cascade_style_by_name, DEFAULT_THEME_STYLES
from .types import (
    IRAnimation,
    IRDocument,
    IRNode,
    IRPosition,
    IRStyle,
    NodeType,
)


# ============================================================
# 坐标转换
# ============================================================

def _parse_length(value: str | float | None, parent_size: float = 0) -> tuple[float, bool, bool]:
    """解析长度值，返回 (mm值, is_relative, is_auto)"""
    if value is None:
        return 0.0, False, False
    if isinstance(value, (int, float)):
        return float(value), False, False
    if value == "auto":
        return 0.0, False, True
    if value == "center":
        return 0.0, False, False  # center 由 position.center 标记处理

    s = str(value).strip()
    if s.endswith("mm"):
        return float(s[:-2]), False, False
    if s.endswith("%"):
        pct = float(s[:-1]) / 100.0
        return parent_size * pct, True, False
    if s.endswith("in"):
        # 英寸 → mm (1 in = 25.4 mm)
        return float(s[:-2]) * 25.4, False, False
    if s.endswith("pt"):
        # pt → mm (1 pt = 0.3528 mm)
        return float(s[:-2]) * 0.3528, False, False
    # 默认当作 mm
    try:
        return float(s), False, False
    except ValueError:
        return 0.0, False, False


def compile_position(pos: PositionSpec | None, parent_w: float = 254.0, parent_h: float = 142.875) -> IRPosition:
    """将 DSL PositionSpec 编译为 IRPosition（mm 单位）

    默认父容器尺寸：标准 16:9 幻灯片 = 254mm x 142.875mm (10" x 5.625")
    注意：190.5mm 是 4:3 幻灯片高度（7.5"），16:9 正确高度是 142.875mm（5.625"）
    """
    if pos is None:
        return IRPosition()

    x, _, _ = _parse_length(pos.x, parent_w)
    y, _, _ = _parse_length(pos.y, parent_h)
    w, w_rel, w_auto = _parse_length(pos.width, parent_w)
    h, h_rel, h_auto = _parse_length(pos.height, parent_h)

    # bottom 定位：从底部向上计算
    if pos.bottom is not None:
        bottom_mm, _, _ = _parse_length(pos.bottom, parent_h)
        y = parent_h - bottom_mm - h

    return IRPosition(
        x_mm=x,
        y_mm=y,
        width_mm=w,
        height_mm=h,
        is_relative=w_rel or h_rel,
        is_center=pos.center,
        is_auto=w_auto or h_auto,
    )


# ============================================================
# 样式编译
# ============================================================

def compile_style(style: StyleSpec | None) -> IRStyle | None:
    """将 DSL StyleSpec 编译为 IRStyle"""
    if style is None:
        return None

    ir = IRStyle()
    if style.font:
        ir.font_family = style.font.family
        ir.font_size = style.font.size
        ir.font_weight = style.font.weight
        ir.font_italic = style.font.italic
        ir.font_color = style.font.color
    if style.fill:
        ir.fill_color = style.fill.color
        ir.fill_gradient = _gradient_to_dict(style.fill.gradient) if style.fill.gradient else None
        ir.fill_opacity = style.fill.opacity
    if style.shadow:
        ir.shadow = {
            "blur": style.shadow.blur,
            "offset": style.shadow.offset,
            "color": style.shadow.color,
        }
    if style.border:
        ir.border = style.border
    if style.text_effect:
        ir.text_effect = style.text_effect
    return ir


def _gradient_to_dict(grad) -> dict[str, Any]:
    return {
        "type": grad.type,
        "angle": grad.angle,
        "stops": grad.stops,
    }


# ============================================================
# 元素编译
# ============================================================

def _parse_animations(raw: dict | None) -> list[IRAnimation]:
    """将 DSL animation 字典解析为 IRAnimation 列表

    支持格式：
      animation: { effect: fade, duration: 0.5 }
      animation:
        - { effect: fade_in, trigger: on_click }
        - { effect: pulse, trigger: after_previous }
    """
    if not raw:
        return []

    # 支持单个动画 dict 或列表
    items = raw if isinstance(raw, list) else [raw]

    animations = []
    for item in items:
        if not isinstance(item, dict):
            continue

        # 动画类型推断
        anim_type = item.get("type", "entry")
        effect = item.get("effect", item.get("animation", "fade"))

        # 强调动画自动设置 anim_type
        emphasis_effects = {"pulse", "shake", "glow_pulse", "breathe", "float",
                            "spin_emphasis", "grow", "shrink"}
        if effect in emphasis_effects:
            anim_type = "emphasis"

        # 退出动画
        exit_effects = {"fade_out", "slide_out_up", "slide_out_down", "slide_out_left",
                        "slide_out_right", "zoom_out_exit"}
        if effect in exit_effects:
            anim_type = "exit"

        animations.append(IRAnimation(
            anim_type=anim_type,
            effect=effect,
            trigger=item.get("trigger", "on_click"),
            duration=item.get("duration", 0.5),
            delay=item.get("delay", 0.0),
            easing=item.get("easing", "ease_out"),
            repeat=item.get("repeat", 0),
            direction=item.get("direction", ""),
            extra={k: v for k, v in item.items()
                   if k not in ("type", "effect", "animation", "trigger",
                                "duration", "delay", "easing", "repeat", "direction")},
        ))

    return animations


# DSL type → IR NodeType 映射
TYPE_MAP = {
    "text": NodeType.TEXT,
    "image": NodeType.IMAGE,
    "shape": NodeType.SHAPE,
    "table": NodeType.TABLE,
    "chart": NodeType.CHART,
    "group": NodeType.GROUP,
    "video": NodeType.VIDEO,
    "audio": NodeType.AUDIO,
    "diagram": NodeType.DIAGRAM,
    "code": NodeType.CODE,
}


def compile_element(
    elem: Element,
    global_styles: dict[str, StyleSpec],
    doc_styles: dict[str, IRStyle],  # 已编译的 IR 全局样式
    theme_name: str = "default",
    parent_w: float = 254.0,
    parent_h: float = 142.875,
    path: str = "",
) -> IRNode:
    """将 DSL Element 编译为 IRNode

    样式级联：theme → doc_global → element_style_ref → element_inline
    """
    node_type = TYPE_MAP.get(elem.type, NodeType.SHAPE)

    # 样式：支持字符串引用或内联（dict 或 StyleSpec）
    style_ref = None
    inline_style = None

    if isinstance(elem.style, str):
        style_ref = elem.style
    elif isinstance(elem.style, dict):
        # 原始 YAML dict → StyleSpec → IRStyle
        parsed = parse_style(elem.style)
        if parsed:
            inline_style = compile_style(parsed)
    elif isinstance(elem.style, StyleSpec):
        inline_style = compile_style(elem.style)

    # 样式级联
    theme_styles = DEFAULT_THEME_STYLES  # P0 使用内置主题
    cascaded_style = cascade_style_by_name(
        style_name=style_ref,
        theme_styles=theme_styles,
        doc_styles=doc_styles,
        slide_style=None,  # slide 级样式在后续迭代添加
        element_style=inline_style,
    )

    # 位置
    ir_pos = compile_position(elem.position, parent_w, parent_h)

    # 处理 size 字段覆盖 position 的宽高
    if elem.size:
        w_raw = elem.size.get("width")
        h_raw = elem.size.get("height")
        if w_raw is not None:
            w_mm, _, _ = _parse_length(w_raw, parent_w)
            ir_pos.width_mm = w_mm
        if h_raw is not None:
            h_mm, _, _ = _parse_length(h_raw, parent_h)
            ir_pos.height_mm = h_mm

    # 图片 source 处理
    source = elem.source
    if isinstance(source, dict):
        source = source  # 保留 dict 形式

    # 子节点
    children = []
    for i, child in enumerate(elem.children):
        child_path = f"{path}/{child.type}[{i}]"
        children.append(compile_element(
            child, global_styles, doc_styles, theme_name,
            ir_pos.width_mm or parent_w, ir_pos.height_mm or parent_h, child_path,
        ))

    # 动画
    animations = _parse_animations(elem.animation)

    return IRNode(
        node_type=node_type,
        id=elem.extra.get("id", ""),
        content=elem.content,
        source=source,
        position=ir_pos,
        style=cascaded_style,
        style_ref=style_ref,
        children=children,
        data_ref=elem.data_ref,
        chart_type=elem.chart_type,
        animations=animations,
        extra={k: v for k, v in elem.extra.items() if k != "id"},
        source_path=path,
    )


# ============================================================
# 幻灯片编译
# ============================================================

def compile_slide(
    slide: Slide,
    global_styles: dict[str, StyleSpec],
    doc_ir_styles: dict[str, IRStyle],
    theme_name: str,
    index: int,
) -> IRNode:
    """将 DSL Slide 编译为 IRNode (NodeType.SLIDE)"""
    children = []
    for i, elem in enumerate(slide.elements):
        ir_elem = compile_element(
            elem, global_styles, doc_ir_styles, theme_name,
            path=f"slide[{index}]/{elem.type}[{i}]",
        )
        children.append(ir_elem)

    extra = {}
    if slide.background:
        extra["background"] = slide.background
    if slide.transition:
        extra["transition"] = slide.transition

    return IRNode(
        node_type=NodeType.SLIDE,
        content=None,
        position=IRPosition(x_mm=0, y_mm=0, width_mm=254, height_mm=142.875),
        children=children,
        extra=extra,
        source_path=f"slide[{index}]",
    )


# ============================================================
# 文档编译（入口）
# ============================================================

def compile_document(doc: Document) -> IRDocument:
    """将 DSL Document 编译为 IRDocument"""
    # 编译全局样式 → IR 样式表
    doc_ir_styles = {}
    for name, style_spec in doc.styles.items():
        doc_ir_styles[name] = compile_style(style_spec) or IRStyle()

    # 编译幻灯片
    slides = []
    for i, slide in enumerate(doc.slides):
        slides.append(compile_slide(slide, doc.styles, doc_ir_styles, doc.theme, i))

    return IRDocument(
        version=doc.version,
        doc_type=doc.type.value,
        theme=doc.theme,
        title=doc.title,
        styles=doc_ir_styles,
        data={k: v for k, v in doc.data.items()},
        children=slides,
        raw_dsl=doc.raw,
    )
