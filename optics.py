"""
纯物理计算模块（内部使用，不向学生展示折射率数值）。
"""

import math


# 内部固定折射率（不在界面上展示）
N_AIR = 1.00
N_WATER = 1.33
N_GLASS = 1.52


def refract_angle(theta1_deg: float, n1: float, n2: float) -> float:
    """
    根据斯涅尔定律计算折射角（内部使用）。

    参数:
        theta1_deg: 入射角（度）
        n1: 入射侧折射率
        n2: 折射侧折射率

    返回:
        折射角（度）。若发生全反射则返回 None。
    """
    sin_theta2 = n1 * math.sin(math.radians(theta1_deg)) / n2
    if abs(sin_theta2) > 1.0:
        return None
    return math.degrees(math.asin(sin_theta2))


def reflect_angle(theta1_deg: float) -> float:
    """
    反射角等于入射角（封装便于教学）。

    参数:
        theta1_deg: 入射角（度）

    返回:
        反射角（度），与入射角相同。
    """
    return theta1_deg
