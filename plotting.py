"""
Plotly 绘图模块。
暴露三个函数：draw_reflection / draw_chopstick / draw_refraction。
"""

import math
import numpy as np
import plotly.graph_objects as go

from optics import refract_angle, reflect_angle, N_AIR, N_WATER, N_GLASS

# ---------------------------------------------------------------------------
# 公共常量
# ---------------------------------------------------------------------------
FONT_FAMILY = "Microsoft YaHei, PingFang SC, SimHei, sans-serif"
ARC_RADIUS = 2.0
ARC_N = 48

# 介质外观（水 / 玻璃）
MEDIUM_STYLES = {
    N_WATER: dict(name="水", fill="rgba(135,206,250,0.25)", accent="#1E90FF"),
    N_GLASS: dict(name="玻璃", fill="rgba(200,220,225,0.45)", accent="#607D8B"),
}


def _medium_style(n):
    """按折射率取下方介质的名称与配色。"""
    return MEDIUM_STYLES.get(
        n, dict(name="介质", fill="rgba(200,200,200,0.30)", accent="#757575")
    )


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _arc_points(cx, cy, r, start_deg, end_deg, n=ARC_N):
    """
    生成从 start_deg 逆时针到 end_deg 的圆弧点。
    角度采用 Plotly 约定：0°=正 x 轴，90°=正 y 轴。
    """
    if end_deg < start_deg:
        end_deg += 360.0
    angles = np.linspace(math.radians(start_deg), math.radians(end_deg), n)
    xs = cx + r * np.cos(angles)
    ys = cy + r * np.sin(angles)
    return xs, ys


def _arc_span(a, b):
    """返回 a 到 b 之间较短圆弧的 (起始角, 结束角)，结束角大于起始角。"""
    diff = (b - a + 180.0) % 360.0 - 180.0
    if diff >= 0:
        return a, a + diff
    return b, b - diff


def _base_layout():
    return dict(
        width=700, height=520,
        xaxis=dict(range=[-7, 7], visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[-5, 5], visible=False),
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=True,
        legend=dict(x=1.0, y=1.0, xanchor="right", font=dict(family=FONT_FAMILY, size=12)),
        margin=dict(l=10, r=10, t=30, b=10),
    )


def _normalize_deg(d):
    """将角度归一化到 [0, 360)。"""
    return d % 360.0


def _add_click_targets(fig, air_x=(-6.6, 6.6), air_y=(0.4, 4.7),
                       surface_x=(-6.6, 6.6), surface_y=-0.08,
                       nx=29, ny=23, surface_step=0.15):
    """
    在 fig 顶层添加透明散点，作为 st.plotly_chart 点选的命中目标。
    上半部分覆盖空气区域，最下面一行贴着界面（镜面/水面），
    点击界面时选中点的 y 约为 surface_y，便于上层区分点击区域。
    """
    xs = np.linspace(air_x[0], air_x[1], nx)
    ys = np.linspace(air_y[0], air_y[1], ny)
    grid_x, grid_y = np.meshgrid(xs, ys)
    surface_xs = np.arange(surface_x[0], surface_x[1] + 1e-9, surface_step)
    fig.add_trace(go.Scatter(
        x=np.concatenate([grid_x.ravel(), surface_xs]),
        y=np.concatenate([grid_y.ravel(), np.full(surface_xs.shape, surface_y)]),
        mode="markers",
        marker=dict(size=18, color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip", name="点击区域",
    ))


# ---------------------------------------------------------------------------
# 场景 A：光的反射
# ---------------------------------------------------------------------------

def draw_reflection(src_x: float, src_y: float, hit_x: float = 0.0) -> go.Figure:
    dx = hit_x - src_x
    dy = -src_y
    dist = math.hypot(dx, dy)
    cos_theta1 = abs(dy) / dist if dist > 0 else 0
    theta1_deg = math.degrees(math.acos(min(cos_theta1, 1.0)))

    theta2_deg = theta1_deg

    ref_dir_x = dx
    ref_dir_y = -dy
    ref_len = math.hypot(ref_dir_x, ref_dir_y)
    if ref_len > 0:
        ref_end_x = hit_x + ref_dir_x / ref_len * 6
        ref_end_y = 0 + ref_dir_y / ref_len * 6
    else:
        ref_end_x = hit_x + 3
        ref_end_y = 3

    fig = go.Figure()

    # 镜面（灰色矩形）
    fig.add_trace(go.Scatter(
        x=[-6, 6, 6, -6], y=[-0.15, -0.15, 0, 0],
        fill="toself", fillcolor="lightgray",
        line=dict(color="gray", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    # 法线
    fig.add_trace(go.Scatter(
        x=[hit_x, hit_x], y=[-4, 4],
        mode="lines", line=dict(color="gray", width=1.5, dash="dash"),
        name="法线", hoverinfo="skip",
    ))

    # 入射光线（黄色）
    fig.add_trace(go.Scatter(
        x=[src_x, hit_x], y=[src_y, 0],
        mode="lines", line=dict(color="gold", width=4),
        name="入射光",
    ))

    # 反射光线（橙色）
    fig.add_trace(go.Scatter(
        x=[hit_x, ref_end_x], y=[0, ref_end_y],
        mode="lines", line=dict(color="darkorange", width=4),
        name="反射光",
    ))

    # 入射角弧：从法线(向上=90°) 扫到入射光来的方向（从入射点看向光源）
    inc_back_x = src_x - hit_x
    inc_back_y = src_y - 0
    inc_back_angle = _normalize_deg(math.degrees(math.atan2(inc_back_y, inc_back_x)))
    normal_up = 90.0
    if inc_back_angle < normal_up:
        a_start_i, a_end_i = inc_back_angle, normal_up
    else:
        a_start_i, a_end_i = normal_up, inc_back_angle
    ax_i, ay_i = _arc_points(hit_x, 0, ARC_RADIUS, a_start_i, a_end_i)
    fig.add_trace(go.Scatter(
        x=ax_i, y=ay_i, mode="lines",
        line=dict(color="gold", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    # 反射角弧：从法线(90°) 扫到反射光方向
    ref_angle = _normalize_deg(math.degrees(math.atan2(ref_end_y, ref_end_x - hit_x)))
    if normal_up < ref_angle:
        a_start_r, a_end_r = normal_up, ref_angle
    else:
        a_start_r, a_end_r = ref_angle, normal_up
    ax_r, ay_r = _arc_points(hit_x, 0, ARC_RADIUS, a_start_r, a_end_r)
    fig.add_trace(go.Scatter(
        x=ax_r, y=ay_r, mode="lines",
        line=dict(color="darkorange", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    # 入射角标签
    mid_i = math.radians((a_start_i + a_end_i) / 2)
    fig.add_annotation(
        x=hit_x + 2.8 * math.cos(mid_i), y=2.8 * math.sin(mid_i),
        text=f"入射角 {round(theta1_deg)}°", showarrow=False,
        font=dict(size=15, color="gold", family=FONT_FAMILY),
    )

    # 反射角标签
    mid_r = math.radians((a_start_r + a_end_r) / 2)
    fig.add_annotation(
        x=hit_x + 2.8 * math.cos(mid_r), y=2.8 * math.sin(mid_r),
        text=f"反射角 {round(theta2_deg)}°", showarrow=False,
        font=dict(size=15, color="darkorange", family=FONT_FAMILY),
    )

    # 入射点标记
    fig.add_annotation(
        x=hit_x, y=0, text="O", showarrow=False, xshift=-15, yshift=-15,
        font=dict(size=14, color="black", family=FONT_FAMILY),
    )

    # 光源 marker（可点击）
    fig.add_trace(go.Scatter(
        x=[src_x], y=[src_y],
        mode="markers",
        marker=dict(size=18, color="gold", line=dict(color="darkorange", width=2)),
        name="光源",
    ))

    # 透明点击目标放在最上层，保证点击优先命中网格而不是光线端点
    _add_click_targets(fig)
    fig.update_layout(**_base_layout())
    return fig, round(theta1_deg), round(theta2_deg)


# ---------------------------------------------------------------------------
# 场景 B：水中的筷子
# ---------------------------------------------------------------------------

def draw_chopstick(depth: float, n1: float = N_WATER) -> go.Figure:
    top_x, top_y = 2.0, 3.0
    tip_x, tip_y = -1.0, -depth
    eye_x, eye_y = 4.0, 3.0
    style = _medium_style(n1)

    # 筷子与水面交点
    t_surf = top_y / (top_y - tip_y)
    surf_x = top_x + t_surf * (tip_x - top_x)

    # 光线折射点（满足斯涅尔定律）
    hit_x = _find_chopstick_hit(tip_x, tip_y, eye_x, eye_y, n1=n1)

    # 计算角度
    dx_w = hit_x - tip_x
    dy_w = -tip_y
    len_w = math.hypot(dx_w, dy_w)
    theta_i = math.degrees(math.asin(min(abs(dx_w) / len_w, 1.0))) if len_w > 0 else 0

    dx_a = eye_x - hit_x
    dy_a = eye_y
    len_a = math.hypot(dx_a, dy_a)
    theta_r = math.degrees(math.asin(min(abs(dx_a) / len_a, 1.0))) if len_a > 0 else 0

    # 表观筷子尖端
    app_x, app_y = _apparent_tip(tip_x, tip_y, hit_x, eye_x, eye_y)

    fig = go.Figure()

    # 空气背景
    fig.add_trace(go.Scatter(
        x=[-7, 7, 7, -7], y=[5, 5, 0, 0],
        fill="toself", fillcolor="rgba(240,248,255,0.5)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))

    # 介质背景
    fig.add_trace(go.Scatter(
        x=[-7, 7, 7, -7], y=[0, 0, -5, -5],
        fill="toself", fillcolor=style["fill"],
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))

    # 介质名称
    fig.add_annotation(
        x=-5.6, y=-2.6, text=style["name"], showarrow=False,
        font=dict(size=30, color=style["accent"], family=FONT_FAMILY),
        opacity=0.55,
    )

    # 介质界面
    fig.add_trace(go.Scatter(
        x=[-7, 7], y=[0, 0],
        mode="lines", line=dict(color="black", width=3),
        name=f"{style['name']}面", hoverinfo="skip",
    ))

    # 法线
    fig.add_trace(go.Scatter(
        x=[hit_x, hit_x], y=[-4, 4],
        mode="lines", line=dict(color="gray", width=1.5, dash="dash"),
        name="法线", hoverinfo="skip",
    ))

    # 实际筷子（灰色虚线）
    fig.add_trace(go.Scatter(
        x=[top_x, tip_x], y=[top_y, tip_y],
        mode="lines", line=dict(color="gray", width=3, dash="dash"),
        name="实际位置",
    ))

    # 表观筷子（棕色实线，弯折）
    fig.add_trace(go.Scatter(
        x=[top_x, surf_x, app_x], y=[top_y, 0, app_y],
        mode="lines", line=dict(color="#8B4513", width=5),
        name="看起来的位置",
    ))

    # 光线路径
    fig.add_trace(go.Scatter(
        x=[tip_x, hit_x, eye_x], y=[tip_y, 0, eye_y],
        mode="lines", line=dict(color="#FFD700", width=3),
        name="光线",
    ))

    # 眼睛标记
    fig.add_trace(go.Scatter(
        x=[eye_x], y=[eye_y], mode="markers",
        marker=dict(size=22, color="black"),
        name="眼睛",
    ))
    fig.add_trace(go.Scatter(
        x=[eye_x + 0.15], y=[eye_y + 0.15], mode="markers",
        marker=dict(size=8, color="white"),
        showlegend=False, hoverinfo="skip",
    ))

    # 入射角弧（水中，法线下方）
    normal_down = 270.0
    inc_dir = _normalize_deg(math.degrees(math.atan2(tip_y, tip_x - hit_x)))
    if inc_dir < normal_down:
        a_start, a_end = inc_dir, normal_down
    else:
        a_start, a_end = normal_down, inc_dir
    ax, ay = _arc_points(hit_x, 0, ARC_RADIUS, a_start, a_end)
    fig.add_trace(go.Scatter(
        x=ax, y=ay, mode="lines",
        line=dict(color="#FFD700", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    # 折射角弧（空气中，法线上方）
    normal_up = 90.0
    ref_dir = _normalize_deg(math.degrees(math.atan2(eye_y, eye_x - hit_x)))
    if normal_up < ref_dir:
        a_start2, a_end2 = normal_up, ref_dir
    else:
        a_start2, a_end2 = ref_dir, normal_up
    ax2, ay2 = _arc_points(hit_x, 0, ARC_RADIUS, a_start2, a_end2)
    fig.add_trace(go.Scatter(
        x=ax2, y=ay2, mode="lines",
        line=dict(color="#1E90FF", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    # 角度标签
    mid_i = math.radians((a_start + a_end) / 2)
    fig.add_annotation(
        x=hit_x + 2.8 * math.cos(mid_i), y=2.8 * math.sin(mid_i),
        text=f"入射角 {round(theta_i)}°", showarrow=False,
        font=dict(size=14, color="#FFD700", family=FONT_FAMILY),
    )
    mid_r = math.radians((a_start2 + a_end2) / 2)
    fig.add_annotation(
        x=hit_x + 2.8 * math.cos(mid_r), y=2.8 * math.sin(mid_r),
        text=f"折射角 {round(theta_r)}°", showarrow=False,
        font=dict(size=14, color="#1E90FF", family=FONT_FAMILY),
    )

    fig.update_layout(**_base_layout())
    return fig


def _find_chopstick_hit(tip_x, tip_y, eye_x, eye_y, n1=N_WATER, n2=N_AIR):
    """数值法求光线从水下尖端到空气中眼睛的折射点 x 坐标。"""
    best_hx = (tip_x + eye_x) / 2
    best_err = float("inf")
    for hx_int in range(int(tip_x * 20), int(eye_x * 20) + 1):
        hx = hx_int / 20.0
        dx1 = hx - tip_x
        dy1 = -tip_y
        l1 = math.hypot(dx1, dy1)
        sin1 = abs(dx1) / l1 if l1 > 0 else 0

        dx2 = eye_x - hx
        dy2 = eye_y
        l2 = math.hypot(dx2, dy2)
        sin2 = abs(dx2) / l2 if l2 > 0 else 0

        err = abs(n1 * sin1 - n2 * sin2)
        if err < best_err:
            best_err = err
            best_hx = hx
    return best_hx


def _apparent_tip(tip_x, tip_y, hit_x, eye_x, eye_y):
    """计算表观筷子尖端：折射光线反向延长线与原始筷子线的交点。"""
    dx_a = eye_x - hit_x
    dy_a = eye_y

    top_x, top_y = 2.0, 3.0
    c_x = tip_x - top_x
    c_y = tip_y - top_y

    if abs(dy_a) < 1e-10:
        return tip_x, tip_y

    ratio = dx_a / dy_a
    lhs_coeff = c_y * ratio - c_x
    if abs(lhs_coeff) < 1e-10:
        return tip_x, tip_y

    rhs = top_x - hit_x - top_y * ratio
    s = rhs / lhs_coeff

    return top_x + s * c_x, top_y + s * c_y


# ---------------------------------------------------------------------------
# 场景 C：光进水里
# ---------------------------------------------------------------------------

def draw_refraction(hit_x: float, n2: float, src_x: float = -5.0, src_y: float = 4.0) -> go.Figure:
    """
    绘制折射场景。

    参数:
        hit_x: 光线照射到水面的 x 位置
        n2: 下方介质的折射率
        src_x: 光源 x 坐标
        src_y: 光源 y 坐标（>0 在介质上方，<0 表示光源在介质中）
    """
    dx = hit_x - src_x
    dy = 0 - src_y
    dist = math.hypot(dx, dy)
    cos_theta1 = abs(dy) / dist if dist > 0 else 0
    theta1 = math.degrees(math.acos(min(cos_theta1, 1.0)))
    theta2 = reflect_angle(theta1)

    # src_y >= 0：光从空气射入下方介质；src_y < 0：光源在介质中，光射向空气
    above = src_y >= 0
    side = 1.0 if above else -1.0
    n_from = N_AIR if above else n2
    n_to = n2 if above else N_AIR
    theta3 = refract_angle(theta1, n_from, n_to)

    sign_x = 1 if dx >= 0 else -1

    # 反射光：与入射光同在一侧，按入射角对称折回
    refl_dir_x = math.sin(math.radians(theta1)) * sign_x
    refl_dir_y = math.cos(math.radians(theta1)) * side
    refl_end_x = hit_x + refl_dir_x * 6
    refl_end_y = 0 + refl_dir_y * 6

    # 折射光：进入另一侧介质
    if theta3 is not None:
        refr_dir_x = math.sin(math.radians(theta3)) * sign_x
        refr_dir_y = -math.cos(math.radians(theta3)) * side
        refr_end_x = hit_x + refr_dir_x * 6
        refr_end_y = 0 + refr_dir_y * 6
    else:
        refr_end_x = hit_x
        refr_end_y = -side * 6

    fig = go.Figure()

    # 空气背景
    fig.add_trace(go.Scatter(
        x=[-7, 7, 7, -7], y=[5, 5, 0, 0],
        fill="toself", fillcolor="rgba(240,248,255,0.5)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))

    # 下方介质背景
    style = _medium_style(n2)
    fig.add_trace(go.Scatter(
        x=[-7, 7, 7, -7], y=[0, 0, -5, -5],
        fill="toself", fillcolor=style["fill"],
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))

    # 介质名称
    fig.add_annotation(
        x=-5.6, y=-2.6, text=style["name"], showarrow=False,
        font=dict(size=30, color=style["accent"], family=FONT_FAMILY),
        opacity=0.55,
    )

    # 界面（黑色粗线）
    fig.add_trace(go.Scatter(
        x=[-7, 7], y=[0, 0],
        mode="lines", line=dict(color="black", width=3),
        name="界面", hoverinfo="skip",
    ))

    # 法线
    fig.add_trace(go.Scatter(
        x=[hit_x, hit_x], y=[-4, 4],
        mode="lines", line=dict(color="gray", width=1.5, dash="dash"),
        name="法线", hoverinfo="skip",
    ))

    # 入射光线（黄色）
    fig.add_trace(go.Scatter(
        x=[src_x, hit_x], y=[src_y, 0],
        mode="lines", line=dict(color="gold", width=4),
        name="入射光",
    ))

    # 反射光线（橙色）
    fig.add_trace(go.Scatter(
        x=[hit_x, refl_end_x], y=[0, refl_end_y],
        mode="lines", line=dict(color="darkorange", width=4),
        name="反射光",
    ))

    # 折射光线（蓝色）
    if theta3 is not None:
        fig.add_trace(go.Scatter(
            x=[hit_x, refr_end_x], y=[0, refr_end_y],
            mode="lines", line=dict(color="blue", width=4),
            name="折射光",
        ))

    # ---- 角度弧 ----
    normal_src = 90.0 if above else 270.0  # 指向光源一侧的法线方向
    normal_dst = 270.0 if above else 90.0
    inc_back_deg = _normalize_deg(math.degrees(math.atan2(-dy, -dx)))
    a_start_i, a_end_i = _arc_span(inc_back_deg, normal_src)
    ax_i, ay_i = _arc_points(hit_x, 0, ARC_RADIUS, a_start_i, a_end_i)
    fig.add_trace(go.Scatter(
        x=ax_i, y=ay_i, mode="lines",
        line=dict(color="gold", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    refl_dir_angle = _normalize_deg(math.degrees(math.atan2(refl_dir_y, refl_dir_x)))
    a_start_r, a_end_r = _arc_span(refl_dir_angle, normal_src)
    ax_r, ay_r = _arc_points(hit_x, 0, ARC_RADIUS, a_start_r, a_end_r)
    fig.add_trace(go.Scatter(
        x=ax_r, y=ay_r, mode="lines",
        line=dict(color="darkorange", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    if theta3 is not None:
        refr_dir_angle = _normalize_deg(math.degrees(math.atan2(refr_dir_y, refr_dir_x)))
        a_start_t, a_end_t = _arc_span(refr_dir_angle, normal_dst)
        ax_t, ay_t = _arc_points(hit_x, 0, ARC_RADIUS, a_start_t, a_end_t)
        fig.add_trace(go.Scatter(
            x=ax_t, y=ay_t, mode="lines",
            line=dict(color="blue", width=2),
            showlegend=False, hoverinfo="skip",
        ))

    # ---- 角度标签 ----
    mid_i = math.radians((a_start_i + a_end_i) / 2)
    fig.add_annotation(
        x=hit_x + 2.8 * math.cos(mid_i), y=2.8 * math.sin(mid_i),
        text=f"入射角 {round(theta1)}°", showarrow=False,
        font=dict(size=15, color="gold", family=FONT_FAMILY),
    )
    mid_r = math.radians((a_start_r + a_end_r) / 2)
    fig.add_annotation(
        x=hit_x + 2.8 * math.cos(mid_r), y=2.8 * math.sin(mid_r),
        text=f"反射角 {round(theta2)}°", showarrow=False,
        font=dict(size=15, color="darkorange", family=FONT_FAMILY),
    )
    if theta3 is not None:
        mid_t = math.radians((a_start_t + a_end_t) / 2)
        fig.add_annotation(
            x=hit_x + 2.8 * math.cos(mid_t), y=2.8 * math.sin(mid_t),
            text=f"折射角 {round(theta3)}°", showarrow=False,
            font=dict(size=15, color="blue", family=FONT_FAMILY),
        )

    # 光源 marker
    fig.add_trace(go.Scatter(
        x=[src_x], y=[src_y],
        mode="markers",
        marker=dict(size=18, color="gold", line=dict(color="darkorange", width=2)),
        name="光源",
    ))

    # 透明点击目标放在最上层，保证点击优先命中网格而不是光线端点
    _add_click_targets(fig)
    fig.update_layout(**_base_layout())
    return fig, round(theta1), round(theta2), (round(theta3) if theta3 is not None else None)


# ---------------------------------------------------------------------------
# 场景 D：三棱镜折射光路（全透 / 非全透对照）
# ---------------------------------------------------------------------------

def _prism_entry(entry_t):
    """返回 (入射方向, 入射点)：光与左侧面法线成 45°。"""
    d_in = (math.cos(math.radians(15)), math.sin(math.radians(15)))
    entry = (
        _PRISM_B[0] + entry_t * (_PRISM_A[0] - _PRISM_B[0]),
        _PRISM_B[1] + entry_t * (_PRISM_A[1] - _PRISM_B[1]),
    )
    return d_in, entry


def _nearest_face(p, d, skip=None):
    """离 p 最近的棱镜面交点。"""
    best = None
    for idx, (a, b, n_out) in enumerate(_PRISM_FACES):
        if idx == skip:
            continue
        t = _ray_face_hit(p, d, a, b)
        if t is not None and (best is None or t < best[0]):
            best = (t, idx, n_out)
    return best


def _reflect_dir(d, normal):
    k = _dot(d, normal)
    return _unit((d[0] - 2 * k * normal[0], d[1] - 2 * k * normal[1]))


def _face_out_normal_at(point):
    """返回经过 point 的那个棱镜面的向外法线。"""
    for a, b, n_out in _PRISM_FACES:
        ex, ey = b[0] - a[0], b[1] - a[1]
        t = ((point[0] - a[0]) * ex + (point[1] - a[1]) * ey) / (ex * ex + ey * ey)
        t = max(0.0, min(1.0, t))
        if math.hypot(point[0] - (a[0] + t * ex), point[1] - (a[1] + t * ey)) < 1e-6:
            return n_out
    return None


def _add_normal(fig, point, normal, length=1.3, show_label=False):
    """在界面上的光线作用点画一条虚线法线。"""
    fig.add_trace(go.Scatter(
        x=[point[0] - length * normal[0], point[0] + length * normal[0]],
        y=[point[1] - length * normal[1], point[1] + length * normal[1]],
        mode="lines",
        line=dict(color="#455A64", width=2, dash="dash"),
        name="法线", showlegend=show_label, hoverinfo="skip",
    ))
    if show_label:
        fig.add_annotation(
            x=point[0] + length * normal[0],
            y=point[1] + length * normal[1],
            text="法线", showarrow=False, xanchor="left",
            font=dict(size=11, color="#455A64", family=FONT_FAMILY),
        )


def _add_prism(fig):
    style = _medium_style(N_GLASS)
    fig.add_trace(go.Scatter(
        x=[_PRISM_B[0], _PRISM_C[0], _PRISM_A[0], _PRISM_B[0]],
        y=[_PRISM_B[1], _PRISM_C[1], _PRISM_A[1], _PRISM_B[1]],
        fill="toself", fillcolor=style["fill"],
        line=dict(color="#607D8B", width=3),
        showlegend=False, hoverinfo="skip",
    ))


def _add_incoming(fig, entry, d_in):
    start = (entry[0] - 4.8 * d_in[0], entry[1] - 4.8 * d_in[1])
    fig.add_trace(go.Scatter(
        x=[start[0], entry[0]], y=[start[1], entry[1]],
        mode="lines", line=dict(color="gold", width=4),
        name="入射光",
    ))


def draw_prism_ideal(entry_t: float = 0.5, show_labels: bool = True):
    """
    全透三棱镜：光只在两个界面上发生折射。

    返回 (fig, 入射角, 出射角, 偏转角)。
    """
    d_in, entry = _prism_entry(entry_t)
    path, q, d_out, theta_out = _trace_through_prism(entry, d_in, N_GLASS)

    fig = go.Figure()
    _add_prism(fig)
    _add_incoming(fig, entry, d_in)

    # 入射点的法线
    _add_normal(fig, entry, _face_out_normal_at(entry), show_label=True)

    # 镜内光路
    fig.add_trace(go.Scatter(
        x=[pt[0] for pt in path], y=[pt[1] for pt in path],
        mode="lines", line=dict(color="#FFC107", width=4),
        name="镜内折射光",
    ))

    # 出射光
    if d_out is not None:
        end = (q[0] + 3.8 * d_out[0], q[1] + 3.8 * d_out[1])
        fig.add_trace(go.Scatter(
            x=[q[0], end[0]], y=[q[1], end[1]],
            mode="lines", line=dict(color="blue", width=4),
            name="出射光",
        ))
        # 出射点的法线
        _add_normal(fig, q, _face_out_normal_at(q))
        fig.add_annotation(
            x=end[0] + 0.1, y=end[1] - 0.5, text="向底面偏折",
            showarrow=False, xanchor="left",
            font=dict(size=13, color="#1565C0", family=FONT_FAMILY),
            visible=show_labels,
        )

    theta_i = 45.0
    deviation = math.degrees(math.acos(max(-1.0, min(1.0, _dot(d_in, d_out))))) if d_out else None

    fig.update_layout(**_base_layout())
    return fig, theta_i, theta_out, deviation


def draw_prism_partial(entry_t: float = 0.5, max_gen: int = 2, show_labels: bool = True):
    """
    非全透三棱镜：界面处同时发生折射与部分反射，形成多条逐渐变弱的光路。

    返回 (fig, 入射角, 主出射角, 光路条数)。
    """
    d_in, entry = _prism_entry(entry_t)

    res = _refract_vec(d_in, (0.866, -0.5), N_AIR, N_GLASS)
    branches = []
    normal_pts = [(entry, _face_out_normal_at(entry))]
    if res is not None:
        stack = [(entry, res[0], 0, [entry], None)]
        while stack:
            p, d, gen, pts, skip = stack.pop(0)
            for _ in range(3):
                hit = _nearest_face(p, d, skip)
                if hit is None:
                    break
                t, idx, n_out = hit
                q = (p[0] + t * d[0], p[1] + t * d[1])
                pts = pts + [q]
                normal_pts.append((q, n_out))
                out = _refract_vec(d, n_out, N_GLASS, N_AIR)
                if out is not None:
                    branches.append((pts, q, out[0], gen))
                    if gen < max_gen:
                        stack.append((q, _reflect_dir(d, n_out), gen + 1, [q], idx))
                    break
                # 全反射：留在镜内继续传播
                d = _reflect_dir(d, n_out)
                p, skip = q, idx

    fig = go.Figure()
    _add_prism(fig)
    _add_incoming(fig, entry, d_in)

    exit_colors = ("#1E88E5", "#64B5F6", "#90CAF9")
    exit_widths = (4, 2.5, 1.6)
    exit_names = ("折射线（最强）", "折射线（较弱）", "折射线（最弱）")
    shown = set()
    for pts, q, d_out, gen in branches:
        g = min(gen, 2)
        legend = gen not in shown
        shown.add(gen)
        # 镜内光路（实线）
        fig.add_trace(go.Scatter(
            x=[pt[0] for pt in pts], y=[pt[1] for pt in pts],
            mode="lines",
            line=dict(color=exit_colors[g], width=exit_widths[g]),
            name=exit_names[g], showlegend=legend,
        ))
        # 出射后：越弱的支路越浅、用虚线
        end = (q[0] + 3.6 * d_out[0], q[1] + 3.6 * d_out[1])
        fig.add_trace(go.Scatter(
            x=[q[0], end[0]], y=[q[1], end[1]],
            mode="lines",
            line=dict(color=exit_colors[g], width=exit_widths[g],
                      dash="solid" if gen == 0 else "dash"),
            showlegend=False, hoverinfo="skip",
        ))

    # 每个折射 / 反射界面上的法线
    seen = set()
    first_normal = True
    for point, n_out in normal_pts:
        if n_out is None:
            continue
        key = (round(point[0], 4), round(point[1], 4))
        if key in seen:
            continue
        seen.add(key)
        _add_normal(fig, point, n_out, show_label=first_normal)
        first_normal = False

    weak = [b for b in branches if b[3] >= 2]
    if weak:
        q, d_out = weak[-1][1], weak[-1][2]
        fig.add_annotation(
            x=q[0] + 2.2 * d_out[0], y=q[1] + 2.2 * d_out[1],
            text="光强逐渐减弱", showarrow=False, xanchor="left",
            font=dict(size=12, color="#1565C0", family=FONT_FAMILY),
            visible=show_labels,
        )

    main_out = next((b[2] for b in branches if b[3] == 0), None)
    main_angle = None
    if main_out is not None:
        main_angle = math.degrees(math.acos(max(-1.0, min(1.0, _dot(
            main_out, (0.866, 0.5))))))

    fig.update_layout(**_base_layout())
    return fig, 45.0, main_angle, len(branches)


# ---------------------------------------------------------------------------
# 场景 E：三棱镜色散
# ---------------------------------------------------------------------------
# 等边三棱镜（顶角朝上）
_PRISM_A = (0.0, 1.7)
_PRISM_B = (-1.7, -1.244)
_PRISM_C = (1.7, -1.244)
# 每个面：(起点, 终点, 向外法线)
_PRISM_FACES = (
    (_PRISM_B, _PRISM_C, (0.0, -1.0)),      # 底面
    (_PRISM_C, _PRISM_A, (0.866, 0.5)),     # 右侧面
    (_PRISM_A, _PRISM_B, (-0.866, 0.5)),    # 左侧面
)

# 七色光的折射率（略作夸张，方便学生看清色散）
_SPECTRUM = (
    ("红", "#E53935", 1.500),
    ("橙", "#FB8C00", 1.512),
    ("黄", "#FDD835", 1.523),
    ("绿", "#43A047", 1.535),
    ("蓝", "#1E88E5", 1.546),
    ("靛", "#3949AB", 1.557),
    ("紫", "#8E24AA", 1.568),
)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _unit(v):
    length = math.hypot(v[0], v[1])
    return (v[0] / length, v[1] / length)


def _refract_vec(d, normal, n1, n2):
    """
    向量形式的折射（法线 normal 由入射介质指向折射介质）。

    返回 (折射方向, 入射角, 折射角)；发生全反射时返回 None。
    """
    cos1 = _dot(d, normal)  # normal 指向折射介质，与入射方向同向
    eta = n1 / n2
    k = 1 - eta * eta * (1 - cos1 * cos1)
    if k < 0:
        return None
    cos2 = math.sqrt(k)
    r = (
        eta * d[0] + (cos2 - eta * cos1) * normal[0],
        eta * d[1] + (cos2 - eta * cos1) * normal[1],
    )
    theta1 = math.degrees(math.acos(max(-1.0, min(1.0, cos1))))
    theta2 = math.degrees(math.acos(max(-1.0, min(1.0, cos2))))
    return _unit(r), theta1, theta2


def _ray_face_hit(p, d, a, b):
    """射线 p + t·d 与线段 ab 的交点参数 t；无交点返回 None。"""
    ex, ey = b[0] - a[0], b[1] - a[1]
    denom = d[0] * ey - d[1] * ex
    if abs(denom) < 1e-12:
        return None
    apx, apy = a[0] - p[0], a[1] - p[1]
    t = (apx * ey - apy * ex) / denom
    s = (apx * d[1] - apy * d[0]) / denom
    if t > 1e-9 and -1e-9 <= s <= 1 + 1e-9:
        return t
    return None


def _trace_through_prism(entry, d_in, n_glass):
    """
    追迹一条光线穿过等边三棱镜。

    返回 (镜内路径点列表, 出射起点, 出射方向, 出射角)。
    发生全反射时出射方向为 None。
    """
    inward_left = (0.866, -0.5)  # 左侧面的向内法线
    res = _refract_vec(d_in, inward_left, N_AIR, n_glass)
    if res is None:
        return [entry], entry, None, None
    d, _, _ = res

    p = entry
    path = [entry]
    for _ in range(3):
        best = None
        for a, b, n_out in _PRISM_FACES:
            t = _ray_face_hit(p, d, a, b)
            if t is not None and (best is None or t < best[0]):
                best = (t, a, b, n_out)
        if best is None:
            break
        t, _, _, n_out = best
        q = (p[0] + t * d[0], p[1] + t * d[1])
        path.append(q)

        out = _refract_vec(d, n_out, n_glass, N_AIR)
        if out is not None:
            d_out, _, theta_out = out
            return path, q, d_out, theta_out

        # 全反射，继续在镜内传播
        d = _unit((d[0] - 2 * _dot(d, n_out) * n_out[0],
                   d[1] - 2 * _dot(d, n_out) * n_out[1]))
        p = q

    return path, p, None, None


def draw_dispersion(entry_t: float = 0.5, show_labels: bool = True):
    """
    白光通过等边三棱镜的折射、部分反射与色散。

    参数:
        entry_t: 光射在左侧面上的位置比例（0.25 ~ 0.85）
    """
    style = _medium_style(N_GLASS)
    # 入射光方向：与左侧面法线成 45°
    d_in = (math.cos(math.radians(15)), math.sin(math.radians(15)))
    entry = (
        _PRISM_B[0] + entry_t * (_PRISM_A[0] - _PRISM_B[0]),
        _PRISM_B[1] + entry_t * (_PRISM_A[1] - _PRISM_B[1]),
    )
    start = (entry[0] - 4.8 * d_in[0], entry[1] - 4.8 * d_in[1])

    fig = go.Figure()

    # 棱镜
    fig.add_trace(go.Scatter(
        x=[_PRISM_B[0], _PRISM_C[0], _PRISM_A[0], _PRISM_B[0]],
        y=[_PRISM_B[1], _PRISM_C[1], _PRISM_A[1], _PRISM_B[1]],
        fill="toself", fillcolor=style["fill"],
        line=dict(color="#607D8B", width=3),
        showlegend=False, hoverinfo="skip",
    ))

    # 白光入射
    fig.add_trace(go.Scatter(
        x=[start[0], entry[0]], y=[start[1], entry[1]],
        mode="lines", line=dict(color="#EEEEEE", width=5),
        name="白光",
    ))

    ends = {}
    for name, color, n_glass in _SPECTRUM:
        path, q, d_out, _ = _trace_through_prism(entry, d_in, n_glass)
        fig.add_trace(go.Scatter(
            x=[pt[0] for pt in path], y=[pt[1] for pt in path],
            mode="lines", line=dict(color=color, width=3),
            showlegend=False, hoverinfo="skip",
        ))
        if d_out is None:
            continue
        end = (q[0] + 4.0 * d_out[0], q[1] + 4.0 * d_out[1])
        fig.add_trace(go.Scatter(
            x=[q[0], end[0]], y=[q[1], end[1]],
            mode="lines", line=dict(color=color, width=3),
            showlegend=False, hoverinfo="skip",
        ))
        ends[name] = end

    # 出射处的部分反射（以绿光为例，画一段虚线）
    g_path, q, _, _ = _trace_through_prism(entry, d_in, 1.535)
    if len(g_path) >= 2:
        d_inner = _unit((g_path[-1][0] - g_path[-2][0], g_path[-1][1] - g_path[-2][1]))
        normal = (0.866, 0.5)
        d_refl = _unit((d_inner[0] - 2 * _dot(d_inner, normal) * normal[0],
                        d_inner[1] - 2 * _dot(d_inner, normal) * normal[1]))
        fig.add_trace(go.Scatter(
            x=[q[0], q[0] + 1.5 * d_refl[0]], y=[q[1], q[1] + 1.5 * d_refl[1]],
            mode="lines", line=dict(color="#9E9E9E", width=1.5, dash="dot"),
            name="反射光（部分）",
        ))

    if "红" in ends:
        fig.add_annotation(
            x=ends["红"][0] + 0.15, y=ends["红"][1] + 0.3, text="红（偏折小）",
            showarrow=False, xanchor="left",
            font=dict(size=12, color="#E53935", family=FONT_FAMILY),
            visible=show_labels,
        )
    if "紫" in ends:
        fig.add_annotation(
            x=ends["紫"][0] + 0.15, y=ends["紫"][1] - 0.35, text="紫（偏折大）",
            showarrow=False, xanchor="left",
            font=dict(size=12, color="#8E24AA", family=FONT_FAMILY),
            visible=show_labels,
        )

    fig.update_layout(**_base_layout())

    theta_i = 45.0
    theta_red = _trace_through_prism(entry, d_in, 1.500)[3]
    theta_violet = _trace_through_prism(entry, d_in, 1.568)[3]
    return fig, theta_i, theta_red, theta_violet


# ---------------------------------------------------------------------------
# 知识卡片配图
# ---------------------------------------------------------------------------

def draw_normal_angle():
    """
    绘制法线和角度示意图（用于知识卡片）。
    水平镜面，法线竖直，入射光和反射光对称，标注入射角和反射角。
    """
    fig = go.Figure()

    # 镜面（灰色矩形）
    fig.add_trace(go.Scatter(
        x=[-6, 6, 6, -6], y=[-0.15, -0.15, 0, 0],
        fill="toself", fillcolor="lightgray",
        line=dict(color="gray", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    # 法线（灰色虚线）
    fig.add_trace(go.Scatter(
        x=[0, 0], y=[-2.5, 2.5],
        mode="lines", line=dict(color="gray", width=1.5, dash="dash"),
        name="法线", hoverinfo="skip",
    ))

    # 法线标签
    fig.add_annotation(
        x=0, y=2.8, text="法线", showarrow=False,
        font=dict(size=16, color="gray", family=FONT_FAMILY),
    )

    # 入射光（从左上方射向原点，45°）
    theta = 45
    theta_rad = math.radians(theta)
    src_x = -3 * math.sin(theta_rad)
    src_y = 3 * math.cos(theta_rad)
    fig.add_trace(go.Scatter(
        x=[src_x, 0], y=[src_y, 0],
        mode="lines", line=dict(color="gold", width=4),
        name="入射光",
    ))

    # 反射光（从原点射向右上方，45°）
    ref_x = 3 * math.sin(theta_rad)
    ref_y = 3 * math.cos(theta_rad)
    fig.add_trace(go.Scatter(
        x=[0, ref_x], y=[0, ref_y],
        mode="lines", line=dict(color="darkorange", width=4),
        name="反射光",
    ))

    # 入射角弧
    src_angle = _normalize_deg(math.degrees(math.atan2(src_y, src_x)))
    arc_x, arc_y = _arc_points(0, 0, 1.5, 90, src_angle)
    fig.add_trace(go.Scatter(
        x=arc_x, y=arc_y, mode="lines",
        line=dict(color="gold", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    # 反射角弧
    ref_angle = _normalize_deg(math.degrees(math.atan2(ref_y, ref_x)))
    arc_x2, arc_y2 = _arc_points(0, 0, 1.5, ref_angle, 90)
    fig.add_trace(go.Scatter(
        x=arc_x2, y=arc_y2, mode="lines",
        line=dict(color="darkorange", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    # 入射角标签
    mid_inc = math.radians(90 + theta / 2)
    fig.add_annotation(
        x=2.0 * math.cos(mid_inc), y=2.0 * math.sin(mid_inc),
        text="入射角", showarrow=False,
        font=dict(size=16, color="gold", family=FONT_FAMILY),
    )

    # 反射角标签
    mid_ref = math.radians(90 - theta / 2)
    fig.add_annotation(
        x=2.0 * math.cos(mid_ref), y=2.0 * math.sin(mid_ref),
        text="反射角", showarrow=False,
        font=dict(size=16, color="darkorange", family=FONT_FAMILY),
    )

    # 原点标记
    fig.add_annotation(
        x=0, y=0, text="O", showarrow=False, xshift=-15, yshift=-15,
        font=dict(size=14, color="black", family=FONT_FAMILY),
    )

    fig.update_layout(
        width=700, height=320,
        xaxis=dict(range=[-6, 6], visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[-4, 4], visible=False),
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=True,
        legend=dict(x=1.0, y=1.0, xanchor="right", font=dict(family=FONT_FAMILY, size=12)),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig


def draw_straight_line():
    """
    绘制光沿直线传播示意图（用于知识卡片）。
    光源发出平行光线，途中有障碍物，后面形成影子。
    """
    fig = go.Figure()

    # 光源（左侧黄色圆）
    fig.add_trace(go.Scatter(
        x=[-4], y=[0], mode="markers",
        marker=dict(size=20, color="gold"),
        name="光源",
    ))

    # 三条平行光线
    for y_offset in [-1, 0, 1]:
        fig.add_trace(go.Scatter(
            x=[-3.5, 4], y=[y_offset, y_offset],
            mode="lines", line=dict(color="gold", width=2),
            showlegend=False, hoverinfo="skip",
        ))

    # 障碍物（灰色矩形）
    fig.add_trace(go.Scatter(
        x=[0, 0.5, 0.5, 0], y=[-1.5, -1.5, 1.5, 1.5],
        fill="toself", fillcolor="darkgray",
        line=dict(color="black", width=2),
        name="障碍物",
    ))

    # 影子区域（浅灰色矩形）
    fig.add_trace(go.Scatter(
        x=[0.5, 4, 4, 0.5], y=[-1.5, -1.5, 1.5, 1.5],
        fill="toself", fillcolor="rgba(100,100,100,0.3)",
        line=dict(width=0),
        name="影子",
    ))

    # 标签
    fig.add_annotation(
        x=-4, y=1.5, text="光源", showarrow=False,
        font=dict(size=14, color="gold", family=FONT_FAMILY),
    )
    fig.add_annotation(
        x=0.25, y=2, text="障碍物", showarrow=False,
        font=dict(size=14, color="black", family=FONT_FAMILY),
    )
    fig.add_annotation(
        x=2.5, y=2, text="影子", showarrow=False,
        font=dict(size=14, color="gray", family=FONT_FAMILY),
    )

    fig.update_layout(
        width=700, height=320,
        xaxis=dict(range=[-5, 5], visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[-3, 3], visible=False),
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=True,
        legend=dict(x=1.0, y=1.0, xanchor="right", font=dict(family=FONT_FAMILY, size=12)),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig
