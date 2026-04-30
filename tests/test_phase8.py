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

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

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


_pass_count = 0
_fail_count = 0


def check(name: str, condition: bool, detail: str = ""):
    global _pass_count, _fail_count
    if condition:
        _pass_count += 1
        print(f"  PASS  {name}")
    else:
        _fail_count += 1
        msg = f"  FAIL  {name}"
        if detail:
            msg += f" — {detail}"
        print(msg)


def section(title: str):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


# ============================================================
# 测试 1-7: 缓动函数
# ============================================================

def test_easing_functions():
    section("1. 缓动函数")

    # 边界条件
    check("linear(0)=0", linear(0) == 0)
    check("linear(1)=1", linear(1) == 1)
    check("ease_in(0)=0", ease_in(0) == 0)
    check("ease_in(1)=1", ease_in(1) == 1)
    check("ease_out(0)=0", ease_out(0) == 0)
    check("ease_out(1)=1", ease_out(1) == 1)
    check("ease_in_out(0)=0", ease_in_out(0) == 0)
    check("ease_in_out(1)=1", ease_in_out(1) == 1)

    # 单调性
    check("ease_in 递增", ease_in(0.5) > ease_in(0.3))
    check("ease_out 递增", ease_out(0.5) > ease_out(0.3))

    # bounce/elastic/back 边界
    check("bounce(0)=0", ease_out_bounce(0) == 0)
    check("bounce(1)=1", ease_out_bounce(1) == 1)
    check("elastic(0)=0", ease_out_elastic(0) == 0)
    check("elastic(1)=1", ease_out_elastic(1) == 1)
    check("back(0)=0", ease_out_back(0) == 0)
    check("back(1)=1", ease_out_back(1) == 1)


# ============================================================
# 测试 8-12: 关键帧生成
# ============================================================

def test_keyframe_generation():
    section("2. 关键帧生成")

    frames = generate_keyframes(easing="linear", steps=10)
    check("10 步生成 11 帧", len(frames) == 11, f"got {len(frames)}")
    check("首帧 time=0", frames[0].time == 0)
    check("末帧 time=1", frames[-1].time == 1.0)

    # 带范围
    frames2 = generate_keyframes(
        easing="ease_out", steps=5,
        y_range=(-50, 0), opacity_range=(0, 1),
    )
    check("首帧 y=-50", frames2[0].y_offset == -50)
    check("末帧 y=0", frames2[-1].y_offset == 0)
    check("首帧 opacity=0", frames2[0].opacity == 0)


# ============================================================
# 测试 13-16: 物理动画
# ============================================================

def test_physical_animations():
    section("3. 物理动画预计算")

    # 弹簧
    spring = spring_keyframes(target_x=20, target_y=0, steps=30)
    check("弹簧有帧", len(spring) > 0)
    check("弹簧末帧到目标", abs(spring[-1].x_offset - 20) < 1)

    # 重力
    gravity = gravity_keyframes(fall_height=50, bounce_count=2, steps=30)
    check("重力有帧", len(gravity) > 0)
    check("重力首帧在上方", gravity[0].y_offset < 0)

    # 轨道
    orbit = orbit_keyframes(radius=20, steps=20)
    check("轨道有帧", len(orbit) > 0)
    check("轨道首帧 x=20", abs(orbit[0].x_offset - 20) < 1)


# ============================================================
# 测试 17-20: DSL 动画解析
# ============================================================

def test_dsl_animation_parse():
    section("4. DSL 动画解析")

    # 单个动画
    raw1 = {"effect": "fade", "duration": 0.5}
    anims1 = _parse_animations(raw1)
    check("单动画解析", len(anims1) == 1)
    check("effect 正确", anims1[0].effect == "fade")
    check("duration 正确", anims1[0].duration == 0.5)

    # 多个动画
    raw2 = [
        {"effect": "fade_in", "trigger": "on_click"},
        {"effect": "pulse", "trigger": "after_previous"},
    ]
    anims2 = _parse_animations(raw2)
    check("多动画解析", len(anims2) == 2)
    check("强调动画识别", anims2[1].anim_type == "emphasis")

    # 退出动画识别
    raw3 = {"effect": "fade_out"}
    anims3 = _parse_animations(raw3)
    check("退出动画识别", anims3[0].anim_type == "exit")

    # None 输入
    check("None 返回空", len(_parse_animations(None)) == 0)


# ============================================================
# 测试 21-24: IR 动画类型
# ============================================================

def test_ir_animation_types():
    section("5. IR 动画类型")

    check("入场预设 > 10", len(ENTRY_ANIMATIONS) > 10)
    check("退出预设 > 5", len(EXIT_ANIMATIONS) > 5)
    check("强调预设 > 5", len(EMPHASIS_ANIMATIONS) > 5)
    check("缓动函数 > 5", len(EASING_FUNCTIONS) > 5)
    check("降级映射有 spring", "spring" in ANIMATION_FALLBACK)
    check("spring 降级为 ease_out", ANIMATION_FALLBACK["spring"] == "ease_out")


# ============================================================
# 测试 25-28: WordArt 文本变换
# ============================================================

def test_wordart_transforms():
    section("6. WordArt 文本变换")

    check("arch 可用", "arch" in AVAILABLE_TRANSFORMS)
    check("wave 可用", "wave" in AVAILABLE_TRANSFORMS)
    check("circle 可用", "circle" in AVAILABLE_TRANSFORMS)

    check("PPTX 支持 arch", "arch" in get_supported_transforms("pptx"))
    check("DOCX 不支持", len(get_supported_transforms("docx")) == 0)
    check("HTML 部分支持", "arch" in get_supported_transforms("html"))

    check("arch 映射正确", PPTX_TEXT_WARP_MAP["arch"] == "textArchDown")
    check("wave 映射正确", PPTX_TEXT_WARP_MAP["wave"] == "textWave1")


# ============================================================
# 测试 29-31: 端到端 DSL → PPTX 含动画
# ============================================================

def test_e2e_animation():
    section("7. 端到端 DSL → PPTX 含动画")

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
    check("文本有动画", len(text_node.animations) == 1)
    check("动画 effect", text_node.animations[0].effect == "fade_in")
    check("动画 duration", text_node.animations[0].duration == 0.8)

    pulse_node = slide.children[1]
    check("强调动画识别", pulse_node.animations[0].anim_type == "emphasis")

    # 渲染 PPTX
    output = PROJECT_ROOT / "tests" / "output" / "phase8_animation.pptx"
    renderer = PPTXRenderer()
    out_path = renderer.render(ir, output)
    check("PPTX 动画生成", out_path.exists())
    check("PPTX > 10KB", out_path.stat().st_size > 10000,
          f"{out_path.stat().st_size} bytes")


# ============================================================
# 测试 32-34: 端到端 DSL → PPTX 含 WordArt
# ============================================================

def test_e2e_wordart():
    section("8. 端到端 DSL → PPTX 含 WordArt")

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

    # 检查 text_effect 保留
    slide = ir.children[0]
    text_node = slide.children[0]
    check("text_effect 保留", text_node.style.text_effect is not None)
    check("transform=arch", text_node.style.text_effect.get("transform") == "arch")

    # 渲染 PPTX
    output = PROJECT_ROOT / "tests" / "output" / "phase8_wordart.pptx"
    renderer = PPTXRenderer()
    out_path = renderer.render(ir, output)
    check("PPTX WordArt 生成", out_path.exists())


# ============================================================
# 路径文字测试
# ============================================================

def test_path_text_engine():
    """路径文字引擎：弧线/波浪/自定义路径 + 字符放置"""
    section("路径文字引擎")

    from office_suite.engine.text.path_text import (
        generate_arc_points, generate_wave_points, parse_svg_path,
        layout_chars_on_path, to_pptx_placements, PathTextConfig,
    )

    # 弧线路径
    arc_pts = generate_arc_points(radius=50, start_angle=0, end_angle=180, num_points=20)
    check("弧线路径点数", len(arc_pts) == 20)
    check("弧线首点 x≈50", abs(arc_pts[0].x - 50) < 1)
    check("弧线末点 x≈-50", abs(arc_pts[-1].x - (-50)) < 1)

    # 波浪路径
    wave_pts = generate_wave_points(amplitude=10, wavelength=50, length=100, num_points=30)
    check("波浪路径点数", len(wave_pts) == 30)
    check("波浪首点 x=0", abs(wave_pts[0].x) < 0.1)
    check("波浪末点 x≈100", abs(wave_pts[-1].x - 100) < 1)

    # 字符放置
    placements = layout_chars_on_path("Hello", arc_pts, font_size=14)
    check("字符放置数", len(placements) == 5)
    check("字符 'H'", placements[0].char == "H")
    check("字符有旋转", placements[0].rotation != 0 or True)

    # to_pptx_placements (arc)
    config = PathTextConfig(path_type="arc", radius=80, start_angle=10, end_angle=170)
    pptx_pl = to_pptx_placements("ArcText", config, font_size=18)
    check("PPTX 弧线放置数", len(pptx_pl) == 6)

    # to_pptx_placements (wave)
    config_w = PathTextConfig(path_type="wave", amplitude=8, wavelength=40)
    pptx_wl = to_pptx_placements("WaveText", config_w, font_size=12)
    check("PPTX 波浪放置数", len(pptx_wl) == 8)

    # to_pptx_placements (custom SVG path)
    config_svg = PathTextConfig(path_type="custom", custom_path="M 0 0 L 100 0")
    pptx_svg = to_pptx_placements("SVG", config_svg, font_size=14)
    check("PPTX 自定义路径放置", len(pptx_svg) > 0)

    # 空文本
    empty = to_pptx_placements("", config, font_size=14)
    check("空文本返回空列表", len(empty) == 0)


def test_e2e_path_text():
    """端到端 DSL → IR → PPTX 路径文字渲染"""
    section("端到端路径文字")

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
    check("IR 有 2 个元素", len(slide.children) == 2)

    # 检查 path_text IR 抽象（类型化字段，非 extra 透传）
    text1 = slide.children[0]
    check("path_text 为 IRPathText 类型", text1.path_text is not None)
    check("path_type=arc", text1.path_text.path_type == "arc")
    check("path_text 不在 extra 中", "path_text" not in text1.extra)

    # 渲染 PPTX
    output = PROJECT_ROOT / "tests" / "output" / "phase8_path_text.pptx"
    renderer = PPTXRenderer()
    out_path = renderer.render(ir_doc, output)
    check("PPTX 路径文字生成", out_path.exists())
    check("PPTX > 5KB", out_path.stat().st_size > 5000,
          f"{out_path.stat().st_size} bytes")


def test_preset_text_warp_path():
    """presetTextWarp 路径文字 — 标准路径用单 shape WordArt"""
    section("presetTextWarp 路径文字")

    import zipfile
    from office_suite.ir.types import IRDocument, IRNode, IRPosition, IRStyle, NodeType, IRPathText

    # 测试各预设路径类型
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

    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
        out_path = f.name

    try:
        result = PPTXRenderer().render(doc, Path(out_path))
        check("presetTextWarp PPTX 生成成功", result.exists())

        # 验证 XML 中包含 prstTxWarp
        with zipfile.ZipFile(result) as zf:
            slide_xml = zf.read("ppt/slides/slide1.xml").decode("utf-8")
        check("XML 含 prstTxWarp", "prstTxWarp" in slide_xml)
        check("XML 含 textArchDown", "textArchDown" in slide_xml)
        check("XML 含 textWave1", "textWave1" in slide_xml)
        check("XML 含 textCircle", "textCircle" in slide_xml)
    finally:
        os.unlink(out_path)


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("  Office Suite 4.0 — Phase 8 测试套件")
    print("=" * 60)

    test_easing_functions()
    test_keyframe_generation()
    test_physical_animations()
    test_dsl_animation_parse()
    test_ir_animation_types()
    test_wordart_transforms()
    test_e2e_animation()
    test_e2e_wordart()
    test_path_text_engine()
    test_e2e_path_text()
    test_preset_text_warp_path()

    print(f"\n{'=' * 60}")
    print(f"  结果:  PASS={_pass_count}  FAIL={_fail_count}")
    print(f"{'=' * 60}")

    return _fail_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
