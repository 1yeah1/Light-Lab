"""
光学知识学习模块（知识卡片）。
"""

import streamlit as st

from plotting import (
    draw_reflection,
    draw_refraction,
    draw_normal_angle,
    draw_straight_line,
)
from optics import N_WATER

# ---------------------------------------------------------------------------
# 面向学生的文案
# ---------------------------------------------------------------------------
TEXTS = {
    "module_title": "📖 光学知识卡片",
    "card_prefix": "卡片",
    "think_about_it": "💭 想一想",
    "show_answer": "👀 显示答案",
    "hide_answer": "🙈 隐藏答案",
    "answer_prefix": "**参考答案：**",
    "footer": "学完可以去「✏️ 练一练」检验一下",
}

# ---------------------------------------------------------------------------
# 知识卡片数据
# ---------------------------------------------------------------------------
CARDS = [
    {
        "title": "光沿直线传播",
        "summary": "光在同种均匀介质中沿直线传播",
        "body": "手电筒的光在空气中是一条直线。影子的形成、小孔成像，都是因为光沿直线传播。",
        "figure": ("draw_straight_line", {}),
        "think": "影子的形状和物体一样吗？为什么？",
        "answer": "不完全一样。影子是物体挡住光后形成的暗区，形状取决于物体的轮廓和光照射的方向。光源越大、物体离地面越远，影子就越模糊、越容易变形放大。",
    },
    {
        "title": "认识法线和角度",
        "summary": "法线垂直于镜面；入射角和反射角都是光线与法线的夹角",
        "body": "法线不是真实存在的光线，是为了研究方便画出来的一条虚线。入射角是入射光与法线的夹角，反射角是反射光与法线的夹角。它们都不是光线与镜面的夹角。",
        "figure": ("draw_normal_angle", {}),
        "think": "如果一束光贴着镜面照过去，入射角大约是多少度？",
        "answer": "大约 90°。贴着镜面照，光线几乎与镜面平行，而法线垂直于镜面，所以光线与法线的夹角接近 90°。",
    },
    {
        "title": "光的反射",
        "summary": "反射角总是等于入射角",
        "body": "光照到镜面上会弹回来，这叫反射。无论入射角是多少，反射角都和它一样大。",
        "figure": ("draw_reflection", {"src_x": -2.83, "src_y": 2.83, "hit_x": 0}),
        "think": "照镜子时你往左走一步，镜子里的你往哪边走？",
        "answer": "镜子里的你也往左走。像和人是关于镜面对称的，你向左移动，像也向左移动（只是左右看起来是反的）。",
    },
    {
        "title": "光的折射",
        "summary": "光从空气斜射入水中时，折射角小于入射角",
        "body": "光从空气进入水中时会拐弯，这叫折射。拐弯后光线更靠近法线，所以折射角比入射角小。",
        "figure": ("draw_refraction", {"hit_x": -1, "n2": N_WATER}),
        "think": "在水里看岸上的树，树看起来变高了还是变矮了？",
        "answer": "看起来变高了。光从树射到水面再折射进入眼睛，我们沿着折射后的光线看过去，会觉得树的位置比实际更高。",
    },
    {
        "title": "生活中的光现象",
        "summary": "镜子、潜望镜利用反射；筷子弯折、水中看鱼利用折射",
        "body": "生活中有很多光的现象。照镜子、潜望镜是反射；水中的筷子看起来弯了、在岸上看水里的鱼位置偏浅，都是折射。",
        "figure": None,
        "think": "你还见过哪些光的反射或折射现象？",
        "answer": "参考：湖面倒影、汽车后视镜、潜望镜（反射）；水中的鱼看起来比实际浅、筷子在水里像断了、放大镜聚光、雨后彩虹（折射）。",
    },
]

# ---------------------------------------------------------------------------
# 绘图函数映射
# ---------------------------------------------------------------------------
FIGURE_FUNCTIONS = {
    "draw_straight_line": draw_straight_line,
    "draw_normal_angle": draw_normal_angle,
    "draw_reflection": draw_reflection,
    "draw_refraction": draw_refraction,
}


# 核心结论气泡框样式
BUBBLE_CSS = """
<style>
.conclusion-bubble {
    position: relative;
    display: inline-block;
    background: linear-gradient(135deg, #fff9d9 0%, #ffe1ef 55%, #dbf1ff 100%);
    border: 3px solid #ffffff;
    border-radius: 26px;
    padding: 14px 40px 16px 16px;
    margin: 14px 0 28px 10px;
    font-size: 1.04rem;
    line-height: 1.6;
    color: #6b4a3a;
    box-shadow: 0 8px 20px rgba(255, 158, 196, 0.30), 0 2px 0 #ffd3e6 inset;
    animation: bubble-pop 0.4s ease-out;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.conclusion-bubble:hover {
    transform: translateY(-2px) rotate(-0.4deg);
    box-shadow: 0 12px 24px rgba(255, 158, 196, 0.38), 0 2px 0 #ffd3e6 inset;
}
.conclusion-bubble::before {
    content: "";
    position: absolute;
    left: 26px;
    bottom: -11px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #dbf1ff;
    box-shadow: 0 0 0 3px #ffffff;
}
.conclusion-bubble::after {
    content: "";
    position: absolute;
    left: 14px;
    bottom: -24px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #ffe1ef;
    box-shadow: 0 0 0 2px #ffffff;
}
.bubble-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    margin-right: 6px;
    border-radius: 50%;
    background: #ffffff;
    box-shadow: 0 3px 8px rgba(255, 150, 190, 0.35);
    font-size: 18px;
    vertical-align: -8px;
    animation: badge-wiggle 2.6s ease-in-out infinite;
}
.bubble-label {
    font-weight: 800;
    color: #ef7fa4;
    letter-spacing: 0.5px;
}
.bubble-text {
    font-weight: 700;
    color: #6b4a3a;
}
.bubble-spark {
    position: absolute;
    top: 6px;
    right: 12px;
    font-size: 14px;
    animation: twinkle 1.8s ease-in-out infinite;
}
.bubble-spark.alt {
    top: 22px;
    right: 26px;
    font-size: 11px;
    animation-delay: 0.7s;
}

/* 想一想气泡：与核心结论同一风格，配色换成天空蓝 */
.think-bubble {
    position: relative;
    background: linear-gradient(135deg, #eef7ff 0%, #e6f0ff 55%, #f3e9ff 100%);
    border: 3px solid #ffffff;
    border-radius: 26px;
    padding: 14px 40px 16px 16px;
    margin: 14px 0 28px 10px;
    font-size: 1.04rem;
    line-height: 1.6;
    color: #3f5c72;
    box-shadow: 0 8px 20px rgba(126, 178, 240, 0.30), 0 2px 0 #d6e8ff inset;
    animation: bubble-pop 0.4s ease-out;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.think-bubble:hover {
    transform: translateY(-2px) rotate(0.4deg);
    box-shadow: 0 12px 24px rgba(126, 178, 240, 0.38), 0 2px 0 #d6e8ff inset;
}
.think-bubble::before {
    content: "";
    position: absolute;
    left: 26px;
    bottom: -11px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #f3e9ff;
    box-shadow: 0 0 0 3px #ffffff;
}
.think-bubble::after {
    content: "";
    position: absolute;
    left: 14px;
    bottom: -24px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #e6f0ff;
    box-shadow: 0 0 0 2px #ffffff;
}
.think-badge {
    box-shadow: 0 3px 8px rgba(126, 178, 240, 0.38);
}
.think-label {
    font-weight: 800;
    color: #4a90d9;
    letter-spacing: 0.5px;
}
.think-text {
    font-weight: 600;
    color: #3f5c72;
}
@keyframes bubble-pop {
    from { transform: scale(0.94) translateY(4px); opacity: 0.3; }
    to   { transform: scale(1) translateY(0); opacity: 1; }
}
@keyframes badge-wiggle {
    0%, 100% { transform: rotate(-6deg); }
    50%      { transform: rotate(6deg); }
}
@keyframes twinkle {
    0%, 100% { transform: scale(1); opacity: 0.85; }
    50%      { transform: scale(1.25); opacity: 1; }
}
</style>
"""


def _render_conclusion(summary):
    """用可爱气泡框展示核心结论。"""
    st.markdown(
        f"""
<div class="conclusion-bubble">
  <span class="bubble-spark">✨</span>
  <span class="bubble-spark alt">⭐</span>
  <span class="bubble-badge">💡</span>
  <span class="bubble-label">核心结论：</span>
  <span class="bubble-text">{summary}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_think(text):
    """用与核心结论同款的气泡框展示「想一想」。"""
    st.markdown(
        f"""
<div class="think-bubble">
  <span class="bubble-spark">🫧</span>
  <span class="bubble-badge think-badge">💭</span>
  <span class="think-label">想一想：</span>
  <span class="think-text">{text}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def render_knowledge():
    """渲染知识卡片模块。"""
    st.markdown(f"## {TEXTS['module_title']}")
    st.markdown(BUBBLE_CSS, unsafe_allow_html=True)

    for i, card in enumerate(CARDS, start=1):
        with st.container(border=True):
            # 标题
            st.markdown(f"### {TEXTS['card_prefix']} {i}：{card['title']}")

            # 核心结论（气泡框）
            _render_conclusion(card["summary"])

            # 正文
            st.write(card["body"])

            # 配图
            if card["figure"] is not None:
                func_name, func_kwargs = card["figure"]
                if func_name in FIGURE_FUNCTIONS:
                    result = FIGURE_FUNCTIONS[func_name](**func_kwargs)
                    fig = result[0] if isinstance(result, tuple) else result
                    st.plotly_chart(fig, use_container_width=True, height=320)

            # 想一想
            _render_think(card["think"])

            # 答案按钮：控制参考答案是否显示
            answer_key = f"show_answer_{i}"
            is_shown = st.session_state.get(answer_key, False)
            if st.button(
                TEXTS["hide_answer"] if is_shown else TEXTS["show_answer"],
                key=f"answer_btn_{i}",
            ):
                st.session_state[answer_key] = not is_shown
                st.rerun()

            if is_shown:
                st.success(f"{TEXTS['answer_prefix']}{card['answer']}")

            # 底部提示
            st.caption(TEXTS["footer"])

        # 卡片之间用分隔线
        if i < len(CARDS):
            st.divider()
