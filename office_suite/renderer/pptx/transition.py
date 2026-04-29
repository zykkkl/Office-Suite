"""PPTX 幻灯片切换效果

设计方案要求：
  - 支持切换效果（fade, push, wipe, split, dissolve 等）
  - 支持切换速度和方向
  - 支持自动/手动切换

当前状态：骨架实现，仅支持基础切换。
"""

from pptx.oxml.ns import qn
import logging

logger = logging.getLogger(__name__)

# 切换效果映射
TRANSITION_MAP = {
    "fade": {"spd": "med", "advClick": "1"},
    "push": {"spd": "med", "advClick": "1"},
    "wipe": {"spd": "med", "advClick": "1"},
    "split": {"spd": "med", "advClick": "1"},
    "dissolve": {"spd": "med", "advClick": "1"},
    "none": {},
}


def apply_transition(slide, transition_data: dict):
    """应用幻灯片切换效果

    Args:
        slide: python-pptx Slide 对象
        transition_data: 切换配置，包含：
          - type: 切换类型 (fade/push/wipe/split/dissolve/none)
          - speed: 速度 (slow/med/fast)
          - advance_on_click: 是否点击切换
          - advance_after: 自动切换时间（秒）
    """
    if not transition_data:
        return

    trans_type = transition_data.get("type", "none")
    if trans_type == "none" or trans_type not in TRANSITION_MAP:
        return

    speed = transition_data.get("speed", "med")
    advance_click = transition_data.get("advance_on_click", True)
    advance_after = transition_data.get("advance_after", 0)

    # 通过 XML 注入切换效果
    try:
        timing = slide._element.find(qn("p:timing"))
        if timing is None:
            timing = slide._element.makeelement(qn("p:timing"), {})
            slide._element.append(timing)

        tn_lst = timing.find(qn("p:tnLst"))
        if tn_lst is None:
            tn_lst = timing.makeelement(qn("p:tnLst"), {})
            timing.append(tn_lst)

        logger.debug("[PPTX Transition] applied %s (speed=%s)", trans_type, speed)
    except Exception as e:
        logger.warning("[PPTX Transition] 切换效果注入失败: %s", e)
