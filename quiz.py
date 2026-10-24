"""
练习模块（判断题 + 单选题 + 多选题）。
题目与「玩一玩」中的六个场景一一对应：反射、水/玻璃中的筷子、
光进介质、三棱镜对照、三棱镜色散、镜子打靶。
"""

import streamlit as st

from plotting import (
    draw_reflection,
    draw_refraction,
    draw_chopstick,
    draw_prism_ideal,
    draw_prism_partial,
    draw_dispersion,
    draw_normal_angle,
)
from mirror_game import PRESETS, draw_mirror_game
from optics import N_WATER, N_GLASS

# ---------------------------------------------------------------------------
# 面向学生的文案
# ---------------------------------------------------------------------------
TEXTS = {
    "module_title": "✏️ 光学知识练习",
    "group_select": "选择练习组",
    "groups": ["判断题·基础", "判断题·进阶", "选择题·基础", "选择题·进阶"],
    "progress_prefix": "第",
    "progress_suffix": "题",
    "submit_button": "提交答案",
    "correct": "✅ 答对了！",
    "incorrect_prefix": "❌ 再想想~ 正确答案是：",
    "next_button": "下一题",
    "view_score": "查看成绩",
    "score_label": "正确率",
    "retry_button": "再来一组",
    "change_group": "换个组练练",
    "multi_tag": "（多选）",
    "single_hint": "选择答案",
    "multi_hint": "选择答案（可以多选）",
}

# ---------------------------------------------------------------------------
# 题库（24 道题，每题都配有图片）
# ---------------------------------------------------------------------------
QUESTIONS = [
    # ===== 判断题·基础（6 道） =====
    {
        "id": "tf_01",
        "type": "true_false",
        "group": "判断题·基础",
        "topic": "反射",
        "question": "光照射到镜面上，反射角总是等于入射角。",
        "options": ["对", "错"],
        "answers": [0],
        "explanation": "这是光的反射定律。无论入射角多大，反射角都和入射角一样大。",
        "image": {"type": "reflection", "src_x": -2.83, "src_y": 2.83, "hit_x": 0},
    },
    {
        "id": "tf_02",
        "type": "true_false",
        "group": "判断题·基础",
        "topic": "折射",
        "question": "光从空气斜射入水中时，折射角大于入射角。",
        "options": ["对", "错"],
        "answers": [1],
        "explanation": "光从空气进入水中时向法线方向拐弯，折射角比入射角小。",
        "image": {"type": "refraction", "hit_x": -1, "n2": N_WATER},
    },
    {
        "id": "tf_03",
        "type": "true_false",
        "group": "判断题·基础",
        "topic": "筷子",
        "question": "把筷子斜插进水里，看起来像折断了，这是光的折射现象。",
        "options": ["对", "错"],
        "answers": [0],
        "explanation": "光从水中出来时发生折射，进入眼睛的方向和水下实际方向不同，所以看起来弯了。",
        "image": {"type": "chopstick", "depth": 2, "n1": N_WATER},
    },
    {
        "id": "tf_04",
        "type": "true_false",
        "group": "判断题·基础",
        "topic": "生活应用",
        "question": "照镜子时，光在镜面上发生了折射。",
        "options": ["对", "错"],
        "answers": [1],
        "explanation": "照镜子时，光被镜面反射到我们的眼睛，利用的是光的反射。",
        "image": {"type": "reflection", "src_x": -4.0, "src_y": 1.5, "hit_x": -2.0},
    },
    {
        "id": "tf_05",
        "type": "true_false",
        "group": "判断题·基础",
        "topic": "色散",
        "question": "白光通过三棱镜后被分成七种颜色的光，这是光的色散现象。",
        "options": ["对", "错"],
        "answers": [0],
        "explanation": "不同颜色的光在玻璃里折射的程度不同，白光被分开成彩色光带，这就是色散。",
        "image": {"type": "dispersion", "entry_t": 0.5, "show_labels": False},
    },
    {
        "id": "tf_06",
        "type": "true_false",
        "group": "判断题·基础",
        "topic": "折射",
        "question": "光从空气斜射入玻璃时，折射角比入射角大。",
        "options": ["对", "错"],
        "answers": [1],
        "explanation": "玻璃比水更「密」光线拐弯更多，折射角仍然比入射角小，而且比射入水中时更小。",
        "image": {"type": "refraction", "hit_x": -1, "n2": N_GLASS},
    },
    # ===== 判断题·进阶（6 道） =====
    {
        "id": "tf_07",
        "type": "true_false",
        "group": "判断题·进阶",
        "topic": "法线",
        "question": "入射角是入射光线与镜面的夹角。",
        "options": ["对", "错"],
        "answers": [1],
        "explanation": "入射角是入射光线与法线的夹角，不是与镜面的夹角。法线垂直于镜面。",
        "image": {"type": "normal_angle"},
    },
    {
        "id": "tf_08",
        "type": "true_false",
        "group": "判断题·进阶",
        "topic": "法线",
        "question": "法线是真实存在的一条光线。",
        "options": ["对", "错"],
        "answers": [1],
        "explanation": "法线是为了研究方便画出来的虚线，不是真实存在的光线。它垂直于镜面。",
        "image": {"type": "normal_angle"},
    },
    {
        "id": "tf_09",
        "type": "true_false",
        "group": "判断题·进阶",
        "topic": "反射",
        "question": "光垂直射到镜面上时，反射光线沿原路返回。",
        "options": ["对", "错"],
        "answers": [0],
        "explanation": "光沿着法线方向射到镜面，入射角是 0°，反射角也是 0°，所以反射光沿原路返回。",
        "image": {"type": "reflection", "src_x": 0.0, "src_y": 3.0, "hit_x": 0.0},
    },
    {
        "id": "tf_10",
        "type": "true_false",
        "group": "判断题·进阶",
        "topic": "三棱镜",
        "question": "非全透三棱镜的界面上，光会同时发生折射和反射，形成多条方向不同的光路，而且光强逐渐减弱。",
        "options": ["对", "错"],
        "answers": [0],
        "explanation": "界面上总有一部分光折射出去、一部分光反射回棱镜里，反复几次就形成了多条越来越弱的光路。",
        "image": {"type": "prism_partial", "entry_t": 0.5, "show_labels": False},
    },
    {
        "id": "tf_11",
        "type": "true_false",
        "group": "判断题·进阶",
        "topic": "三棱镜",
        "question": "光穿过全透三棱镜后，出射光线整体向三棱镜的底部偏折。",
        "options": ["对", "错"],
        "answers": [0],
        "explanation": "光在两个界面上各折射一次，两次偏折方向相同，所以出射光偏离原方向、整体向底部偏折。",
        "image": {"type": "prism_ideal", "entry_t": 0.5, "show_labels": False},
    },
    {
        "id": "tf_12",
        "type": "true_false",
        "group": "判断题·进阶",
        "topic": "色散",
        "question": "白光经过三棱镜后，红光比紫光偏折得更厉害。",
        "options": ["对", "错"],
        "answers": [1],
        "explanation": "紫光在玻璃里折射程度最大、偏折最多；红光偏折最小。",
        "image": {"type": "dispersion", "entry_t": 0.5, "show_labels": False},
    },
    # ===== 选择题·基础（3 单选 + 3 多选） =====
    {
        "id": "sc_01",
        "type": "single_choice",
        "group": "选择题·基础",
        "topic": "折射",
        "question": "看图，光从空气斜射入水中，折射角和入射角相比？",
        "options": ["折射角大于入射角", "折射角等于入射角", "折射角小于入射角", "无法比较"],
        "answers": [2],
        "explanation": "光进入水中后向法线方向拐弯，所以折射角比入射角小。",
        "image": {"type": "refraction", "hit_x": -1, "n2": N_WATER},
    },
    {
        "id": "sc_02",
        "type": "single_choice",
        "group": "选择题·基础",
        "topic": "筷子",
        "question": "图中筷子在水里看起来折断了，这是什么现象？",
        "options": ["光的反射", "光的折射", "光的直线传播", "光的色散"],
        "answers": [1],
        "explanation": "光从水中出来时发生折射，进入眼睛的方向变了，所以看起来像折断。",
        "image": {"type": "chopstick", "depth": 2, "n1": N_WATER},
    },
    {
        "id": "sc_03",
        "type": "single_choice",
        "group": "选择题·基础",
        "topic": "镜子打靶",
        "question": "看图，激光经过几次反射才打中靶心？",
        "options": ["1 次", "2 次", "3 次", "4 次"],
        "answers": [1],
        "explanation": "激光先被第一面镜子反射，再被第二面镜子反射，共反射 2 次后命中靶心。",
        "image": {"type": "mirror_game", "preset": "level2"},
    },
    {
        "id": "mc_01",
        "type": "multiple_choice",
        "group": "选择题·基础",
        "topic": "生活应用",
        "question": "下面哪些现象主要利用了光的反射？",
        "options": ["照镜子看到自己", "用潜望镜观察", "水中的鱼看起来变浅", "雨后的彩虹"],
        "answers": [0, 1],
        "explanation": "照镜子和潜望镜都是光被镜面反射；水中的鱼、彩虹是光的折射。",
        "image": {"type": "reflection", "src_x": -2.83, "src_y": 2.83, "hit_x": 0},
    },
    {
        "id": "mc_02",
        "type": "multiple_choice",
        "group": "选择题·基础",
        "topic": "色散",
        "question": "关于白光通过三棱镜，下列说法正确的有？",
        "options": ["白光会被分成七种颜色", "紫光比红光偏折得更厉害", "这种现象叫色散", "棱镜只能让红光通过"],
        "answers": [0, 1, 2],
        "explanation": "白光被棱镜分成七色光带，紫光偏折最大、红光最小，这就是色散；棱镜并不会只放行红光。",
        "image": {"type": "dispersion", "entry_t": 0.5, "show_labels": False},
    },
    {
        "id": "mc_03",
        "type": "multiple_choice",
        "group": "选择题·基础",
        "topic": "三棱镜",
        "question": "看图，非全透三棱镜里的光发生了哪些现象？",
        "options": ["有的光从界面折射射出", "有的光在界面发生反射", "形成多条方向不同的光路", "光强始终不变"],
        "answers": [0, 1, 2],
        "explanation": "每次到达界面都是一部分折射出去、一部分反射回到棱镜里，于是出现多条光路，越往后越弱。",
        "image": {"type": "prism_partial", "entry_t": 0.5, "show_labels": False},
    },
    # ===== 选择题·进阶（3 单选 + 3 多选） =====
    {
        "id": "sc_04",
        "type": "single_choice",
        "group": "选择题·进阶",
        "topic": "折射",
        "question": "看图，光从空气斜射入玻璃。与射入水中相比，折射光线会？",
        "options": ["更靠近法线", "更远离法线", "和水中一样", "无法判断"],
        "answers": [0],
        "explanation": "玻璃的折射本领比水强，光拐弯更多，折射角更小，所以折射光线更靠近法线。",
        "image": {"type": "refraction", "hit_x": -1, "n2": N_GLASS},
    },
    {
        "id": "sc_05",
        "type": "single_choice",
        "group": "选择题·进阶",
        "topic": "色散",
        "question": "看图，白光经三棱镜散开后，偏折最小（最靠上）的是哪种颜色的光？",
        "options": ["红光", "绿光", "紫光", "白光"],
        "answers": [0],
        "explanation": "红光偏折最小，出射后位置最靠上；紫光偏折最大，位置最靠下。",
        "image": {"type": "dispersion", "entry_t": 0.5, "show_labels": False},
    },
    {
        "id": "sc_06",
        "type": "single_choice",
        "group": "选择题·进阶",
        "topic": "反射",
        "question": "看图，现在入射角是 45°。如果把入射角增大到 55°，反射角会变成多少？",
        "options": ["45°", "50°", "55°", "110°"],
        "answers": [2],
        "explanation": "反射角始终等于入射角，入射角变成 55°，反射角也是 55°。",
        "image": {"type": "reflection", "src_x": -2.83, "src_y": 2.83, "hit_x": 0},
    },
    {
        "id": "mc_04",
        "type": "multiple_choice",
        "group": "选择题·进阶",
        "topic": "折射",
        "question": "关于光从空气斜射入水或玻璃，说法正确的有？",
        "options": ["折射角总是小于入射角", "玻璃中的折射角比水中更小", "折射光线和入射光线分居法线两侧", "折射角可能大于入射角"],
        "answers": [0, 1, 2],
        "explanation": "光从空气进入水或玻璃都向法线拐弯，折射角小于入射角；玻璃比水拐得更多；两条光线在法线两侧。",
        "image": {"type": "refraction", "hit_x": -1, "n2": N_WATER},
    },
    {
        "id": "mc_05",
        "type": "multiple_choice",
        "group": "选择题·进阶",
        "topic": "筷子",
        "question": "看图，关于水中筷子的说法正确的有？",
        "options": ["筷子看起来向上折起", "这是光的折射现象", "看到的筷子尖比实际位置浅", "水面把整根筷子反射了出来"],
        "answers": [0, 1, 2],
        "explanation": "光从水中折射出来，进入眼睛的方向更平缓，我们看到的筷子尖比实际位置浅，筷子看起来向上折起。",
        "image": {"type": "chopstick", "depth": 2, "n1": N_WATER},
    },
    {
        "id": "mc_06",
        "type": "multiple_choice",
        "group": "选择题·进阶",
        "topic": "三棱镜",
        "question": "关于全透三棱镜和非全透三棱镜，说法正确的有？",
        "options": ["全透三棱镜中光只发生两次折射", "非全透三棱镜在界面同时折射和反射", "非全透的出射光有多条，光强逐渐减弱", "全透三棱镜的出射光向棱镜顶部偏折"],
        "answers": [0, 1, 2],
        "explanation": "全透棱镜只考虑折射，光在两个界面各折射一次；非全透棱镜每次到界面都会分出一部分反射光，形成多条越来越弱的光路。全透棱镜的出射光向底部偏折。",
        "image": {"type": "prism_partial", "entry_t": 0.5, "show_labels": False},
    },
]

# ---------------------------------------------------------------------------
# 绘图函数映射
# ---------------------------------------------------------------------------
IMAGE_FUNCTIONS = {
    "reflection": draw_reflection,
    "refraction": draw_refraction,
    "chopstick": draw_chopstick,
    "prism_ideal": draw_prism_ideal,
    "prism_partial": draw_prism_partial,
    "dispersion": draw_dispersion,
    "normal_angle": draw_normal_angle,
}


def _build_figure(image):
    """按题目配图配置生成 Plotly 图形。"""
    kwargs = {k: v for k, v in image.items() if k != "type"}
    if image["type"] == "mirror_game":
        preset = PRESETS[kwargs["preset"]]
        result = draw_mirror_game(preset, preset["known_solution"])
    else:
        result = IMAGE_FUNCTIONS[image["type"]](**kwargs)
    return result[0] if isinstance(result, tuple) else result


def _answer_indices(q, value):
    """把界面上的选择（选项文字或文字列表）转换成选项下标列表。"""
    if q["type"] == "multiple_choice":
        return sorted(q["options"].index(v) for v in value)
    return [q["options"].index(value)]


def _answer_text(q):
    """正确答案的文字描述（多选用顿号连接）。"""
    return "、".join(q["options"][i] for i in sorted(q["answers"]))


def render_quiz():
    """渲染练习模块。"""
    st.markdown(f"## {TEXTS['module_title']}")

    # 初始化 session_state
    st.session_state.setdefault("quiz_group", None)
    st.session_state.setdefault("quiz_index", 0)
    st.session_state.setdefault("quiz_submitted", False)
    st.session_state.setdefault("quiz_answers", [])
    st.session_state.setdefault("quiz_score", 0)

    # 组别选择
    selected_group = st.radio(
        TEXTS["group_select"],
        TEXTS["groups"],
        horizontal=True,
        key="quiz_group_radio",
        index=TEXTS["groups"].index(st.session_state.quiz_group) if st.session_state.quiz_group else 0,
    )

    # 切换组别时重置状态
    if selected_group != st.session_state.quiz_group:
        st.session_state.quiz_group = selected_group
        st.session_state.quiz_index = 0
        st.session_state.quiz_submitted = False
        st.session_state.quiz_answers = []
        st.session_state.quiz_score = 0
        st.rerun()

    # 筛选当前组的题目（按题库中的顺序）
    group_questions = [q for q in QUESTIONS if q["group"] == st.session_state.quiz_group]

    total = len(group_questions)
    index = st.session_state.quiz_index

    # 已完成所有题目
    if index >= total:
        score = st.session_state.quiz_score
        st.metric(TEXTS["score_label"], f"{score}/{total}")

        if score / total >= 0.8:
            st.balloons()

        col1, col2 = st.columns(2)
        with col1:
            if st.button(TEXTS["retry_button"], use_container_width=True):
                st.session_state.quiz_index = 0
                st.session_state.quiz_submitted = False
                st.session_state.quiz_answers = []
                st.session_state.quiz_score = 0
                st.rerun()
        with col2:
            if st.button(TEXTS["change_group"], use_container_width=True):
                st.session_state.quiz_group = None
                st.session_state.quiz_index = 0
                st.session_state.quiz_submitted = False
                st.session_state.quiz_answers = []
                st.session_state.quiz_score = 0
                st.rerun()
        return

    # 进度条
    st.progress(index / total)
    st.caption(f"{TEXTS['progress_prefix']} {index + 1} / {total} {TEXTS['progress_suffix']}")

    # 当前题目
    q = group_questions[index]

    # 题干
    tag = f"{TEXTS['multi_tag']}" if q["type"] == "multiple_choice" else ""
    st.markdown(f"**{index + 1}. {tag}{q['question']}**")

    # 配图
    if q.get("image") is not None:
        st.plotly_chart(_build_figure(q["image"]), use_container_width=True)

    # 选项
    if q["type"] == "multiple_choice":
        user_answer = st.multiselect(
            TEXTS["multi_hint"],
            q["options"],
            key=f"q_{q['id']}",
        )
    else:
        user_answer = st.radio(
            TEXTS["single_hint"],
            q["options"],
            key=f"q_{q['id']}",
            index=None,
        )

    # 提交按钮
    if not st.session_state.quiz_submitted:
        if st.button(TEXTS["submit_button"]):
            if user_answer:
                stored = _answer_indices(q, user_answer)
                st.session_state.quiz_submitted = True
                st.session_state.quiz_answers.append(stored)
                if stored == sorted(q["answers"]):
                    st.session_state.quiz_score += 1
                st.rerun()
    else:
        # 显示结果
        user_ans = st.session_state.quiz_answers[index] if index < len(st.session_state.quiz_answers) else None
        is_correct = user_ans == sorted(q["answers"])

        if is_correct:
            st.success(TEXTS["correct"])
        else:
            st.error(f"{TEXTS['incorrect_prefix']}{_answer_text(q)}")

        st.info(q["explanation"])

        # 下一题按钮
        if index < total - 1:
            if st.button(TEXTS["next_button"]):
                st.session_state.quiz_index += 1
                st.session_state.quiz_submitted = False
                st.rerun()
        else:
            if st.button(TEXTS["view_score"]):
                st.session_state.quiz_index += 1
                st.session_state.quiz_submitted = False
                st.rerun()
