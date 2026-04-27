"""文本塑形 — WordArt 变换 + 路径文字

设计方案第八章：艺术字 & 文本引擎。

WordArt 变换：
  - arch / arch_up: 弧形文字
  - wave: 波浪文字
  - circle: 环形文字
  - slant_up / slant_down: 倾斜文字
  - triangle: 三角形文字

PPTX 实现方式：
  python-pptx 不直接支持 WordArt，
  通过 Oxml 注入 <a:bodyPr> 的 presetTextWarp 属性实现。

其他渲染器：
  - DOCX: 降级为普通文本
  - HTML: 用 CSS transform 模拟
  - PDF: 降级为普通文本
"""

from dataclasses import dataclass
from typing import Any

from ...ir.types import IRStyle


# PPTX presetTextWarp 映射
# <a:prstTxWarp prst="...">
PPTX_TEXT_WARP_MAP = {
    "arch": "textArchDown",
    "arch_up": "textArchUp",
    "wave": "textWave1",
    "wave_2": "textWave2",
    "circle": "textCircle",
    "slant_up": "textSlantUp",
    "slant_down": "textSlantDown",
    "triangle": "textTriangle",
    "chevron_up": "textChevronUp",
    "chevron_down": "textChevronDown",
    "button": "textButton",
    "deflate": "textDeflate",
    "inflate": "textInflate",
    "fade_up": "textFadeUp",
    "fade_down": "textFadeDown",
    "plain": "textPlain",
}

# 降级映射: 不支持的变换 → 最接近的可用变换
TRANSFORM_FALLBACK = {
    "arch": "plain_text",
    "arch_up": "plain_text",
    "wave": "plain_text",
    "circle": "plain_text",
    "slant_up": "plain_text",
    "slant_down": "plain_text",
}

# 可用的变换集合
AVAILABLE_TRANSFORMS = set(PPTX_TEXT_WARP_MAP.keys())


@dataclass
class TextTransform:
    """文本变换参数"""
    transform_type: str = "plain"   # 变换类型
    # 弧形参数
    bend: float = 0.0              # 弯曲程度 (-100 ~ 100)
    # 自适应
    auto_size: str = "none"        # none / shape_to_fit / shrink_to_fit
    # 旋转
    rotation: float = 0.0          # 文本框旋转角度


def apply_text_transform(style: IRStyle, transform: TextTransform) -> dict[str, Any]:
    """将文本变换应用到样式

    Args:
        style: 原始样式
        transform: 变换参数

    Returns:
        包含变换信息的 dict，渲染器使用
    """
    warp_preset = PPTX_TEXT_WARP_MAP.get(transform.transform_type, "textPlain")

    return {
        "text_warp": warp_preset,
        "bend": transform.bend,
        "auto_size": transform.auto_size,
        "rotation": transform.rotation,
    }


def get_supported_transforms(renderer_type: str) -> set[str]:
    """获取某渲染器支持的文本变换

    Args:
        renderer_type: 渲染器类型 (pptx/docx/xlsx/pdf/html)

    Returns:
        支持的变换名集合
    """
    if renderer_type == "pptx":
        return AVAILABLE_TRANSFORMS
    elif renderer_type == "html":
        return {"arch", "wave", "slant_up", "slant_down"}
    else:
        return set()  # 其他渲染器不支持
