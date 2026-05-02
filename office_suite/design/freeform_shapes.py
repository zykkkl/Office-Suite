"""自由贝塞尔形状预设 — 有机形状、波浪边框、水墨飞溅等装饰元素

所有函数返回 freeform_path 字符串（SVG 路径语法，百分比坐标 0-100），
可直接赋值给 DSL 元素的 freeform_path 字段。

用法：
    from office_suite.design.freeform_shapes import blob_shape, wave_edge
    path = blob_shape(seed=42)
    slide_elements.append({
        "type": "shape",
        "shape_type": "freeform",
        "freeform_path": path,
        "position": {"x": 60, "y": 40, "width": 30, "height": 25},
        "style": {"fill": {"color": "#3B82F6"}, "opacity": 0.15},
    })
"""

from __future__ import annotations

import math
import random


def blob_shape(
    seed: int = 0,
    cx: float = 50,
    cy: float = 50,
    r: float = 30,
    points: int = 6,
    jitter: float = 0.25,
) -> str:
    """生成有机斑点形状（贝塞尔闭合路径）

    Args:
        seed: 随机种子（不同 seed 产生不同形状）
        cx, cy: 中心点（百分比 0-100）
        r: 基础半径（百分比）
        points: 控制点数量（4-12）
        jitter: 形状变异程度（0-0.5）
    Returns:
        SVG 路径字符串
    """
    rng = random.Random(seed)
    pts = []
    for i in range(points):
        angle = 2 * math.pi * i / points
        rr = r * (1 + rng.uniform(-jitter, jitter))
        px = cx + rr * math.cos(angle)
        py = cy + rr * math.sin(angle)
        pts.append((px, py))

    # 用三次贝塞尔平滑连接各控制点
    path_parts = [f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(points):
        p0 = pts[i]
        p1 = pts[(i + 1) % points]
        # 用控制点构造平滑曲线
        tension = 0.4
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        cp1x = p0[0] + dx * tension
        cp1y = p0[1] + dy * tension
        cp2x = p1[0] - dx * tension
        cp2y = p1[1] - dy * tension
        path_parts.append(
            f"C {cp1x:.1f},{cp1y:.1f} {cp2x:.1f},{cp2y:.1f} {p1[0]:.1f},{p1[1]:.1f}"
        )
    path_parts.append("Z")
    return " ".join(path_parts)


def wave_edge(
    direction: str = "bottom",
    amplitude: float = 8.0,
    waves: int = 3,
) -> str:
    """生成波浪边缘形状（用于底部/顶部装饰条）

    Args:
        direction: 波浪方向（bottom, top）
        amplitude: 波浪振幅（百分比）
        waves: 波浪数量
    Returns:
        SVG 路径字符串（闭合矩形+波浪边）
    """
    seg_count = waves * 2
    seg_w = 100.0 / seg_count

    if direction == "bottom":
        path = ["M 0,0 L 100,0 L 100,100"]
        # 从右向左画波浪底边
        for i in range(seg_count):
            x1 = 100 - i * seg_w
            x2 = 100 - (i + 1) * seg_w
            mid = (x1 + x2) / 2
            cp_y = 100 - amplitude if i % 2 == 0 else 100 + amplitude
            path.append(f"Q {mid:.1f},{cp_y:.1f} {x2:.1f},100")
        path.append("Z")
    else:  # top
        path = ["M 0,100 L 100,100 L 100,0"]
        for i in range(seg_count):
            x1 = 100 - i * seg_w
            x2 = 100 - (i + 1) * seg_w
            mid = (x1 + x2) / 2
            cp_y = amplitude if i % 2 == 0 else -amplitude
            path.append(f"Q {mid:.1f},{cp_y:.1f} {x2:.1f},0")
        path.append("Z")
    return " ".join(path)


def ink_splash(
    seed: int = 0,
    cx: float = 50,
    cy: float = 50,
    r: float = 35,
) -> str:
    """生成墨溅形状（不规则有机边界，适合水墨主题）

    Args:
        seed: 随机种子
        cx, cy: 中心点
        r: 基础半径
    Returns:
        SVG 路径字符串
    """
    rng = random.Random(seed)
    n = 8
    pts = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        rr = r * rng.uniform(0.5, 1.3)
        # 墨溅特征：部分方向有尖角
        if rng.random() < 0.3:
            rr *= 1.4
        pts.append((cx + rr * math.cos(angle), cy + rr * math.sin(angle)))

    path = [f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(n):
        p0 = pts[i]
        p1 = pts[(i + 1) % n]
        # 不对称控制点产生不规则边缘
        t1 = rng.uniform(0.2, 0.5)
        t2 = rng.uniform(0.5, 0.8)
        cp1x = p0[0] + (p1[0] - p0[0]) * t1 + rng.uniform(-5, 5)
        cp1y = p0[1] + (p1[1] - p0[1]) * t1 + rng.uniform(-5, 5)
        cp2x = p0[0] + (p1[0] - p0[0]) * t2 + rng.uniform(-5, 5)
        cp2y = p0[1] + (p1[1] - p0[1]) * t2 + rng.uniform(-5, 5)
        path.append(
            f"C {cp1x:.1f},{cp1y:.1f} {cp2x:.1f},{cp2y:.1f} {p1[0]:.1f},{p1[1]:.1f}"
        )
    path.append("Z")
    return " ".join(path)


def ribbon_shape(width: float = 30, tail: float = 8) -> str:
    """生成飘带形状（角标装饰用）

    Args:
        width: 飘带宽度（百分比）
        tail: 尾部折叠深度（百分比）
    Returns:
        SVG 路径字符串
    """
    w = width
    t = tail
    return (
        f"M 0,0 L {w:.1f},0 L {w - t:.1f},{t:.1f} "
        f"L {w:.1f},{t * 2:.1f} L 0,{t * 2:.1f} Z"
    )


def cloud_shape(cx: float = 50, cy: float = 50, r: float = 25) -> str:
    """生成云朵形状（由多个圆弧组合）

    Args:
        cx, cy: 中心点
        r: 基础半径
    Returns:
        SVG 路径字符串
    """
    # 用 5 个相切的圆弧模拟云朵
    bumps = [
        (cx - r * 0.6, cy + r * 0.1, r * 0.45),
        (cx - r * 0.2, cy - r * 0.3, r * 0.55),
        (cx + r * 0.2, cy - r * 0.25, r * 0.5),
        (cx + r * 0.6, cy + r * 0.05, r * 0.45),
        (cx, cy + r * 0.15, r * 0.35),
    ]
    # 用贝塞尔近似每个弧并连接
    pts = []
    for bx, by, br in bumps:
        n = 6
        for i in range(n):
            angle = 2 * math.pi * i / n - math.pi / 2
            pts.append((bx + br * math.cos(angle), by + br * math.sin(angle)))

    # 按角度排序，取凸包上的点
    avg_x = sum(p[0] for p in pts) / len(pts)
    avg_y = sum(p[1] for p in pts) / len(pts)
    pts.sort(key=lambda p: math.atan2(p[1] - avg_y, p[0] - avg_x))

    # 用简化凸包（取前 12 个点做贝塞尔）
    hull = pts[:12]
    path = [f"M {hull[0][0]:.1f},{hull[0][1]:.1f}"]
    for i in range(len(hull)):
        p0 = hull[i]
        p1 = hull[(i + 1) % len(hull)]
        cp1x = p0[0] + (p1[0] - p0[0]) * 0.35
        cp1y = p0[1] + (p1[1] - p0[1]) * 0.35
        cp2x = p1[0] - (p1[0] - p0[0]) * 0.35
        cp2y = p1[1] - (p1[1] - p0[1]) * 0.35
        path.append(
            f"C {cp1x:.1f},{cp1y:.1f} {cp2x:.1f},{cp2y:.1f} {p1[0]:.1f},{p1[1]:.1f}"
        )
    path.append("Z")
    return " ".join(path)


def leaf_shape(
    cx: float = 50,
    cy: float = 50,
    length: float = 40,
    angle_deg: float = -30,
) -> str:
    """生成树叶形状

    Args:
        cx, cy: 叶柄端点
        length: 叶片长度（百分比）
        angle_deg: 叶片朝向角度（度，0=向右）
    Returns:
        SVG 路径字符串
    """
    rad = math.radians(angle_deg)
    ex = cx + length * math.cos(rad)
    ey = cy + length * math.sin(rad)
    # 叶片宽度控制点（垂直于叶轴）
    perp_rad = rad + math.pi / 2
    w = length * 0.25
    mx = (cx + ex) / 2
    my = (cy + ey) / 2
    cp1x = mx + w * math.cos(perp_rad)
    cp1y = my + w * math.sin(perp_rad)
    cp2x = mx - w * math.cos(perp_rad)
    cp2y = my - w * math.sin(perp_rad)
    return (
        f"M {cx:.1f},{cy:.1f} "
        f"C {cp1x:.1f},{cp1y:.1f} {cp1x:.1f},{cp1y:.1f} {ex:.1f},{ey:.1f} "
        f"C {cp2x:.1f},{cp2y:.1f} {cp2x:.1f},{cp2y:.1f} {cx:.1f},{cy:.1f} Z"
    )
