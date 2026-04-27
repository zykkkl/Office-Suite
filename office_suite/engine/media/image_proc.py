"""图片处理引擎 — 缩放、裁剪、滤镜

设计方案第七章：媒体处理。

当前渲染器将图片作为文件路径透传，不做处理。
本模块提供图片操作能力：
  - 尺寸计算（保持宽高比缩放）
  - 装填模式（contain / cover / fill / fit）
  - 滤镜（亮度/对比度/灰度/模糊等）

注意：实际像素操作需要 Pillow，本模块优先提供
尺寸计算和参数生成，像素操作作为可选增强。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class FitMode(Enum):
    """装填模式"""
    CONTAIN = "contain"   # 保持比例，完全显示
    COVER = "cover"       # 保持比例，填满容器（裁剪溢出）
    FILL = "fill"         # 拉伸填满（不保持比例）
    FIT = "fit"           # 同 contain
    SCALE_DOWN = "scale-down"  # 取 contain 和原始尺寸中较小的


@dataclass(frozen=True)
class ImageSize:
    """图片尺寸"""
    width: float   # mm
    height: float  # mm


@dataclass(frozen=True)
class CropRegion:
    """裁剪区域"""
    x: float = 0.0       # 左上角 x (mm)
    y: float = 0.0       # 左上角 y (mm)
    width: float = 0.0   # 裁剪宽度 (mm)
    height: float = 0.0  # 裁剪高度 (mm)


@dataclass
class ImageFilters:
    """图片滤镜"""
    brightness: float = 1.0    # 0.0 - 2.0 (1.0 = 原始)
    contrast: float = 1.0      # 0.0 - 2.0
    saturate: float = 1.0      # 0.0 - 2.0
    grayscale: float = 0.0     # 0.0 - 1.0
    blur: float = 0.0          # 0 - 100 (px)
    opacity: float = 1.0       # 0.0 - 1.0
    hue_rotate: float = 0.0    # 0 - 360 (degrees)
    invert: float = 0.0        # 0.0 - 1.0
    sepia: float = 0.0         # 0.0 - 1.0


# ============================================================
# 尺寸计算
# ============================================================

def calculate_size(
    image_width: float,
    image_height: float,
    container_width: float,
    container_height: float,
    fit: FitMode = FitMode.CONTAIN,
) -> ImageSize:
    """计算图片在容器中的显示尺寸

    Args:
        image_width: 原始图片宽度（mm 或任意单位）
        image_height: 原始图片高度
        container_width: 容器宽度
        container_height: 容器高度
        fit: 装填模式

    Returns:
        显示尺寸
    """
    if image_width <= 0 or image_height <= 0:
        return ImageSize(width=container_width, height=container_height)

    aspect_ratio = image_width / image_height
    container_ratio = container_width / container_height

    if fit == FitMode.FILL:
        return ImageSize(width=container_width, height=container_height)

    if fit in (FitMode.CONTAIN, FitMode.FIT, FitMode.SCALE_DOWN):
        if aspect_ratio > container_ratio:
            # 图片更宽，以宽度为准
            w = container_width
            h = w / aspect_ratio
        else:
            # 图片更高，以高度为准
            h = container_height
            w = h * aspect_ratio

        if fit == FitMode.SCALE_DOWN:
            # 不超过原始尺寸
            w = min(w, image_width)
            h = min(h, image_height)

        return ImageSize(width=w, height=h)

    if fit == FitMode.COVER:
        if aspect_ratio < container_ratio:
            # 图片更宽（相对），以宽度为准
            w = container_width
            h = w / aspect_ratio
        else:
            h = container_height
            w = h * aspect_ratio
        return ImageSize(width=w, height=h)

    return ImageSize(width=container_width, height=container_height)


def calculate_crop(
    image_width: float,
    image_height: float,
    container_width: float,
    container_height: float,
) -> CropRegion:
    """计算 cover 模式下的裁剪区域（居中裁剪）

    Returns:
        裁剪区域（相对于原始图片坐标）
    """
    aspect = image_width / image_height
    container_aspect = container_width / container_height

    if aspect > container_aspect:
        # 图片更宽，裁剪左右
        new_width = image_height * container_aspect
        x = (image_width - new_width) / 2
        return CropRegion(x=x, y=0, width=new_width, height=image_height)
    else:
        # 图片更高，裁剪上下
        new_height = image_width / container_aspect
        y = (image_height - new_height) / 2
        return CropRegion(x=0, y=y, width=image_width, height=new_height)


# ============================================================
# CSS 滤镜生成
# ============================================================

def filters_to_css(filters: ImageFilters) -> str:
    """将滤镜转换为 CSS filter 字符串

    Args:
        filters: 滤镜参数

    Returns:
        CSS filter 值
    """
    parts = []
    if filters.brightness != 1.0:
        parts.append(f"brightness({filters.brightness})")
    if filters.contrast != 1.0:
        parts.append(f"contrast({filters.contrast})")
    if filters.saturate != 1.0:
        parts.append(f"saturate({filters.saturate})")
    if filters.grayscale > 0:
        parts.append(f"grayscale({filters.grayscale})")
    if filters.blur > 0:
        parts.append(f"blur({filters.blur}px)")
    if filters.hue_rotate != 0:
        parts.append(f"hue-rotate({filters.hue_rotate}deg)")
    if filters.invert > 0:
        parts.append(f"invert({filters.invert})")
    if filters.sepia > 0:
        parts.append(f"sepia({filters.sepia})")
    return " ".join(parts) if parts else "none"


# ============================================================
# PPTX 图片参数
# ============================================================

def to_pptx_crop(crop: CropRegion, image_width: float, image_height: float) -> dict[str, float]:
    """转换为 PPTX 裁剪参数（百分比）

    PPTX 使用百分比裁剪：0.0 = 未裁剪，正值 = 裁剪量

    Returns:
        dict with left, top, right, bottom (0.0 - 1.0)
    """
    if image_width <= 0 or image_height <= 0:
        return {"left": 0.0, "top": 0.0, "right": 0.0, "bottom": 0.0}

    return {
        "left": crop.x / image_width,
        "top": crop.y / image_height,
        "right": (image_width - crop.x - crop.width) / image_width,
        "bottom": (image_height - crop.y - crop.height) / image_height,
    }
