"""
输入校验
========
基于 pydantic 的请求参数校验

使用方式：
    from validation import validate_state, validate_questions, DecisionRequest
    errors = validate_state("文本内容")
    errors = validate_questions({"category": {...}})
    req = DecisionRequest(state="文本", questions={...})
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class DecisionRequest(BaseModel):
    """完整的决策请求模型"""

    state: str
    questions: dict[str, dict[str, Any]]

    @field_validator("state", mode="before")
    @classmethod
    def strip_state(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("state 不能为空")
        if len(v) > 10000:
            raise ValueError("state 长度超过 10000")
        return v

    @field_validator("questions", mode="before")
    @classmethod
    def validate_questions(cls, v: dict) -> dict:
        if not v:
            raise ValueError("questions 不能为空")
        for key, q in v.items():
            key_str = str(key).strip()
            if not key_str:
                raise ValueError("问题 key 不能为空")
            if not isinstance(q, dict):
                raise ValueError(f"问题 {key!r} 格式错误")
            if "type" not in q:
                raise ValueError(f"问题 {key!r} 缺少 type 字段")
            if "instructions" not in q:
                raise ValueError(f"问题 {key!r} 缺少 instructions 字段")
            if "criteria" not in q:
                raise ValueError(f"问题 {key!r} 缺少 criteria 字段")
            criteria = q.get("criteria", {})
            if not criteria:
                raise ValueError(f"问题 {key!r} 的 criteria 不能为空")
            for ck, cv in criteria.items():
                if not cv or not str(cv).strip():
                    raise ValueError(f"criteria[{ck!r}] 的描述不能为空")
        return v


class BatchRequest(BaseModel):
    """批量请求模型"""

    states: list[dict[str, Any]]
    questions: dict[str, dict[str, Any]]

    @field_validator("states", mode="before")
    @classmethod
    def states_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("states 不能为空")
        return v


def validate_state(text: str) -> list[str]:
    """校验输入文本

    Returns:
        错误列表，为空表示通过
    """
    try:
        DecisionRequest(state=text, questions={"__dummy__": {"type": "choice", "instructions": "dummy", "criteria": {"a": "b"}}})
        return []
    except Exception as exc:
        return [str(exc)]


def validate_questions(questions: dict) -> list[str]:
    """校验问题定义

    Returns:
        错误列表，为空表示通过
    """
    try:
        DecisionRequest(state="x", questions=questions)
        return []
    except Exception as exc:
        return [str(exc)]


def parse_decision_request(
    state: str, questions: dict
) -> tuple[DecisionRequest | None, list[str]]:
    """解析并校验决策请求

    Returns:
        (parsed_request, errors) — errors 为空表示成功
    """
    try:
        return DecisionRequest(state=state, questions=questions), []
    except Exception as exc:
        return None, [str(exc)]