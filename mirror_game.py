"""
激光平面镜反射打靶游戏。
"""

import math
import streamlit as st
import plotly.graph_objects as go

from ray_tracing import mirror_segment, trace_ray

# ---------------------------------------------------------------------------
# 字体
# ---------------------------------------------------------------------------
FONT_FAMILY = "Microsoft YaHei, PingFang SC, SimHei, sans-serif"

# ---------------------------------------------------------------------------
# 预设数据
# ---------------------------------------------------------------------------
# level1 已知解 [45]，反射 1 次命中，已手工验证
# level2 已知解 [-45, -45]，反射 2 次命中，已手工验证
# level3 已知解 [-45, -45, 45]，反射 3 次命中，已手工验证
# level4 已知解 [-45, -45, 45, -45]，反射 4 次命中，已手工验证
# level5 已知解 [-45, -45, 45, -45, 45]，反射 5 次命中，已手工验证

PRESETS = {
    "level1": {
        "name": "1 面镜（初级）",
        "laser": {"origin": (-6, 0), "direction": (1, 0)},
        "mirrors": [{"center": (0, 0), "half_length": 1.2}],
        "target": {"center": (0, 4.5), "half_width": 0.6, "radii": [0.6, 0.4, 0.2]},
        "known_solution": [45],
        "init_angles": [15],
        "final_ray_dir": (0, 1),
    },
    "level2": {
        "name": "2 面镜（中级）",
        "laser": {"origin": (-6, 0), "direction": (1, 0)},
        "mirrors": [
            {"center": (0, 0), "half_length": 1.2},
            {"center": (0, -3), "half_length": 1.2},
        ],
        "target": {"center": (5, -3), "half_width": 0.8, "radii": [0.8, 0.5, 0.3]},
        "known_solution": [-45, -45],
        "init_angles": [-25, -65],
        "final_ray_dir": (1, 0),
    },
    "level3": {
        "name": "3 面镜（高级）",
        "laser": {"origin": (-7, 3), "direction": (1, 0)},
        "mirrors": [
            {"center": (0, 3), "half_length": 1.2},
            {"center": (0, -2), "half_length": 1.2},
            {"center": (5, -2), "half_length": 1.2},
        ],
        "target": {"center": (5, 3), "half_width": 0.8, "radii": [0.8, 0.5, 0.3]},
        "known_solution": [-45, -45, 45],
        "init_angles": [-30, -60, 30],
        "final_ray_dir": (0, 1),
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
        "target": {"center": (2, 1), "half_width": 0.9, "radii": [0.9, 0.6, 0.3]},
        "known_solution": [-45, -45, 45, -45],
        "init_angles": [-35, -55, 35, -55],
        "final_ray_dir": (-1, 0),
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
        "target": {"center": (-1, -3), "half_width": 1.0, "radii": [1.0, 0.7, 0.4]},
        "known_solution": [-45, -45, 45, -45, 45],
        "init_angles": [-40, -50, 40, -50, 40],
        "final_ray_dir": (0, -1),
    },
}


def get_target_segment(target, final_ray_dir):
    """根据最终光线方向生成靶的线段端点。"""
    cx, cy = target["center"]
    hw = target["half_width"]

    dx, dy = final_ray_dir
    if abs(dy) > abs(dx):
        # 光线主要是竖直方向，靶应为水平线段
        return (cx - hw, cy), (cx + hw, cy)
    else:
        # 光线主要是水平方向，靶应为竖直线段
        return (cx, cy - hw), (cx, cy + hw)


def draw_mirror_game(preset, mirror_angles):
    """
    绘制打靶场景。

    参数:
        preset: 预设字典
        mirror_angles: 当前镜面角度列表

    返回:
        go.Figure
    """
    laser = preset["laser"]
    origin = laser["origin"]
    direction = laser["direction"]

    # 构造镜子列表
    mirrors = []
    for i, mirror_data in enumerate(preset["mirrors"]):
        mirrors.append({
            "center": mirror_data["center"],
            "half_length": mirror_data["half_length"],
            "angle_deg": mirror_angles[i],
        })

    # 生成靶的线段
    target = preset["target"]
    target_p1, target_p2 = get_target_segment(target, preset["final_ray_dir"])

    # 运行光线追踪
    path, hit = trace_ray(origin, direction, mirrors, target_p1, target_p2)

    fig = go.Figure()

    # ---- 靶（同心圆） ----
    cx, cy = target["center"]
    radii = target["radii"]
    colors = ["red", "white", "red"]
    for i, r in enumerate(radii):
        # 画圆（用散点图模拟）
        theta = [t * 2 * math.pi / 60 for t in range(61)]
        circle_x = [cx + r * math.cos(t) for t in theta]
        circle_y = [cy + r * math.sin(t) for t in theta]
        fig.add_trace(go.Scatter(
            x=circle_x, y=circle_y,
            mode="lines",
            line=dict(color=colors[i % len(colors)], width=2),
            showlegend=False, hoverinfo="skip",
        ))

    # 命中时加黄色半透明圆
    if hit:
        r_hit = radii[0] * 1.5
        theta = [t * 2 * math.pi / 60 for t in range(61)]
        circle_x = [cx + r_hit * math.cos(t) for t in theta]
        circle_y = [cy + r_hit * math.sin(t) for t in theta]
        fig.add_trace(go.Scatter(
            x=circle_x, y=circle_y,
            fill="toself",
            fillcolor="rgba(255, 255, 0, 0.35)",
            line=dict(color="yellow", width=2),
            showlegend=False, hoverinfo="skip",
        ))

    # ---- 平面镜 ----
    for i, mirror in enumerate(mirrors):
        p1, p2 = mirror_segment(mirror["center"], mirror["half_length"], mirror["angle_deg"])
        # 镜面线段
        fig.add_trace(go.Scatter(
            x=[p1[0], p2[0]], y=[p1[1], p2[1]],
            mode="lines",
            line=dict(color="silver", width=8),
            name=f"镜 {i+1}",
            showlegend=(i == 0),
        ))
        # 两端小圆点
        fig.add_trace(go.Scatter(
            x=[p1[0], p2[0]], y=[p1[1], p2[1]],
            mode="markers",
            marker=dict(size=6, color="gray"),
            showlegend=False, hoverinfo="skip",
        ))
        # 中心小圆点
        fig.add_trace(go.Scatter(
            x=[mirror["center"][0]], y=[mirror["center"][1]],
            mode="markers",
            marker=dict(size=8, color="darkgray"),
            showlegend=False, hoverinfo="skip",
        ))
        # 序号徽标：沿镜面法线方向偏移，避免压住光线
        ang = math.radians(mirror["angle_deg"])
        fig.add_annotation(
            x=mirror["center"][0] - math.sin(ang) * 0.9,
            y=mirror["center"][1] + math.cos(ang) * 0.9,
            text=f"镜 {i+1}",
            showarrow=False,
            font=dict(size=13, color="white", family=FONT_FAMILY),
            bgcolor="#37474F",
            bordercolor="#ffffff", borderwidth=2, borderpad=4,
        )

    # ---- 激光源 ----
    fig.add_trace(go.Scatter(
        x=[origin[0]], y=[origin[1]],
        mode="markers",
        marker=dict(size=14, color="red"),
        name="激光源",
    ))
    # 激光源方向箭头（短线段）
    arrow_len = 0.8
    arrow_end = (origin[0] + arrow_len * direction[0], origin[1] + arrow_len * direction[1])
    fig.add_trace(go.Scatter(
        x=[origin[0], arrow_end[0]], y=[origin[1], arrow_end[1]],
        mode="lines",
        line=dict(color="red", width=3),
        showlegend=False, hoverinfo="skip",
    ))

    # ---- 光线路径 ----
    if len(path) >= 2:
        path_x = [p[0] for p in path]
        path_y = [p[1] for p in path]
        fig.add_trace(go.Scatter(
            x=path_x, y=path_y,
            mode="lines",
            line=dict(color="red", width=2.5),
            name="光线",
        ))

        # 最后一段加箭头
        if len(path) >= 2:
            last_seg_start = path[-2]
            last_seg_end = path[-1]
            fig.add_annotation(
                x=last_seg_end[0], y=last_seg_end[1],
                ax=last_seg_start[0], ay=last_seg_start[1],
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True,
                arrowhead=3, arrowsize=1.5, arrowwidth=2, arrowcolor="red",
            )

    # ---- 布局 ----
    fig.update_layout(
        width=700, height=520,
        xaxis=dict(range=[-8, 8], visible=False, scaleanchor="x", scaleratio=1),
        yaxis=dict(range=[-5, 5], visible=False),
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=True,
        legend=dict(x=1.0, y=1.0, xanchor="right", font=dict(family=FONT_FAMILY, size=12)),
        margin=dict(l=10, r=10, t=30, b=10),
    )

    return fig, hit, len(path) - 2


def render_mirror_game():
    """渲染打靶游戏的 UI。"""
    col_left, col_right = st.columns([1, 2.5])

    with col_left:
        # 难度选择
        level_names = [PRESETS[k]["name"] for k in PRESETS]
        selected_name = st.selectbox("难度", level_names, key="mirror_game_level")
        level_key = [k for k, v in PRESETS.items() if v["name"] == selected_name][0]
        preset = PRESETS[level_key]

        st.markdown("---")

        # 镜面角度滑块
        n_mirrors = len(preset["mirrors"])
        mirror_angles = []

        # 重置请求必须在滑块创建之前写回，否则会触发
        # StreamlitWidgetAlreadyInstantiatedError
        pending_reset = st.session_state.pop(f"mirror_reset_{level_key}", None)
        if pending_reset:
            for i, angle_value in enumerate(pending_reset):
                st.session_state[f"mirror_{level_key}_{i}"] = angle_value

        if n_mirrors <= 2:
            # 单列
            for i in range(n_mirrors):
                key = f"mirror_{level_key}_{i}"
                init_angle = preset["init_angles"][i]
                angle = st.slider(
                    f"平面镜 {i+1} 角度",
                    min_value=-90, max_value=90,
                    value=init_angle, step=1,
                    key=key,
                )
                mirror_angles.append(angle)
                st.caption(f"当前：{angle}°")
        elif n_mirrors <= 4:
            # 2 列
            for i in range(n_mirrors):
                if i % 2 == 0:
                    cols = st.columns(2)
                key = f"mirror_{level_key}_{i}"
                init_angle = preset["init_angles"][i]
                with cols[i % 2]:
                    angle = st.slider(
                        f"平面镜 {i+1}",
                        min_value=-90, max_value=90,
                        value=init_angle, step=1,
                        key=key,
                    )
                    mirror_angles.append(angle)
                    st.caption(f"{angle}°")
        else:  # n_mirrors == 5
            # 2 列排 4 个 + 第 5 个单独一行
            for i in range(4):
                if i % 2 == 0:
                    cols = st.columns(2)
                key = f"mirror_{level_key}_{i}"
                init_angle = preset["init_angles"][i]
                with cols[i % 2]:
                    angle = st.slider(
                        f"平面镜 {i+1}",
                        min_value=-90, max_value=90,
                        value=init_angle, step=1,
                        key=key,
                    )
                    mirror_angles.append(angle)
                    st.caption(f"{angle}°")

            # 第 5 个单独一行
            key = f"mirror_{level_key}_4"
            init_angle = preset["init_angles"][4]
            angle = st.slider(
                f"平面镜 5",
                min_value=-90, max_value=90,
                value=init_angle, step=1,
                key=key,
            )
            mirror_angles.append(angle)
            st.caption(f"{angle}°")

        st.markdown("---")

        # 重置按钮
        if st.button("🔄 重置", use_container_width=True):
            st.session_state[f"mirror_reset_{level_key}"] = preset["init_angles"]
            st.rerun()

        # 提示按钮
        if st.button("💡 提示", use_container_width=True):
            st.session_state["show_hint"] = not st.session_state.get("show_hint", False)

    with col_right:
        # 绘制图形
        fig, hit, reflections = draw_mirror_game(preset, mirror_angles)
        st.plotly_chart(fig, use_container_width=True)

        # 命中提示
        if hit:
            st.success("🎯 命中！")
        else:
            st.info("再调调角度试试~")

        # 反射次数
        st.caption(f"反射次数：{reflections}")

        # 提示逻辑
        if st.session_state.get("show_hint", False):
            hints = []
            max_delta = 0
            max_delta_idx = -1

            for i in range(n_mirrors):
                delta = mirror_angles[i] - preset["known_solution"][i]
                abs_delta = abs(delta)

                if abs_delta > max_delta:
                    max_delta = abs_delta
                    max_delta_idx = i

            if max_delta_idx >= 0:
                i = max_delta_idx
                delta = mirror_angles[i] - preset["known_solution"][i]
                abs_delta = abs(delta)

                if abs_delta < 5:
                    pass  # 已对准，不提示
                elif abs_delta < 15:
                    hints.append(f"平面镜 {i+1} 快对准了，稍微调一点")
                elif abs_delta < 30:
                    direction = "顺" if delta > 0 else "逆"
                    hints.append(f"平面镜 {i+1} 方向对了，继续往{direction}时针转")
                else:
                    direction = "顺" if delta > 0 else "逆"
                    hints.append(f"平面镜 {i+1} 试试往{direction}时针方向多转一些")

            if hints:
                st.info("\n".join(hints))
