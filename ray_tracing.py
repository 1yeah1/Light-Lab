"""
光线追踪核心（纯函数，不依赖 streamlit）。
"""

import math


def mirror_segment(center, half_length, angle_deg):
    """
    计算平面镜的两个端点。

    参数:
        center: (x, y) 镜面中心坐标
        half_length: 镜面半长
        angle_deg: 镜面角度（度），0=水平，90=竖直，逆时针为正

    返回:
        (p1, p2): 两个端点坐标，每个是 (x, y) 元组
    """
    angle_rad = math.radians(angle_deg)
    u_x = math.cos(angle_rad)
    u_y = math.sin(angle_rad)

    p1 = (center[0] - half_length * u_x, center[1] - half_length * u_y)
    p2 = (center[0] + half_length * u_x, center[1] + half_length * u_y)
    return p1, p2


def intersect_ray_segment(origin, d, p1, p2):
    """
    求解射线与线段的交点。

    射线: origin + s * d (s > 0)
    线段: p1 + t * (p2 - p1) (t ∈ [0, 1])

    参数:
        origin: (x, y) 射线起点
        d: (dx, dy) 射线方向（不必归一化）
        p1, p2: 线段两端点

    返回:
        交点处的 s 值（float），或 None（无交点）
    """
    # 2×2 线性方程组:
    # [ d_x, -(p2_x-p1_x) ] [s]   [p1_x - origin_x]
    # [ d_y, -(p2_y-p1_y) ] [t] = [p1_y - origin_y]

    dx = d[0]
    dy = d[1]
    seg_dx = p2[0] - p1[0]
    seg_dy = p2[1] - p1[1]

    # 行列式
    det = dx * (-seg_dy) - dy * (-seg_dx)
    if abs(det) < 1e-9:
        return None  # 平行或退化

    # 求解 s, t
    rhs_x = p1[0] - origin[0]
    rhs_y = p1[1] - origin[1]

    s = (rhs_x * (-seg_dy) - rhs_y * (-seg_dx)) / det
    t = (dx * rhs_y - dy * rhs_x) / det

    # 检查有效性
    if s > 1e-6 and -1e-9 <= t <= 1 + 1e-9:
        return s
    return None


def trace_ray(origin, d, mirrors, target_p1, target_p2, max_bounces=10):
    """
    追踪光线在平面镜间的反射路径。

    参数:
        origin: (x, y) 光线起点
        d: (dx, dy) 初始方向（应归一化）
        mirrors: 镜子列表，每项 {"center": (x,y), "half_length": h, "angle_deg": a}
        target_p1, target_p2: 靶的两个端点
        max_bounces: 最大反射次数

    返回:
        (path, hit_target):
            path: 路径点列表 [(x1,y1), (x2,y2), ...]
            hit_target: 是否命中靶
    """
    pos = list(origin)
    direction = list(d)
    path = [tuple(pos)]
    hit_target = False

    for _ in range(max_bounces + 1):
        # 找最近的交点（靶或镜子）
        min_s = float("inf")
        hit_type = None  # "target" or mirror index
        hit_s = None

        # 检查靶
        s_target = intersect_ray_segment(pos, direction, target_p1, target_p2)
        if s_target is not None and s_target < min_s:
            min_s = s_target
            hit_type = "target"
            hit_s = s_target

        # 检查各镜子
        for i, mirror in enumerate(mirrors):
            p1, p2 = mirror_segment(mirror["center"], mirror["half_length"], mirror["angle_deg"])
            s_mirror = intersect_ray_segment(pos, direction, p1, p2)
            if s_mirror is not None and s_mirror < min_s:
                min_s = s_mirror
                hit_type = i
                hit_s = s_mirror

        # 无交点：画出边界
        if hit_type is None:
            path.append((pos[0] + direction[0] * 20, pos[1] + direction[1] * 20))
            break

        # 计算交点位置
        hit_pos = (pos[0] + hit_s * direction[0], pos[1] + hit_s * direction[1])

        # 检查是否陷入循环
        if len(path) >= 2:
            prev_pos = path[-1]
            dist = math.hypot(hit_pos[0] - prev_pos[0], hit_pos[1] - prev_pos[1])
            if dist < 1e-3:
                break

        # 命中靶
        if hit_type == "target":
            path.append(hit_pos)
            hit_target = True
            break

        # 命中镜子：反射
        mirror = mirrors[hit_type]
        p1, p2 = mirror_segment(mirror["center"], mirror["half_length"], mirror["angle_deg"])

        # 镜面法线（垂直于镜面方向）
        seg_dx = p2[0] - p1[0]
        seg_dy = p2[1] - p1[1]
        seg_len = math.hypot(seg_dx, seg_dy)
        if seg_len < 1e-9:
            break

        # 法线（两个可能方向）
        n1 = (-seg_dy / seg_len, seg_dx / seg_len)
        n2 = (seg_dy / seg_len, -seg_dx / seg_len)

        # 选择使 d·n < 0 的法线
        dot1 = direction[0] * n1[0] + direction[1] * n1[1]
        n = n1 if dot1 < 0 else n2

        # 反射公式: d' = d - 2(d·n)n
        dot_dn = direction[0] * n[0] + direction[1] * n[1]
        new_dir = [
            direction[0] - 2 * dot_dn * n[0],
            direction[1] - 2 * dot_dn * n[1],
        ]

        # 归一化
        new_len = math.hypot(new_dir[0], new_dir[1])
        if new_len < 1e-9:
            break
        direction = [new_dir[0] / new_len, new_dir[1] / new_len]

        pos = list(hit_pos)
        path.append(hit_pos)

    return path, hit_target
