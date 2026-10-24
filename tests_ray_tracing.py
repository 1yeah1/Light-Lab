"""
光线追踪单元测试。
"""

import math
import pytest
from ray_tracing import mirror_segment, intersect_ray_segment, trace_ray


def assert_close(actual, expected, tol=0.01, msg=""):
    assert abs(actual - expected) <= tol, (
        f"{msg}: expected {expected}, got {actual}, diff {abs(actual - expected)}"
    )


# ===== 1. intersect_ray_segment 基本用例 =====

def test_intersect_basic_hit():
    """射线 (0,0)→(1,0) 打线段 (5,-1)-(5,1)：返回 5.0"""
    s = intersect_ray_segment((0, 0), (1, 0), (5, -1), (5, 1))
    assert s is not None, "应有交点"
    assert_close(s, 5.0, msg="交点距离")


def test_intersect_miss_vertical():
    """射线 (0,0)→(1,0) 打线段 (5,2)-(5,4)：返回 None"""
    s = intersect_ray_segment((0, 0), (1, 0), (5, 2), (5, 4))
    assert s is None, "射线与线段不相交"


def test_intersect_reverse_direction():
    """射线 (0,0)→(-1,0) 打线段 (5,-1)-(5,1)：返回 None（反向）"""
    s = intersect_ray_segment((0, 0), (-1, 0), (5, -1), (5, 1))
    assert s is None, "反向射线不应相交"


# ===== 2. mirror_segment 端点验证 =====

def test_mirror_segment_45deg():
    """center=(0,0), half=1.2, angle=45°"""
    p1, p2 = mirror_segment((0, 0), 1.2, 45)
    # cos(45°) = sin(45°) ≈ 0.7071
    # 1.2 * 0.7071 ≈ 0.8485
    assert_close(p1[0], -0.849, msg="p1.x")
    assert_close(p1[1], -0.849, msg="p1.y")
    assert_close(p2[0], 0.849, msg="p2.x")
    assert_close(p2[1], 0.849, msg="p2.y")


# ===== 3. 反射方向验证 =====

def test_reflection_vertical_mirror():
    """入射 (1,0) 打 angle=90° 的镜（竖直镜面）：反射方向 ≈ (-1,0)"""
    # 竖直镜面，法线水平
    mirrors = [{"center": (5, 0), "half_length": 1.2, "angle_deg": 90}]
    target_p1 = (10, -1)
    target_p2 = (10, 1)

    path, hit = trace_ray((0, 0), (1, 0), mirrors, target_p1, target_p2)
    # 光线应被反射回左侧
    if len(path) >= 2:
        # 第二段方向应大致向左
        dx = path[2][0] - path[1][0] if len(path) > 2 else path[1][0] - path[0][0]
        assert dx < 0, f"反射后应向左，实际 dx={dx}"


def test_reflection_45deg_mirror():
    """入射 (1,0) 打 angle=45° 的镜：反射方向 ≈ (0,1) 或 (0,-1)"""
    mirrors = [{"center": (5, 0), "half_length": 1.2, "angle_deg": 45}]
    target_p1 = (10, -1)
    target_p2 = (10, 1)

    path, hit = trace_ray((0, 0), (1, 0), mirrors, target_p1, target_p2)
    # 45° 镜面应使光线转向垂直方向
    if len(path) >= 3:
        dx = path[2][0] - path[1][0]
        dy = path[2][1] - path[1][1]
        # 应大致垂直（dx ≈ 0）
        assert abs(dx) < 0.5, f"反射后应大致垂直，实际 dx={dx}, dy={dy}"


# ===== 4. 5 档难度的已知解验证（核心测试） =====

def _build_mirrors(centers, angles, half_length=1.2):
    """辅助函数：构造镜子列表"""
    return [
        {"center": c, "half_length": half_length, "angle_deg": a}
        for c, a in zip(centers, angles)
    ]


def test_level1_known_solution():
    """难度 1：1 面镜，已知解 [45]"""
    mirrors = _build_mirrors([(0, 0)], [45])
    # 靶在顶部，光线从下方来，应为水平线段
    target_p1 = (-0.6, 4.5)
    target_p2 = (0.6, 4.5)

    path, hit = trace_ray((-6, 0), (1, 0), mirrors, target_p1, target_p2)
    assert hit, "已知解应命中靶"
    # 反射次数 = 镜子数 = 1
    # path 包含：起点 + 1 个反射点 + 靶点 = 3 个点
    # 反射次数 = len(path) - 2 = 1
    assert len(path) - 2 == 1, f"应反射 1 次，实际 {len(path) - 2}"


def test_level2_known_solution():
    """难度 2：2 面镜，已知解 [-45, -45]"""
    centers = [(0, 0), (0, -3)]
    mirrors = _build_mirrors(centers, [-45, -45])
    target_p1 = (5, -3.8)
    target_p2 = (5, -2.2)

    path, hit = trace_ray((-6, 0), (1, 0), mirrors, target_p1, target_p2)
    assert hit, "已知解应命中靶"
    assert len(path) - 2 == 2, f"应反射 2 次，实际 {len(path) - 2}"


def test_level3_known_solution():
    """难度 3：3 面镜，已知解 [-45, -45, 45]"""
    centers = [(0, 3), (0, -2), (5, -2)]
    mirrors = _build_mirrors(centers, [-45, -45, 45])
    # 光线从下方来，靶应为水平线段
    target_p1 = (4.2, 3)
    target_p2 = (5.8, 3)

    path, hit = trace_ray((-7, 3), (1, 0), mirrors, target_p1, target_p2)
    assert hit, "已知解应命中靶"
    assert len(path) - 2 == 3, f"应反射 3 次，实际 {len(path) - 2}"


def test_level4_known_solution():
    """难度 4：4 面镜，已知解 [-45, -45, 45, -45]"""
    centers = [(0, 3), (0, -2), (5, -2), (5, 1)]
    mirrors = _build_mirrors(centers, [-45, -45, 45, -45])
    target_p1 = (2, 0.1)
    target_p2 = (2, 1.9)

    path, hit = trace_ray((-7, 3), (1, 0), mirrors, target_p1, target_p2)
    assert hit, "已知解应命中靶"
    assert len(path) - 2 == 4, f"应反射 4 次，实际 {len(path) - 2}"


def test_level5_known_solution():
    """难度 5：5 面镜，已知解 [-45, -45, 45, -45, 45]"""
    centers = [(0, 3), (0, -2), (5, -2), (5, 1), (-1, 1)]
    mirrors = _build_mirrors(centers, [-45, -45, 45, -45, 45])
    # 光线从上方来，靶应为水平线段
    target_p1 = (-2.0, -3)
    target_p2 = (0.0, -3)

    path, hit = trace_ray((-7, 3), (1, 0), mirrors, target_p1, target_p2)
    assert hit, "已知解应命中靶"
    assert len(path) - 2 == 5, f"应反射 5 次，实际 {len(path) - 2}"


# ===== 5. 未命中用例 =====

def test_level1_miss():
    """难度 1，镜子角度 0°（水平镜面与光线共线），应未命中"""
    mirrors = _build_mirrors([(0, 0)], [0])
    # 靶在顶部，水平线段
    target_p1 = (-0.6, 4.5)
    target_p2 = (0.6, 4.5)

    path, hit = trace_ray((-6, 0), (1, 0), mirrors, target_p1, target_p2)
    assert not hit, "水平镜面不应命中靶"


# ===== 6. 多面镜解的稳定性（可选） =====

@pytest.mark.slow
def test_stability_level1():
    """难度 1，在已知解 ±5° 内随机采样，统计命中率"""
    import random
    random.seed(42)

    hits = 0
    trials = 200
    for _ in range(trials):
        angle = 45 + random.uniform(-5, 5)
        mirrors = _build_mirrors([(0, 0)], [angle])
        # 靶在顶部，水平线段
        target_p1 = (-0.6, 4.5)
        target_p2 = (0.6, 4.5)

        path, hit = trace_ray((-6, 0), (1, 0), mirrors, target_p1, target_p2)
        if hit:
            hits += 1

    hit_rate = hits / trials
    assert hit_rate > 0.2, f"命中率应 > 20%，实际 {hit_rate * 100:.1f}%"


if __name__ == "__main__":
    print("运行基础测试...")
    test_intersect_basic_hit()
    print("✓ intersect 基本命中")
    test_intersect_miss_vertical()
    print("✓ intersect 垂直未命中")
    test_intersect_reverse_direction()
    print("✓ intersect 反向未命中")
    test_mirror_segment_45deg()
    print("✓ mirror_segment 45°")
    test_reflection_vertical_mirror()
    print("✓ 竖直镜面反射")
    test_reflection_45deg_mirror()
    print("✓ 45° 镜面反射")
    test_level1_known_solution()
    print("✓ 难度 1 已知解")
    test_level2_known_solution()
    print("✓ 难度 2 已知解")
    test_level3_known_solution()
    print("✓ 难度 3 已知解")
    test_level4_known_solution()
    print("✓ 难度 4 已知解")
    test_level5_known_solution()
    print("✓ 难度 5 已知解")
    test_level1_miss()
    print("✓ 难度 1 未命中")
    print("\n全部基础测试通过！")
