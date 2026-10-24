"""
🔦 光的反射与折射实验室
面向小学五到六年级学生的科学教具。
"""

import math
import streamlit as st
import plotly.graph_objects as go

from optics import refract_angle, reflect_angle, N_AIR, N_WATER, N_GLASS
from plotting import (
    draw_reflection, draw_chopstick, draw_refraction,
    draw_prism_ideal, draw_prism_partial, draw_dispersion,
)
from mirror_game import render_mirror_game
from knowledge import render_knowledge
from quiz import render_quiz


def _first_click_point(event):
    """取出 st.plotly_chart 点选事件中第一个点的 (x, y)，无选中时返回 None。"""
    points = event["selection"]["points"] if event else []
    if not points:
        return None
    return points[0]["x"], points[0]["y"]

# ---------------------------------------------------------------------------
# 面向学生的文案（方便老师修改）
# ---------------------------------------------------------------------------
TEXTS = {
    "page_title": "🔦 光路实验室",
    "tab_learn": "📖 学一学",
    "tab_play": "🔦 玩一玩",
    "tab_practice": "✏️ 练一练",
    "tab_reflection": "🪞 光的反射",
    "tab_chopstick": "🥢 {medium}中的筷子",
    "tab_refraction": "💧 光进{medium}里",
    "tab_prism": "🔺 三棱镜对照",
    "tab_dispersion": "🌈 三棱镜色散",
    "tab_mirror_game": "🎯 镜子打靶",
    "sidebar_medium": "下方介质",
    "sidebar_reset": "重新开始",
    "slider_theta": "入射角",
    "slider_depth": "筷子插入水中的深度",
    "slider_hit": "光照射到水面的位置",
    "slider_prism_entry": "光射入棱镜的位置",
    "slider_dispersion_entry": "光射入棱镜的位置",
    "input_src_x": "光源 X 坐标",
    "input_src_y": "光源 Y 坐标",
    "metric_incident": "入射角",
    "metric_reflected": "反射角",
    "metric_refracted": "折射角",
    "metric_turn": "光路偏转角",
    "metric_main_out": "主出射角",
    "metric_paths": "光路条数",
    "metric_red_out": "红光出射角",
    "metric_violet_out": "紫光出射角",
    "explain_reflection": "反射角总是等于入射角。",
    "explain_chopstick": "光从水里出来时会发生折射，所以筷子看起来弯了。",
    "explain_chopstick_glass": "光从玻璃里出来时折射更明显，所以筷子看起来弯得更厉害。",
    "explain_refraction": "光从空气斜射入水中时，折射角比入射角小。",
    "explain_refraction_glass": "光从空气斜射入玻璃时，折射角比入射角小，而且比射入水中时更小。",
    "explain_mirror_game": "调整平面镜的角度，让激光经过多次反射后命中靶心！",
    "prism_glass_title": "🔷 全透三棱镜：只在两个界面折射",
    "prism_partial_title": "🔸 非全透三棱镜：折射 + 反射",
    "explain_prism_compare": "**全透三棱镜**：入射光线从空气进入三棱镜时发生折射，向法线偏折；到达另一侧界面时，再次发生折射，出射光线偏离原入射方向，整体向三棱镜底部偏折。**非全透三棱镜**：入射光线进入三棱镜后，一部分光发生反射，另一部分光发生折射并继续传播；光线到达其他界面时，可能再次发生反射、折射或被吸收，最终形成多条不同方向的光路，且光强逐渐减弱。",
    "explain_dispersion": "白光看起来是白色的，其实里面藏着**红、橙、黄、绿、蓝、靛、紫**七种颜色的光。白光斜着射进三棱镜，会先后发生**两次折射**：进玻璃时向法线偏折，出玻璃时远离法线偏折。不同颜色的光在玻璃里跑得快慢不一样，红光拐弯最少，紫光拐弯最多。两次折射以后，七种颜色越分越开，形成一条彩色光带：**红色在最上面，紫色在最下面**，整体向三棱镜的底部偏折。这就是光的色散。三百多年前，牛顿正是用三棱镜发现了白光的这个秘密。",
    "dispersion_tip": "紫光比红光多偏折约 {diff:.0f}°，所以紫色排在下面、红色排在上面。",
    "medium_water": "水",
    "medium_glass": "玻璃",
}

# ---------------------------------------------------------------------------
# 页面配置
# ---------------------------------------------------------------------------
st.set_page_config(page_title="光路实验室", layout="wide")
st.title(TEXTS["page_title"])

# ---------------------------------------------------------------------------
# 侧边栏
# ---------------------------------------------------------------------------
with st.sidebar:
    medium_label = st.selectbox(
        TEXTS["sidebar_medium"],
        [TEXTS["medium_water"], TEXTS["medium_glass"]],
        index=0,
    )
    n2 = N_WATER if medium_label == TEXTS["medium_water"] else N_GLASS

    st.markdown("---")
    if st.button(TEXTS["sidebar_reset"], use_container_width=True):
        st.rerun()

# ---------------------------------------------------------------------------
# 三个一级 Tab
# ---------------------------------------------------------------------------
tab_learn, tab_play, tab_practice = st.tabs([
    TEXTS["tab_learn"],
    TEXTS["tab_play"],
    TEXTS["tab_practice"],
])

# ===== Tab 1：学一学 =====
with tab_learn:
    render_knowledge()

# ===== Tab 2：玩一玩（二级 Tab 挂载 6 个场景） =====
with tab_play:
    tab_a, tab_b, tab_c, tab_p, tab_x, tab_d = st.tabs([
        TEXTS["tab_reflection"],
        TEXTS["tab_chopstick"].format(medium=medium_label),
        TEXTS["tab_refraction"].format(medium=medium_label),
        TEXTS["tab_prism"],
        TEXTS["tab_dispersion"],
        TEXTS["tab_mirror_game"],
    ])

    # ===== 场景 A：光的反射 =====
    with tab_a:
        if "src_x_a" not in st.session_state:
            st.session_state.src_x_a = -2.8
            st.session_state.src_y_a = 2.8
        if "slider_hit_x_a" not in st.session_state:
            st.session_state.slider_hit_x_a = 0.0
        # 点击结果必须在控件创建前写回 session_state
        if "pending_src_a" in st.session_state:
            st.session_state.src_x_a, st.session_state.src_y_a = st.session_state.pop("pending_src_a")
        if "pending_hit_x_a" in st.session_state:
            st.session_state.slider_hit_x_a = st.session_state.pop("pending_hit_x_a")

        col_ctrl, col_fig = st.columns([1, 2.5])

        with col_ctrl:
            src_x_a = st.number_input(
                TEXTS["input_src_x"],
                min_value=-6.5, max_value=6.5, step=0.1, format="%.1f",
                key="src_x_a",
            )
            src_y_a = st.number_input(
                TEXTS["input_src_y"],
                min_value=0.5, max_value=4.8, step=0.1, format="%.1f",
                key="src_y_a",
            )
            st.markdown("---")
            hit_x_a = st.slider(
                "入射点 X 位置",
                min_value=-4.0, max_value=4.0, step=0.1,
                key="slider_hit_x_a",
            )

        with col_fig:
            fig, theta1_a, theta2_a = draw_reflection(src_x_a, src_y_a, hit_x_a)

            event = st.plotly_chart(
                fig, width="stretch", key="reflection_fig",
                on_select="rerun", selection_mode="points",
            )
            clicked = _first_click_point(event)

            if clicked is not None:
                cx, cy = clicked
                if cy > 0.3:
                    new_x = round(max(-6.5, min(6.5, cx)), 1)
                    new_y = round(max(0.5, min(4.8, cy)), 1)
                    if (new_x, new_y) != (src_x_a, src_y_a):
                        st.session_state.pending_src_a = (new_x, new_y)
                        st.rerun()
                elif -0.25 <= cy <= 0.25:
                    new_hit = round(max(-5.5, min(5.5, cx)), 1)
                    if new_hit != hit_x_a:
                        st.session_state.pending_hit_x_a = new_hit
                        st.rerun()

        col1, col2, col3 = st.columns(3)
        col1.metric(TEXTS["metric_incident"], f"{theta1_a}°")
        col2.metric(TEXTS["metric_reflected"], f"{theta2_a}°")
        col3.metric(TEXTS["metric_refracted"], "—")

        st.info(TEXTS["explain_reflection"])

    # ===== 场景 B：水中的筷子 =====
    with tab_b:
        # 只有水中才提供插入深度调节；玻璃中固定为同一深度
        if medium_label == TEXTS["medium_water"]:
            depth = st.slider(
                TEXTS["slider_depth"],
                min_value=1.0, max_value=3.0, step=0.5, value=2.0,
                key="slider_depth",
            )
        else:
            depth = 2.0
        fig = draw_chopstick(depth, n1=n2)
        st.plotly_chart(fig, use_container_width=True)

        # 计算角度用于 metric 显示
        tip_x, tip_y = -1.0, -depth
        eye_x, eye_y = 4.0, 3.0
        from plotting import _find_chopstick_hit
        hit_x = _find_chopstick_hit(tip_x, tip_y, eye_x, eye_y, n1=n2)

        dx_w = hit_x - tip_x
        dy_w = -tip_y
        len_w = math.hypot(dx_w, dy_w)
        theta_i_b = round(math.degrees(math.asin(min(abs(dx_w) / len_w, 1.0)))) if len_w > 0 else 0

        dx_a = eye_x - hit_x
        dy_a = eye_y
        len_a = math.hypot(dx_a, dy_a)
        theta_r_b = round(math.degrees(math.asin(min(abs(dx_a) / len_a, 1.0)))) if len_a > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric(TEXTS["metric_incident"], f"{theta_i_b}°")
        col2.metric(TEXTS["metric_reflected"], "—")
        col3.metric(TEXTS["metric_refracted"], f"{theta_r_b}°")

        st.info(
            TEXTS["explain_chopstick_glass"]
            if medium_label == TEXTS["medium_glass"]
            else TEXTS["explain_chopstick"]
        )

    # ===== 场景 C：光进入下方介质 =====
    with tab_c:
        if "src_x_c" not in st.session_state:
            st.session_state.src_x_c = -5.0
            st.session_state.src_y_c = 4.0
        if "slider_hit_c" not in st.session_state:
            st.session_state.slider_hit_c = 0.0
        # 点击结果必须在控件创建前写回 session_state
        if "pending_src_c" in st.session_state:
            st.session_state.src_x_c, st.session_state.src_y_c = st.session_state.pop("pending_src_c")
        if "pending_hit_c" in st.session_state:
            st.session_state.slider_hit_c = st.session_state.pop("pending_hit_c")

        col_ctrl, col_fig = st.columns([1, 2.5])

        with col_ctrl:
            src_x_c = st.number_input(
                TEXTS["input_src_x"],
                min_value=-6.5, max_value=6.5, step=0.1, format="%.1f",
                key="src_x_c",
            )
            src_y_c = st.number_input(
                TEXTS["input_src_y"],
                min_value=-4.5, max_value=4.8, step=0.1, format="%.1f",
                key="src_y_c",
            )
            if src_y_c < 0:
                st.caption(
                    f"光源在下方介质中：此时光从{medium_label}射向空气"
                )
            st.markdown("---")
            hit_x_c = st.slider(
                TEXTS["slider_hit"],
                min_value=-4.0, max_value=4.0, step=0.1,
                key="slider_hit_c",
            )

        with col_fig:
            fig, theta1_c, theta2_c, theta3_c = draw_refraction(hit_x_c, n2, src_x_c, src_y_c)

            event = st.plotly_chart(
                fig, width="stretch", key="refraction_fig",
                on_select="rerun", selection_mode="points",
            )
            clicked = _first_click_point(event)

            if clicked is not None:
                cx, cy = clicked
                if cy > 0.3:
                    new_x = round(max(-6.5, min(6.5, cx)), 1)
                    new_y = round(max(0.5, min(4.8, cy)), 1)
                    if (new_x, new_y) != (src_x_c, src_y_c):
                        st.session_state.pending_src_c = (new_x, new_y)
                        st.rerun()
                elif -0.25 <= cy <= 0.25:
                    new_hit = round(max(-5.5, min(5.5, cx)), 1)
                    if new_hit != hit_x_c:
                        st.session_state.pending_hit_c = new_hit
                        st.rerun()

        col1, col2, col3 = st.columns(3)
        col1.metric(TEXTS["metric_incident"], f"{theta1_c}°")
        col2.metric(TEXTS["metric_reflected"], f"{theta2_c}°")
        col3.metric(TEXTS["metric_refracted"], f"{theta3_c}°" if theta3_c is not None else "—")

        st.info(
            TEXTS["explain_refraction_glass"]
            if medium_label == TEXTS["medium_glass"]
            else TEXTS["explain_refraction"]
        )

    # ===== 场景 D：三棱镜光路对照（全透 / 非全透） =====
    with tab_p:
        entry_t = st.slider(
            TEXTS["slider_prism_entry"],
            min_value=0.25, max_value=0.85, step=0.05, value=0.5,
            key="slider_prism_entry",
        )

        col_ideal, col_partial = st.columns(2)

        with col_ideal:
            st.markdown(TEXTS["prism_glass_title"])
            fig_i, inc_i, out_i, turn_i = draw_prism_ideal(entry_t)
            st.plotly_chart(fig_i, use_container_width=True, key="prism_ideal")

            m1, m2, m3 = st.columns(3)
            m1.metric(TEXTS["metric_incident"], f"{inc_i:.0f}°")
            m2.metric(TEXTS["metric_refracted"], f"{out_i:.0f}°" if out_i is not None else "—")
            m3.metric(TEXTS["metric_turn"], f"{turn_i:.0f}°" if turn_i is not None else "—")

        with col_partial:
            st.markdown(TEXTS["prism_partial_title"])
            fig_p, inc_p, main_p, n_paths = draw_prism_partial(entry_t)
            st.plotly_chart(fig_p, use_container_width=True, key="prism_partial")

            m1, m2, m3 = st.columns(3)
            m1.metric(TEXTS["metric_incident"], f"{inc_p:.0f}°")
            m2.metric(TEXTS["metric_main_out"], f"{main_p:.0f}°" if main_p is not None else "—")
            m3.metric(TEXTS["metric_paths"], f"{n_paths}")

        st.info(TEXTS["explain_prism_compare"])

    # ===== 场景 E：三棱镜色散 =====
    with tab_x:
        entry_t = st.slider(
            TEXTS["slider_dispersion_entry"],
            min_value=0.25, max_value=0.85, step=0.05, value=0.5,
            key="slider_dispersion_entry",
        )
        fig_x, inc_x, red_x, violet_x = draw_dispersion(entry_t)
        st.plotly_chart(fig_x, use_container_width=True, key="dispersion_prism")

        col1, col2, col3 = st.columns(3)
        col1.metric(TEXTS["metric_incident"], f"{inc_x:.0f}°")
        col2.metric(TEXTS["metric_red_out"], f"{red_x:.0f}°")
        col3.metric(TEXTS["metric_violet_out"], f"{violet_x:.0f}°")
        st.caption(TEXTS["dispersion_tip"].format(diff=violet_x - red_x))

        st.info(TEXTS["explain_dispersion"])

    # ===== 场景 F：镜子打靶 =====
    with tab_d:
        st.info(TEXTS["explain_mirror_game"])
        render_mirror_game()

# ===== Tab 3：练一练 =====
with tab_practice:
    render_quiz()
