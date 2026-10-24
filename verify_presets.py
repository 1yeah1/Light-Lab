"""
开发期验证脚本：验证所有难度的预设配置是否正确。
运行方式：python verify_presets.py
"""

from ray_tracing import trace_ray


# 预设数据（与 mirror_game.py 中的 PRESETS 保持一致）
PRESETS = {
    "level1": {
        "name": "1 面镜（初级）",
        "laser": {"origin": (-6, 0), "direction": (1, 0)},
        "mirrors": [{"center": (0, 0), "half_length": 1.2}],
        "target": {"center": (0, 4.5), "half_width": 0.6},
        "known_solution": [45],
        "init_angles": [15],
        "final_ray_dir": (0, 1),  # 光线最终向上
    },
    "level2": {
        "name": "2 面镜（中级）",
        "laser": {"origin": (-6, 0), "direction": (1, 0)},
        "mirrors": [
            {"center": (0, 0), "half_length": 1.2},
            {"center": (0, -3), "half_length": 1.2},
        ],
        "target": {"center": (5, -3), "half_width": 0.8},
        "known_solution": [-45, -45],
        "init_angles": [-25, -65],
        "final_ray_dir": (1, 0),  # 光线最终向右
    },
    "level3": {
        "name": "3 面镜（高级）",
        "laser": {"origin": (-7, 3), "direction": (1, 0)},
        "mirrors": [
            {"center": (0, 3), "half_length": 1.2},
            {"center": (0, -2), "half_length": 1.2},
            {"center": (5, -2), "half_length": 1.2},
        ],
        "target": {"center": (5, 3), "half_width": 0.8},
        "known_solution": [-45, -45, 45],
        "init_angles": [-30, -60, 30],
        "final_ray_dir": (0, 1),  # 光线最终向上
    },
    "level4": {
        "name": "4 面镜（专家）",
        "laser": {"origin": (-7, 3), "direction": (1, 0)},
        "mirrors": [
            {"center": (0, 3), "half_length": 1.2},
            {"center": (0, -2), "half_length": 1.2},
            {"center": (5, -2), "half_length": 1.2},
            {"center": (5, 1), "half_length": 1.2},
        ],
        "target": {"center": (2, 1), "half_width": 0.9},
        "known_solution": [-45, -45, 45, -45],
        "init_angles": [-35, -55, 35, -55],
        "final_ray_dir": (-1, 0),  # 光线最终向左
    },
    "level5": {
        "name": "5 面镜（大师）",
        "laser": {"origin": (-7, 3), "direction": (1, 0)},
        "mirrors": [
            {"center": (0, 3), "half_length": 1.2},
            {"center": (0, -2), "half_length": 1.2},
            {"center": (5, -2), "half_length": 1.2},
            {"center": (5, 1), "half_length": 1.2},
            {"center": (-1, 1), "half_length": 1.2},
        ],
        "target": {"center": (-1, -3), "half_width": 1.0},
        "known_solution": [-45, -45, 45, -45, 45],
        "init_angles": [-40, -50, 40, -50, 40],
        "final_ray_dir": (0, -1),  # 光线最终向下
    },
}


def get_target_segment(target, final_ray_direction):
    """
    根据最终光线方向生成靶的线段端点。
    如果光线主要是竖直方向，靶应为水平线段；反之亦然。
    """
    cx, cy = target["center"]
    hw = target["half_width"]

    # 判断最终光线方向
    dx, dy = final_ray_direction
    if abs(dy) > abs(dx):
        # 光线主要是竖直方向，靶应为水平线段
        return (cx - hw, cy), (cx + hw, cy)
    else:
        # 光线主要是水平方向，靶应为竖直线段
        return (cx, cy - hw), (cx, cy + hw)


def verify_preset(level_name, preset):
    """验证单个难度的预设"""
    print(f"\n验证 {level_name}: {preset['name']}")

    laser = preset["laser"]
    origin = laser["origin"]
    direction = laser["direction"]

    # 构造镜子列表（使用已知解的角度）
    mirrors = []
    for i, mirror_data in enumerate(preset["mirrors"]):
        mirrors.append({
            "center": mirror_data["center"],
            "half_length": mirror_data["half_length"],
            "angle_deg": preset["known_solution"][i],
        })

    # 生成靶的线段（使用最终光线方向）
    target_p1, target_p2 = get_target_segment(preset["target"], preset["final_ray_dir"])

    print(f"  激光: {origin} → {direction}")
    print(f"  镜子数量: {len(mirrors)}")
    print(f"  已知解: {preset['known_solution']}")
    print(f"  靶: {preset['target']['center']}, 半宽 {preset['target']['half_width']}")
    print(f"  最终光线方向: {preset['final_ray_dir']}")
    print(f"  靶线段: {target_p1} → {target_p2}")

    # 运行光线追踪
    path, hit = trace_ray(origin, direction, mirrors, target_p1, target_p2)

    print(f"  路径点数: {len(path)}")
    print(f"  反射次数: {len(path) - 2}")
    print(f"  命中: {hit}")

    if not hit:
        print(f"  ❌ 失败：已知解未命中靶！")
        print(f"  路径: {path}")
        return False

    expected_reflections = len(preset["mirrors"])
    actual_reflections = len(path) - 2
    if actual_reflections != expected_reflections:
        print(f"  ❌ 失败：期望反射 {expected_reflections} 次，实际 {actual_reflections} 次")
        return False

    print(f"  ✓ 通过")
    return True


def main():
    print("=" * 60)
    print("验证所有难度的预设配置")
    print("=" * 60)

    all_passed = True
    for level_name, preset in PRESETS.items():
        if not verify_preset(level_name, preset):
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有预设验证通过！")
    else:
        print("❌ 部分预设验证失败，请检查几何数据或光线追踪算法")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
