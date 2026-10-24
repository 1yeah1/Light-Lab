"""
物理内核单元测试。
用纯 assert 断言（容差 0.1°）。
"""

from optics import refract_angle, reflect_angle, N_AIR, N_WATER, N_GLASS


def assert_close(actual, expected, tol=0.1, msg=""):
    assert abs(actual - expected) <= tol, (
        f"{msg}: expected {expected}, got {actual}, diff {abs(actual - expected)}"
    )


# 1. 空气→水，入射角 45° 时，折射角 ≈ 32.1°
def test_air_water_45():
    result = refract_angle(45, N_AIR, N_WATER)
    assert_close(result, 32.1, msg="空气→水 45°")


# 2. 空气→水，入射角 10° 时，折射角 ≈ 7.5°
def test_air_water_10():
    result = refract_angle(10, N_AIR, N_WATER)
    assert_close(result, 7.5, msg="空气→水 10°")


# 3. 空气→玻璃(1.52)，入射角 45° 时，折射角 ≈ 27.7°
def test_air_glass_45():
    result = refract_angle(45, N_AIR, N_GLASS)
    assert_close(result, 27.7, msg="空气→玻璃 45°")


# 4. 反射角始终等于入射角（测 3 个不同角度）
def test_reflection():
    for angle in [15, 45, 70]:
        result = reflect_angle(angle)
        assert_close(result, angle, msg=f"反射角 {angle}°")


# 5. 空气→水时，所有 10–80° 的入射角，折射角都小于入射角
def test_water_all_angles():
    for angle in range(10, 81, 5):
        result = refract_angle(angle, N_AIR, N_WATER)
        assert result is not None, f"空气→水 {angle}° 返回 None"
        assert result < angle, (
            f"空气→水 {angle}°: 折射角 {result} 应小于入射角 {angle}"
        )


# 6. 空气→玻璃时，所有 10–80° 的入射角，折射角都小于入射角
def test_glass_all_angles():
    for angle in range(10, 81, 5):
        result = refract_angle(angle, N_AIR, N_GLASS)
        assert result is not None, f"空气→玻璃 {angle}° 返回 None"
        assert result < angle, (
            f"空气→玻璃 {angle}°: 折射角 {result} 应小于入射角 {angle}"
        )


if __name__ == "__main__":
    test_air_water_45()
    print("✓ 空气→水 45°")
    test_air_water_10()
    print("✓ 空气→水 10°")
    test_air_glass_45()
    print("✓ 空气→玻璃 45°")
    test_reflection()
    print("✓ 反射角 = 入射角")
    test_water_all_angles()
    print("✓ 空气→水 所有角度折射角 < 入射角")
    test_glass_all_angles()
    print("✓ 空气→玻璃 所有角度折射角 < 入射角")
    print("\n全部测试通过！")
