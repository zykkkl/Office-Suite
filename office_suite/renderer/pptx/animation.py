"""PPTX 动画渲染 — IR IRAnimation → PPTX XML

python-pptx 不提供高级动画 API，需通过 Oxml 注入 XML。

PPTX 动画 XML 结构：
  <p:timing>
    <p:tnLst>
      <p:par>
        <p:cTn id="1" dur="indefinite" restart="never">
          <p:childTnLst>
            <p:seq concurrent="1" nextAc="seek">
              <p:cTn id="2" dur="indefinite">
                <p:childTnLst>
                  <p:par>
                    <p:cTn id="3" fill="hold">
                      <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                      <p:childTnLst>
                        <p:par>
                          <p:cTn id="4" fill="hold">
                            <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                            <p:childTnLst>
                              <p:set>...</p:set>  <!-- 入场 -->
                              <p:animEffect>...</p:animEffect>  <!-- 效果 -->
                            </p:childTnLst>
                          </p:cTn>
                        </p:par>
                      </p:childTnLst>
                    </p:cTn>
                  </p:par>
                </p:childTnLst>
              </p:cTn>
            </p:seq>
          </p:childTnLst>
        </p:cTn>
      </p:par>
    </p:tnLst>
  </p:timing>

简化实现：使用 Oxml 直接操作 slide XML。
"""

from lxml import etree

from ...ir.types import IRAnimation, ANIMATION_FALLBACK

# PPTX 动画效果名映射
# <a:animEffect transition="in" filter="..."> 或 <p:anim> 类型
EFFECT_MAP = {
    # 入场
    "fade": {"type": "animEffect", "filter": "fade"},
    "fade_in": {"type": "animEffect", "filter": "fade"},
    "slide_up": {"type": "animEffect", "filter": "wipe(tl)"},
    "slide_down": {"type": "animEffect", "filter": "wipe(br)"},
    "slide_left": {"type": "animEffect", "filter": "wipe(r)"},
    "slide_right": {"type": "animEffect", "filter": "wipe(l)"},
    "zoom_in": {"type": "animEffect", "filter": "zoomIn"},
    "zoom_out": {"type": "animEffect", "filter": "zoomOut"},
    "fly_in": {"type": "animEffect", "filter": "flyIn"},
    "wipe_up": {"type": "animEffect", "filter": "wipe(t)"},
    "wipe_down": {"type": "animEffect", "filter": "wipe(b)"},
    "wipe_left": {"type": "animEffect", "filter": "wipe(l)"},
    "wipe_right": {"type": "animEffect", "filter": "wipe(r)"},
    # 退出
    "fade_out": {"type": "animEffect", "filter": "fade", "transition": "out"},
    "slide_out_up": {"type": "animEffect", "filter": "wipe(tl)", "transition": "out"},
    "slide_out_down": {"type": "animEffect", "filter": "wipe(br)", "transition": "out"},
    # 强调
    "pulse": {"type": "animScale", "filter": "pulse"},
    "grow": {"type": "animScale", "filter": "grow"},
    "shrink": {"type": "animScale", "filter": "shrink"},
    "spin_emphasis": {"type": "animRot", "filter": "spin"},
}

# 缓动函数 → PPTX 加速/减速
EASING_PPTX = {
    "linear": {"accelerate": "0", "decelerate": "0"},
    "ease_in": {"accelerate": "100000", "decelerate": "0"},
    "ease_out": {"accelerate": "0", "decelerate": "100000"},
    "ease_in_out": {"accelerate": "50000", "decelerate": "50000"},
}

# 触发器映射
TRIGGER_MAP = {
    "on_click": "onClick",
    "with_previous": "withPrev",
    "after_previous": "afterPrev",
}


def apply_animations(slide, shape, animations: list[IRAnimation]):
    """将 IR 动画列表应用到 PPTX shape

    Args:
        slide: pptx Slide 对象
        shape: pptx Shape 对象
        animations: IR 动画列表
    """
    if not animations:
        return

    # 获取 slide XML 根元素
    slide_elem = slide._element

    # 确保有 timing 元素
    timing = slide_elem.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}timing')
    if timing is None:
        timing = etree.SubElement(slide_elem, '{http://schemas.openxmlformats.org/presentationml/2006/main}timing')

    # 获取或创建 tnLst
    p_ns = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    a_ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    r_ns = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

    nsmap = {'p': p_ns, 'a': a_ns, 'r': r_ns}

    # 简化实现：为每个动画创建一个 animEffect 节点
    # 实际 PPTX XML 更复杂，这里做基础实现
    for anim in animations:
        _add_animation_to_slide(slide, shape, anim, nsmap)


def _add_animation_to_slide(slide, shape, anim: IRAnimation, nsmap: dict):
    """添加单个动画到 slide XML

    简化实现：通过 python-pptx 的低级 API 注入。
    """
    p_ns = nsmap['p']
    a_ns = nsmap['a']

    # 获取 shape 的 spTree 索引（shape ID）
    shape_id = shape.shape_id

    # 动画效果映射
    effect_info = EFFECT_MAP.get(anim.effect)
    if effect_info is None:
        # 尝试降级
        fallback = ANIMATION_FALLBACK.get(anim.effect)
        if fallback:
            effect_info = EFFECT_MAP.get(fallback, EFFECT_MAP.get("fade"))
        else:
            effect_info = EFFECT_MAP.get("fade")

    # 构建简化的时间节点
    # 实际实现需要更完整的 XML 结构
    # 这里通过 slide 的 timing 元素添加基本动画

    slide_elem = slide._element
    timing = slide_elem.find(f'{{{p_ns}}}timing')
    if timing is None:
        timing = etree.SubElement(slide_elem, f'{{{p_ns}}}timing')

    # 获取或创建 tnLst
    tn_lst = timing.find(f'{{{p_ns}}}tnLst')
    if tn_lst is None:
        tn_lst = etree.SubElement(timing, f'{{{p_ns}}}tnLst')

    # 创建顶层 par 节点
    par = etree.SubElement(tn_lst, f'{{{p_ns}}}par')

    # cTn (container time node)
    ctn = etree.SubElement(par, f'{{{p_ns}}}cTn')
    ctn.set('id', '1')
    ctn.set('dur', 'indefinite')
    ctn.set('restart', 'never')

    # childTnLst
    child_tn_lst = etree.SubElement(ctn, f'{{{p_ns}}}childTnLst')

    # seq
    seq = etree.SubElement(child_tn_lst, f'{{{p_ns}}}seq')
    seq.set('concurrent', '1')
    seq.set('nextAc', 'seek')

    # seq child
    seq_ctn = etree.SubElement(seq, f'{{{p_ns}}}cTn')
    seq_ctn.set('id', '2')
    seq_ctn.set('dur', 'indefinite')

    seq_child = etree.SubElement(seq_ctn, f'{{{p_ns}}}childTnLst')

    # par for this animation
    anim_par = etree.SubElement(seq_child, f'{{{p_ns}}}par')

    anim_ctn = etree.SubElement(anim_par, f'{{{p_ns}}}cTn')
    anim_ctn.set('id', '3')
    anim_ctn.set('fill', 'hold')

    # start condition
    st_cond_lst = etree.SubElement(anim_ctn, f'{{{p_ns}}}stCondLst')
    cond = etree.SubElement(st_cond_lst, f'{{{p_ns}}}cond')
    delay_val = "0" if anim.trigger == "on_click" else str(int(anim.delay * 1000))
    cond.set('delay', delay_val)

    # inner child
    inner_child = etree.SubElement(anim_ctn, f'{{{p_ns}}}childTnLst')
    inner_par = etree.SubElement(inner_child, f'{{{p_ns}}}par')

    inner_ctn = etree.SubElement(inner_par, f'{{{p_ns}}}cTn')
    inner_ctn.set('id', '4')
    inner_ctn.set('fill', 'hold')

    inner_st = etree.SubElement(inner_ctn, f'{{{p_ns}}}stCondLst')
    inner_cond = etree.SubElement(inner_st, f'{{{p_ns}}}cond')
    inner_cond.set('delay', '0')

    final_child = etree.SubElement(inner_ctn, f'{{{p_ns}}}childTnLst')

    # 构建实际效果节点
    if anim.anim_type == "entry":
        _build_entry_effect(final_child, shape_id, anim, effect_info, p_ns, a_ns)
    elif anim.anim_type == "exit":
        _build_exit_effect(final_child, shape_id, anim, effect_info, p_ns, a_ns)
    elif anim.anim_type == "emphasis":
        _build_emphasis_effect(final_child, shape_id, anim, effect_info, p_ns, a_ns)


def _build_entry_effect(parent, shape_id: int, anim: IRAnimation, effect_info: dict, p_ns: str, a_ns: str):
    """构建入场效果 XML"""
    # set visibility
    set_elem = etree.SubElement(parent, f'{{{p_ns}}}set')

    set_cbn = etree.SubElement(set_elem, f'{{{p_ns}}}cBhvr')
    set_ctn = etree.SubElement(set_cbn, f'{{{p_ns}}}cTn')
    set_ctn.set('id', '5')
    set_ctn.set('dur', '1')
    set_ctn.set('fill', 'hold')

    set_tgt_el = etree.SubElement(set_cbn, f'{{{p_ns}}}tgtEl')
    set_sp_tgt = etree.SubElement(set_tgt_el, f'{{{p_ns}}}spTgt')
    set_sp_tgt.set('spid', str(shape_id))

    set_attr_name_l = etree.SubElement(set_cbn, f'{{{p_ns}}}attrNameLst')
    set_attr_name = etree.SubElement(set_attr_name_l, f'{{{p_ns}}}attrName')
    set_attr_name.text = 'style.visibility'

    set_to = etree.SubElement(set_elem, f'{{{p_ns}}}to')
    set_str = etree.SubElement(set_to, f'{{{p_ns}}}strVal')
    set_str.set('val', 'visible')

    # animEffect
    anim_effect = etree.SubElement(parent, f'{{{p_ns}}}animEffect')
    anim_effect.set('transition', effect_info.get('transition', 'in'))
    anim_effect.set('filter', effect_info.get('filter', 'fade'))

    # duration
    anim_effect_cbn = etree.SubElement(anim_effect, f'{{{p_ns}}}cBhvr')
    anim_effect_ctn = etree.SubElement(anim_effect_cbn, f'{{{p_ns}}}cTn')
    anim_effect_ctn.set('id', '6')
    dur_ms = int(anim.duration * 1000)
    anim_effect_ctn.set('dur', str(dur_ms))

    # target element
    tgt_el = etree.SubElement(anim_effect_cbn, f'{{{p_ns}}}tgtEl')
    sp_tgt = etree.SubElement(tgt_el, f'{{{p_ns}}}spTgt')
    sp_tgt.set('spid', str(shape_id))

    # easing (accelerate/decelerate)
    easing_info = EASING_PPTX.get(anim.easing, EASING_PPTX["ease_out"])
    if easing_info.get("accelerate", "0") != "0":
        anim_effect_ctn.set('accelerate', easing_info["accelerate"])
    if easing_info.get("decelerate", "0") != "0":
        anim_effect_ctn.set('decelerate', easing_info["decelerate"])


def _build_exit_effect(parent, shape_id: int, anim: IRAnimation, effect_info: dict, p_ns: str, a_ns: str):
    """构建退出效果 XML"""
    anim_effect = etree.SubElement(parent, f'{{{p_ns}}}animEffect')
    anim_effect.set('transition', 'out')
    anim_effect.set('filter', effect_info.get('filter', 'fade'))

    cbn = etree.SubElement(anim_effect, f'{{{p_ns}}}cBhvr')
    ctn = etree.SubElement(cbn, f'{{{p_ns}}}cTn')
    ctn.set('id', '7')
    ctn.set('dur', str(int(anim.duration * 1000)))

    tgt_el = etree.SubElement(cbn, f'{{{p_ns}}}tgtEl')
    sp_tgt = etree.SubElement(tgt_el, f'{{{p_ns}}}spTgt')
    sp_tgt.set('spid', str(shape_id))


def _build_emphasis_effect(parent, shape_id: int, anim: IRAnimation, effect_info: dict, p_ns: str, a_ns: str):
    """构建强调效果 XML"""
    anim_scale = etree.SubElement(parent, f'{{{p_ns}}}animScale')
    anim_scale.set('zoomContent', '0')

    cbn = etree.SubElement(anim_scale, f'{{{p_ns}}}cBhvr')
    ctn = etree.SubElement(cbn, f'{{{p_ns}}}cTn')
    ctn.set('id', '8')
    ctn.set('dur', str(int(anim.duration * 1000)))

    tgt_el = etree.SubElement(cbn, f'{{{p_ns}}}tgtEl')
    sp_tgt = etree.SubElement(tgt_el, f'{{{p_ns}}}spTgt')
    sp_tgt.set('spid', str(shape_id))

    # scale to
    to_elem = etree.SubElement(anim_scale, f'{{{p_ns}}}to')
    sx = etree.SubElement(to_elem, f'{{{p_ns}}}sx')
    sx.set('val', '110000')
    sy = etree.SubElement(to_elem, f'{{{p_ns}}}sy')
    sy.set('val', '110000')
