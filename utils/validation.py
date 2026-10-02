"""
Input Validation
================
Request parameter validation based on pydantic

Usage:
    from validation import validate_state, validate_questions, DecisionRequest
    errors = validate_state("text content")
    errors = validate_questions({"category": {...}})
    req = DecisionRequest(state="text", questions={...})
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, field_validator


class DecisionRequest(BaseModel):
    """Complete decision request model"""

    state: str
    questions: dict[str, dict[str, Any]]

    @field_validator("state", mode="before")
    @classmethod
    def strip_state(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("state cannot be empty")
        if len(v) > 10000:
            raise ValueError("state length exceeds 10000")
        return v

    @field_validator("questions", mode="before")
    @classmethod
    def validate_questions(cls, v: dict) -> dict:
        if not v:
            raise ValueError("questions cannot be empty")
        for key, q in v.items():
            key_str = str(key).strip()
            if not key_str:
                raise ValueError("Question key cannot be empty")
            if not isinstance(q, dict):
                raise ValueError(f"Question {key!r} format error")
            if "type" not in q:
                raise ValueError(f"Question {key!r} missing type field")
            if "instructions" not in q:
                raise ValueError(f"Question {key!r} missing instructions field")
            if "criteria" not in q:
                raise ValueError(f"Question {key!r} missing criteria field")
            criteria = q.get("criteria", {})
            if not criteria:
                raise ValueError(f"criteria for question {key!r} cannot be empty")
            for ck, cv in criteria.items():
                if not cv or not str(cv).strip():
                    raise ValueError(f"criteria[{ck!r}] description cannot be empty")
        return v


class BatchRequest(BaseModel):
    """Batch request model"""

    states: list[dict[str, Any]]
    questions: dict[str, dict[str, Any]]

    @field_validator("states", mode="before")
    @classmethod
    def states_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("states cannot be empty")
        return v


def validate_state(text: str) -> list[str]:
    """Validate input text

    Returns:
        Error list, empty means passed
    """
    try:
        DecisionRequest(state=text, questions={"__dummy__": {"type": "choice", "instructions": "dummy", "criteria": {"a": "b"}}})
        return []
    except Exception as exc:
        return [str(exc)]


def validate_questions(questions: dict) -> list[str]:
    """Validate question definition

    Returns:
        Error list, empty means passed
    """
    try:
        DecisionRequest(state="x", questions=questions)
        return []
    except Exception as exc:
        return [str(exc)]


def parse_decision_request(
    state: str, questions: dict
) -> tuple[DecisionRequest | None, list[str]]:
    """Parse and validate decision request

    Returns:
        (parsed_request, errors) — errors empty means success
    """
    try:
        return DecisionRequest(state=state, questions=questions), []
    except Exception as exc:
        return None, [str(exc)]