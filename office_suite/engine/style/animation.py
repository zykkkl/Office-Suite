"""动画引擎 — 缓动函数 + 关键帧预计算

设计方案第七章：动画引擎。

缓动函数：
  将 t ∈ [0,1] 映射到动画进度值。
  PPTX 不支持原生物理动画，需预计算为关键帧序列。

关键帧预计算：
  物理动画（弹簧/重力/轨道）→ 离散关键帧 → PPTX 自定义路径

本模块提供：
  1. 缓动函数集合
  2. 关键帧生成器
  3. 物理模拟器
  4. DSL 动画 → IR IRAnimation 转换
"""

import math
from dataclasses import dataclass, field
from typing import Callable

from ...ir.types import IRAnimation


# ============================================================
# 缓动函数
# ============================================================

def linear(t: float) -> float:
    """线性"""
    return t


def ease_in(t: float) -> float:
    """加速 (二次)"""
    return t * t


def ease_out(t: float) -> float:
    """减速 (二次)"""
    return 1 - (1 - t) ** 2


def ease_in_out(t: float) -> float:
    """先加速后减速 (二次)"""
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2


def ease_out_bounce(t: float) -> float:
    """弹跳减速"""
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def ease_out_elastic(t: float) -> float:
    """弹性减速"""
    if t == 0 or t == 1:
        return t
    p = 0.3
    return math.pow(2, -10 * t) * math.sin((t - p / 4) * (2 * math.pi) / p) + 1


def ease_out_back(t: float) -> float:
    """回拉减速"""
    if t == 0:
        return 0.0
    if t == 1:
        return 1.0
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


EASING_MAP: dict[str, Callable[[float], float]] = {
    "linear": linear,
    "ease_in": ease_in,
    "ease_out": ease_out,
    "ease_in_out": ease_in_out,
    "bounce": ease_out_bounce,
    "elastic": ease_out_elastic,
    "back": ease_out_back,
}


def get_easing(name: str) -> Callable[[float], float]:
    """获取缓动函数"""
    return EASING_MAP.get(name, ease_out)


# ============================================================
# 关键帧
# ============================================================

@dataclass
class Keyframe:
    """单个关键帧"""
    time: float          # 0.0 ~ 1.0
    x_offset: float = 0.0  # 水平偏移 (mm)
    y_offset: float = 0.0  # 垂直偏移 (mm)
    scale: float = 1.0     # 缩放
    rotation: float = 0.0  # 旋转角度
    opacity: float = 1.0   # 不透明度


def generate_keyframes(
    easing: str = "ease_out",
    steps: int = 10,
    x_range: tuple[float, float] = (0, 0),
    y_range: tuple[float, float] = (0, 0),
    scale_range: tuple[float, float] = (1, 1),
    rotation_range: tuple[float, float] = (0, 0),
    opacity_range: tuple[float, float] = (1, 1),
) -> list[Keyframe]:
    """生成关键帧序列

    Args:
        easing: 缓动函数名
        steps: 关键帧数
        x_range: 水平偏移范围 (start, end) mm
        y_range: 垂直偏移范围 (start, end) mm
        scale_range: 缩放范围
        rotation_range: 旋转范围
        opacity_range: 不透明度范围

    Returns:
        关键帧列表
    """
    easing_fn = get_easing(easing)
    frames = []

    for i in range(steps + 1):
        t = i / steps if steps > 0 else 1.0
        progress = easing_fn(t)

        frame = Keyframe(
            time=t,
            x_offset=x_range[0] + (x_range[1] - x_range[0]) * progress,
            y_offset=y_range[0] + (y_range[1] - y_range[0]) * progress,
            scale=scale_range[0] + (scale_range[1] - scale_range[0]) * progress,
            rotation=rotation_range[0] + (rotation_range[1] - rotation_range[0]) * progress,
            opacity=opacity_range[0] + (opacity_range[1] - opacity_range[0]) * progress,
        )
        frames.append(frame)

    return frames


# ============================================================
# 物理动画
# ============================================================

def spring_keyframes(
    target_x: float = 0,
    target_y: float = 0,
    stiffness: float = 100,
    damping: float = 10,
    mass: float = 1.0,
    steps: int = 30,
    dt: float = 0.016,
) -> list[Keyframe]:
    """弹簧动画预计算

    模拟弹簧从 (0,0) 运动到 (target_x, target_y)。
    PPTX 不支持原生弹簧，需预计算为关键帧。

    Args:
        target_x: 目标 x 偏移 (mm)
        target_y: 目标 y 偏移 (mm)
        stiffness: 刚度
        damping: 阻尼
        mass: 质量
        steps: 总步数
        dt: 时间步长

    Returns:
        关键帧列表
    """
    x, y = 0.0, 0.0
    vx, vy = 0.0, 0.0
    frames = []

    for i in range(steps):
        # 弹簧力 F = -k * (x - target) - damping * v
        fx = -stiffness * (x - target_x) - damping * vx
        fy = -stiffness * (y - target_y) - damping * vy

        # 加速度 a = F / m
        ax = fx / mass
        ay = fy / mass

        # 更新速度和位置
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt

        t = i / (steps - 1) if steps > 1 else 1.0
        frames.append(Keyframe(time=t, x_offset=x, y_offset=y))

    # 确保最后一帧到达目标
    frames.append(Keyframe(time=1.0, x_offset=target_x, y_offset=target_y))
    return frames


def gravity_keyframes(
    fall_height: float = 50,
    bounce_count: int = 3,
    decay: float = 0.6,
    steps: int = 40,
) -> list[Keyframe]:
    """重力 + 弹跳动画预计算

    从上方下落并在底部弹跳逐渐衰减。

    Args:
        fall_height: 下落高度 (mm)
        bounce_count: 弹跳次数
        decay: 每次弹跳衰减比例
        steps: 总步数

    Returns:
        关键帧列表
    """
    frames = []
    current_height = -fall_height  # 从上方开始
    velocity = 0.0
    gravity = 2 * fall_height  # 加速度
    time_step = 1.0 / steps

    for i in range(steps + 1):
        t = i / steps
        frame = Keyframe(time=t, y_offset=current_height)
        frames.append(frame)

        velocity += gravity * time_step
        current_height += velocity * time_step

        # 触底弹跳
        if current_height >= 0 and velocity > 0:
            current_height = 0
            velocity = -velocity * decay

    return frames


def orbit_keyframes(
    center_x: float = 0,
    center_y: float = 0,
    radius: float = 20,
    steps: int = 20,
) -> list[Keyframe]:
    """轨道运动预计算

    围绕中心点做圆形运动。

    Args:
        center_x: 中心 x 偏移 (mm)
        center_y: 中心 y 偏移 (mm)
        radius: 轨道半径 (mm)
        steps: 总步数

    Returns:
        关键帧列表
    """
    frames = []
    for i in range(steps + 1):
        t = i / steps
        angle = 2 * math.pi * t
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        frames.append(Keyframe(time=t, x_offset=x, y_offset=y))
    return frames


# ============================================================
# DSL 动画 → IR 转换
# ============================================================

def parse_animation(raw: dict) -> IRAnimation:
    """将 DSL 动画字典转换为 IRAnimation

    Args:
        raw: DSL 动画字典

    Returns:
        IRAnimation 实例
    """
    return IRAnimation(
        anim_type=raw.get("type", "entry"),
        effect=raw.get("effect", raw.get("animation", "fade")),
        trigger=raw.get("trigger", "on_click"),
        duration=raw.get("duration", 0.5),
        delay=raw.get("delay", 0.0),
        easing=raw.get("easing", "ease_out"),
        repeat=raw.get("repeat", 0),
        direction=raw.get("direction", ""),
        extra={k: v for k, v in raw.items()
               if k not in ("type", "effect", "animation", "trigger",
                            "duration", "delay", "easing", "repeat", "direction")},
    )
