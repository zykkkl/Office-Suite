"""Phase 8 测试套件：动画 + 艺术字

验收标准：
1. 缓动函数正确性
2. 关键帧生成
3. 物理动画预计算
4. PPTX 动画渲染
5. WordArt 文本变换
6. DSL → IR 动画解析
7. 端到端 DSL → PPTX 含动画
"""

import zipfile

import pytest

from office_suite.ir.types import (
    IRAnimation, ENTRY_ANIMATIONS, EXIT_ANIMATIONS,
    EMPHASIS_ANIMATIONS, EASING_FUNCTIONS, ANIMATION_FALLBACK,
)
from office_suite.engine.style.animation import (
    linear, ease_in, ease_out, ease_in_out,
    ease_out_bounce, ease_out_elastic, ease_out_back,
    get_easing, generate_keyframes,
    spring_keyframes, gravity_keyframes, orbit_keyframes,
    parse_animation, Keyframe,
)
from office_suite.engine.text.shaping import (
    PPTX_TEXT_WARP_MAP, AVAILABLE_TRANSFORMS,
    get_supported_transforms, TextTransform,
)
from office_suite.ir.compiler import _parse_animations
from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.renderer.pptx.deck import PPTXRenderer


# ============================================================
# 缓动函数
# ============================================================

def test_easing_functions():
    # 边界条件
    assert linear(0) == 0, "linear(0) != 0"
    assert linear(1) == 1, "linear(1) != 1"
    assert ease_in(0) == 0, "ease_in(0) != 0"
    assert ease_in(1) == 1, "ease_in(1) != 1"
    assert ease_out(0) == 0, "ease_out(0) != 0"
    assert ease_out(1) == 1, "ease_out(1) != 1"
    assert ease_in_out(0) == 0, "ease_in_out(0) != 0"
    assert ease_in_out(1) == 1, "ease_in_out(1) != 1"

    # 单调性
    assert ease_in(0.5) > ease_in(0.3), "ease_in 不单调"
    assert ease_out(0.5) > ease_out(0.3), "ease_out 不单调"

    # bounce/elastic/back 边界
    assert ease_out_bounce(0) == 0
    assert ease_out_bounce(1) == 1
    assert ease_out_elastic(0) == 0
    assert ease_out_elastic(1) == 1
    assert ease_out_back(0) == 0
    assert ease_out_back(1) == 1


# ============================================================
# 关键帧生成
# ============================================================

def test_keyframe_generation():
    frames = generate_keyframes(easing="linear", steps=10)
    assert len(frames) == 11, f"10 步应生成 11 帧, got {len(frames)}"
    assert frames[0].time == 0
    assert frames[-1].time == 1.0

    # 带范围
    frames2 = generate_keyframes(
        easing="ease_out", steps=5,
        y_range=(-50, 0), opacity_range=(0, 1),
    )
    assert frames2[0].y_offset == -50
    assert frames2[-1].y_offset == 0
    assert frames2[0].opacity == 0


# ============================================================
# 物理动画
# ============================================================

def test_physical_animations():
    # 弹簧
    spring = spring_keyframes(target_x=20, target_y=0, steps=30)
    assert len(spring) > 0, "弹簧无帧"
    assert abs(spring[-1].x_offset - 20) < 1, "弹簧末帧未到目标"

    # 重力
    gravity = gravity_keyframes(fall_height=50, bounce_count=2, steps=30)
    assert len(gravity) > 0, "重力无帧"
    assert gravity[0].y_offset < 0, "重力首帧不在上方"

    # 轨道
    orbit = orbit_keyframes(radius=20, steps=20)
    assert len(orbit) > 0, "轨道无帧"
    assert abs(orbit[0].x_offset - 20) < 1, "轨道首帧 x!=20"


# ============================================================
# DSL 动画解析
# ============================================================

def test_dsl_animation_parse():
    # 单个动画
    raw1 = {"effect": "fade", "duration": 0.5}
    anims1 = _parse_animations(raw1)
    assert len(anims1) == 1, "单动画解析失败"
    assert anims1[0].effect == "fade"
    assert anims1[0].duration == 0.5

    # 多个动画
    raw2 = [
        {"effect": "fade_in", "trigger": "on_click"},
        {"effect": "pulse", "trigger": "after_previous"},
    ]
    anims2 = _parse_animations(raw2)
    assert len(anims2) == 2, "多动画解析失败"
    assert anims2[1].anim_type == "emphasis", "强调动画未识别"

    # 退出动画识别
    raw3 = {"effect": "fade_out"}
    anims3 = _parse_animations(raw3)
    assert anims3[0].anim_type == "exit", "退出动画未识别"

    # None 输入
    assert len(_parse_animations(None)) == 0, "None 应返回空"


# ============================================================
# IR 动画类型
# ============================================================

def test_ir_animation_types():
    assert len(ENTRY_ANIMATIONS) > 10, f"入场预设 {len(ENTRY_ANIMATIONS)} < 10"
    assert len(EXIT_ANIMATIONS) > 5, f"退出预设 {len(EXIT_ANIMATIONS)} < 5"
    assert len(EMPHASIS_ANIMATIONS) > 5, f"强调预设 {len(EMPHASIS_ANIMATIONS)} < 5"
    assert len(EASING_FUNCTIONS) > 5, f"缓动函数 {len(EASING_FUNCTIONS)} < 5"
    assert "spring" in ANIMATION_FALLBACK, "spring 降级缺失"
    assert ANIMATION_FALLBACK["spring"] == "ease_out"


# ============================================================
# WordArt 文本变换
# ============================================================

def test_wordart_transforms():
    assert "arch" in AVAILABLE_TRANSFORMS
    assert "wave" in AVAILABLE_TRANSFORMS
    assert "circle" in AVAILABLE_TRANSFORMS

    assert "arch" in get_supported_transforms("pptx")
    assert len(get_supported_transforms("docx")) == 0
    assert "arch" in get_supported_transforms("html")

    assert PPTX_TEXT_WARP_MAP["arch"] == "textArchDown"
    assert PPTX_TEXT_WARP_MAP["wave"] == "textWave1"


# ============================================================
# 端到端 DSL → PPTX 含动画
# ============================================================

def test_e2e_animation(tmp_path):
    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: text
        content: "带动画的标题"
        style: { font: { size: 32, weight: 700 } }
        position: { x: 20mm, y: 30mm, width: 200mm, height: 20mm }
        animation:
          effect: fade_in
          duration: 0.8
          trigger: on_click
          easing: ease_out
      - type: text
        content: "强调动画"
        style: { font: { size: 18 } }
        position: { x: 20mm, y: 60mm, width: 200mm, height: 15mm }
        animation:
          effect: pulse
          duration: 0.5
          trigger: after_previous
      - type: shape
        shape_type: rounded_rectangle
        content: "卡片"
        style: { fill: { color: "#EFF6FF" } }
        position: { x: 20mm, y: 90mm, width: 80mm, height: 30mm }
        animation:
          effect: slide_up
          duration: 0.6
          trigger: on_click
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    # 检查动画解析
    slide = ir.children[0]
    text_node = slide.children[0]
    assert len(text_node.animations) == 1, "文本无动画"
    assert text_node.animations[0].effect == "fade_in"
    assert text_node.animations[0].duration == 0.8

    pulse_node = slide.children[1]
    assert pulse_node.animations[0].anim_type == "emphasis"

    # 渲染 PPTX
    output = tmp_path / "phase8_animation.pptx"
    renderer = PPTXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists(), "PPTX 动画生成失败"
    assert out_path.stat().st_size > 10000, f"PPTX 太小: {out_path.stat().st_size}"


# ============================================================
# 端到端 DSL → PPTX 含 WordArt
# ============================================================

def test_e2e_wordart(tmp_path):
    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: text
        content: "弧形艺术字"
        style:
          font: { size: 36, weight: 700, color: "#2563EB" }
          text_effect: { transform: arch, bend: 30 }
        position: { x: 40mm, y: 40mm, width: 160mm, height: 80mm }
      - type: text
        content: "波浪文字"
        style:
          font: { size: 24, color: "#E11D48" }
          text_effect: { transform: wave }
        position: { x: 40mm, y: 130mm, width: 160mm, height: 40mm }
"""
    doc = parse_yaml_string(dsl)
    ir = compile_document(doc)

    slide = ir.children[0]
    text_node = slide.children[0]
    assert text_node.style.text_effect is not None, "text_effect 丢失"
    assert text_node.style.text_effect.get("transform") == "arch"

    output = tmp_path / "phase8_wordart.pptx"
    renderer = PPTXRenderer()
    out_path = renderer.render(ir, output)
    assert out_path.exists(), "PPTX WordArt 生成失败"


# ============================================================
# 路径文字测试
# ============================================================

def test_path_text_engine():
    from office_suite.engine.text.path_text import (
        generate_arc_points, generate_wave_points, parse_svg_path,
        layout_chars_on_path, to_pptx_placements, PathTextConfig,
    )

    # 弧线路径
    arc_pts = generate_arc_points(radius=50, start_angle=0, end_angle=180, num_points=20)
    assert len(arc_pts) == 20, f"弧线点数 {len(arc_pts)} != 20"
    assert abs(arc_pts[0].x - 50) < 1, "弧线首点 x!=50"
    assert abs(arc_pts[-1].x - (-50)) < 1, "弧线末点 x!=-50"

    # 波浪路径
    wave_pts = generate_wave_points(amplitude=10, wavelength=50, length=100, num_points=30)
    assert len(wave_pts) == 30, f"波浪点数 {len(wave_pts)} != 30"
    assert abs(wave_pts[0].x) < 0.1, "波浪首点 x!=0"
    assert abs(wave_pts[-1].x - 100) < 1, "波浪末点 x!=100"

    # 字符放置
    placements = layout_chars_on_path("Hello", arc_pts, font_size=14)
    assert len(placements) == 5, f"字符放置数 {len(placements)} != 5"
    assert placements[0].char == "H"

    # to_pptx_placements (arc)
    config = PathTextConfig(path_type="arc", radius=80, start_angle=10, end_angle=170)
    pptx_pl = to_pptx_placements("ArcText", config, font_size=18)
    assert len(pptx_pl) == 7, f"PPTX 弧线放置数 {len(pptx_pl)} != 7"

    # to_pptx_placements (wave)
    config_w = PathTextConfig(path_type="wave", amplitude=8, wavelength=40)
    pptx_wl = to_pptx_placements("WaveText", config_w, font_size=12)
    assert len(pptx_wl) == 8, f"PPTX 波浪放置数 {len(pptx_wl)} != 8"

    # to_pptx_placements (custom SVG path)
    config_svg = PathTextConfig(path_type="custom", custom_path="M 0 0 L 100 0")
    pptx_svg = to_pptx_placements("SVG", config_svg, font_size=14)
    assert len(pptx_svg) > 0, "自定义路径返回空"

    # 空文本
    empty = to_pptx_placements("", config, font_size=14)
    assert len(empty) == 0, "空文本应返回空列表"


def test_e2e_path_text(tmp_path):
    dsl = """
version: "4.0"
type: presentation
slides:
  - layout: blank
    elements:
      - type: text
        content: "弧形路径文字"
        path_text:
          path_type: arc
          radius: 80
          start_angle: 10
          end_angle: 170
        style:
          font: { size: 18, weight: 700, color: "#2563EB" }
        position: { x: 40mm, y: 40mm, width: 180mm, height: 100mm }
      - type: text
        content: "波浪文字"
        path_text:
          path_type: wave
          amplitude: 8
          wavelength: 40
        style:
          font: { size: 14, color: "#E11D48" }
        position: { x: 20mm, y: 100mm, width: 200mm, height: 30mm }
"""
    ir = parse_yaml_string(dsl)
    ir_doc = compile_document(ir)

    slide = ir_doc.children[0]
    assert len(slide.children) == 2, f"元素数 {len(slide.children)} != 2"

    text1 = slide.children[0]
    assert text1.path_text is not None, "path_text 为 None"
    assert text1.path_text.path_type == "arc", "path_type != arc"
    assert "path_text" not in text1.extra, "path_text 不应在 extra 中"

    output = tmp_path / "phase8_path_text.pptx"
    renderer = PPTXRenderer()
    out_path = renderer.render(ir_doc, output)
    assert out_path.exists(), "PPTX 路径文字生成失败"
    assert out_path.stat().st_size > 5000, f"PPTX 太小: {out_path.stat().st_size}"


@pytest.mark.xfail(reason="渲染器未对 IRPathText 生成 prstTxWarp，降级为普通文本框")
def test_preset_text_warp_path(tmp_path):
    """presetTextWarp 路径文字 — 标准路径用单 shape WordArt

    已知 bug: 渲染器未对 IRPathText 节点生成 prstTxWarp XML，
    而是降级为普通文本框。此测试标记为 xfail 直到渲染器修复。
    """
    from office_suite.ir.types import IRDocument, IRNode, IRPosition, IRStyle, NodeType, IRPathText

    preset_types = ["arc", "arch_up", "wave", "circle", "button", "chevron",
                    "slant_up", "slant_down", "triangle", "inflate", "deflate"]

    children = []
    for i, pt in enumerate(preset_types):
        children.append(IRNode(
            node_type=NodeType.TEXT,
            id=f"path_{pt}",
            content=f"Text on {pt}",
            position=IRPosition(x_mm=10, y_mm=10 + i * 15, width_mm=200, height_mm=14),
            path_text=IRPathText(path_type=pt, bend=60),
        ))

    slide = IRNode(node_type=NodeType.SLIDE, children=children)
    doc = IRDocument(children=[slide])

    out_path = tmp_path / "preset_warp.pptx"
    result = PPTXRenderer().render(doc, out_path)
    assert result.exists(), "presetTextWarp PPTX 生成失败"

    with zipfile.ZipFile(result) as zf:
        slide_xml = zf.read("ppt/slides/slide1.xml").decode("utf-8")
    assert "prstTxWarp" in slide_xml, "XML 缺 prstTxWarp"
    assert "textArchDown" in slide_xml, "XML 缺 textArchDown"
    assert "textWave1" in slide_xml, "XML 缺 textWave1"
    assert "textCircle" in slide_xml, "XML 缺 textCircle"
