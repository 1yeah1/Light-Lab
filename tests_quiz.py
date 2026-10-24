"""
题库单元测试。
用纯 assert 校验题库数据完整性。
"""

from quiz import QUESTIONS


def test_minimum_questions():
    """1. QUESTIONS 至少 24 道"""
    assert len(QUESTIONS) >= 24, f"题目数量不足 24，实际 {len(QUESTIONS)}"


def test_unique_ids():
    """2. 每道题的 id 唯一"""
    ids = [q["id"] for q in QUESTIONS]
    assert len(ids) == len(set(ids)), "存在重复的 id"


def test_valid_types():
    """3. 每道题的 type 只能是 'true_false' 或 'single_choice'"""
    valid_types = {"true_false", "single_choice"}
    for q in QUESTIONS:
        assert q["type"] in valid_types, f"题目 {q['id']} 的 type 无效: {q['type']}"


def test_valid_groups():
    """4. 每道题的 group 只能是 4 个组名之一"""
    valid_groups = {"判断题·基础", "判断题·进阶", "单选题·基础", "单选题·进阶"}
    for q in QUESTIONS:
        assert q["group"] in valid_groups, f"题目 {q['id']} 的 group 无效: {q['group']}"


def test_valid_answers():
    """5. 每道题的 answer 是合法索引"""
    for q in QUESTIONS:
        assert 0 <= q["answer"] < len(q["options"]), (
            f"题目 {q['id']} 的 answer 索引无效: {q['answer']}"
        )


def test_explanation_length():
    """6. 每道题的 explanation 非空且长度 >= 10"""
    for q in QUESTIONS:
        assert len(q["explanation"]) >= 10, (
            f"题目 {q['id']} 的 explanation 太短: {q['explanation']}"
        )


def test_group_distribution():
    """7. 4 个组每组至少 6 道题"""
    from collections import Counter
    group_counts = Counter(q["group"] for q in QUESTIONS)
    for group in ["判断题·基础", "判断题·进阶", "单选题·基础", "单选题·进阶"]:
        assert group_counts[group] >= 6, (
            f"组 {group} 题目数量不足 6，实际 {group_counts[group]}"
        )


def test_true_false_options():
    """8. 判断题的 options 必须是 ['对', '错']"""
    for q in QUESTIONS:
        if q["type"] == "true_false":
            assert q["options"] == ["对", "错"], (
                f"判断题 {q['id']} 的 options 不正确: {q['options']}"
            )


def test_single_choice_options():
    """9. 单选题的 options 至少 3 个"""
    for q in QUESTIONS:
        if q["type"] == "single_choice":
            assert len(q["options"]) >= 3, (
                f"单选题 {q['id']} 的 options 数量不足 3: {q['options']}"
            )


def test_image_questions():
    """10. 至少 4 道单选题带 image 字段"""
    image_count = sum(
        1 for q in QUESTIONS
        if q["type"] == "single_choice" and q.get("image") is not None
    )
    assert image_count >= 4, f"带 image 的单选题数量不足 4，实际 {image_count}"


def test_forbidden_terms():
    """11. 全局字符串扫描：不出现禁用术语"""
    forbidden = ["折射率", "临界角", "全反射", "n₁", "n₂", "sin"]

    for q in QUESTIONS:
        # 检查 question
        for term in forbidden:
            assert term not in q["question"], (
                f"题目 {q['id']} 的 question 包含禁用术语: {term}"
            )

        # 检查 options
        for opt in q["options"]:
            for term in forbidden:
                assert term not in opt, (
                    f"题目 {q['id']} 的 options 包含禁用术语: {term}"
                )

        # 检查 explanation
        for term in forbidden:
            assert term not in q["explanation"], (
                f"题目 {q['id']} 的 explanation 包含禁用术语: {term}"
            )


if __name__ == "__main__":
    print("运行题库测试...")
    test_minimum_questions()
    print("✓ 题目数量 >= 24")
    test_unique_ids()
    print("✓ id 唯一")
    test_valid_types()
    print("✓ type 有效")
    test_valid_groups()
    print("✓ group 有效")
    test_valid_answers()
    print("✓ answer 索引有效")
    test_explanation_length()
    print("✓ explanation 长度 >= 10")
    test_group_distribution()
    print("✓ 每组至少 6 道题")
    test_true_false_options()
    print("✓ 判断题 options 正确")
    test_single_choice_options()
    print("✓ 单选题 options >= 3")
    test_image_questions()
    print("✓ 至少 4 道单选题带 image")
    test_forbidden_terms()
    print("✓ 无禁用术语")
    print("\n全部测试通过！")
