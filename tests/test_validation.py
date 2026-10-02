"""
输入校验测试
============
"""

from utils.validation import (
    DecisionRequest,
    parse_decision_request,
    validate_questions,
    validate_state,
)


class TestValidateState:
    """测试输入文本校验"""

    def test_valid_state(self):
        """有效文本通过"""
        assert validate_state("这是一个有效的文本") == []

    def test_empty_state(self):
        """空字符串失败"""
        errors = validate_state("")
        assert len(errors) > 0

    def test_whitespace_only(self):
        """纯空格失败"""
        errors = validate_state("   ")
        # 纯空格 strip 后为空，pydantic min_length=1 会拦截
        assert len(errors) > 0

    def test_long_text(self):
        """超长文本失败（>10000 字符）"""
        long_text = "x" * 10001
        errors = validate_state(long_text)
        assert len(errors) > 0

    def test_trims_whitespace(self):
        """trim 前后空格"""
        errors = validate_state("  测试  ")
        assert errors == []


class TestValidateQuestions:
    """测试问题定义校验"""

    def test_valid_questions(self):
        """有效问题定义通过"""
        q = {
            "category": {
                "type": "choice",
                "instructions": "选择类别",
                "criteria": {"a": "标准A", "b": "标准B"},
            }
        }
        assert validate_questions(q) == []

    def test_empty_questions(self):
        """空 questions 失败"""
        assert len(validate_questions({})) > 0

    def test_missing_type(self):
        """缺少 type 字段失败"""
        q = {"cat": {"instructions": "x", "criteria": {"a": "b"}}}
        errors = validate_questions(q)
        assert any("type" in e for e in errors)

    def test_missing_criteria(self):
        """缺少 criteria 字段失败"""
        q = {"cat": {"type": "choice", "instructions": "x"}}
        errors = validate_questions(q)
        assert any("criteria" in e for e in errors)

    def test_empty_criteria(self):
        """空 criteria 失败"""
        q = {"cat": {"type": "choice", "instructions": "x", "criteria": {}}}
        errors = validate_questions(q)
        assert len(errors) > 0

    def test_empty_criteria_value(self):
        """criteria 值为空字符串失败"""
        q = {"cat": {"type": "choice", "instructions": "x", "criteria": {"a": ""}}}
        errors = validate_questions(q)
        assert len(errors) > 0

    def test_empty_key(self):
        """空 key 失败"""
        q = {"": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}}
        errors = validate_questions(q)
        assert len(errors) > 0


class TestDecisionRequest:
    """测试完整请求模型"""

    def test_valid_request(self):
        """有效请求"""
        req = DecisionRequest(
            state="测试文本",
            questions={"cat": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}},
        )
        assert req.state == "测试文本"

    def test_invalid_state(self):
        """无效 state"""
        try:
            DecisionRequest(
                state="",
                questions={"cat": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}},
            )
            assert False, "Should raise"
        except Exception as e:
            assert len(str(e)) > 0

    def test_strip_state(self):
        """自动 trim"""
        req = DecisionRequest(
            state="  hello  ",
            questions={"cat": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}},
        )
        assert req.state == "hello"


class TestParseDecisionRequest:
    """测试请求解析"""

    def test_parse_success(self):
        """解析成功"""
        req, errors = parse_decision_request(
            "测试",
            {"cat": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}},
        )
        assert req is not None
        assert errors == []

    def test_parse_failure(self):
        """解析失败"""
        req, errors = parse_decision_request("", {"cat": {"type": "choice", "instructions": "x", "criteria": {}}})
        assert req is None
        assert len(errors) > 0