"""
Tests for input validation
===========================
"""

from __future__ import annotations

import pytest

from utils.validation import validate_state, validate_questions, DecisionRequest


class TestValidateState:
    """Test validate_state function"""

    def test_valid_state(self):
        """Test valid input text"""
        errors = validate_state("This is valid text")
        assert errors == []

    def test_empty_state(self):
        """Test empty input text"""
        errors = validate_state("")
        assert len(errors) > 0

    def test_whitespace_only(self):
        """Test whitespace-only input"""
        errors = validate_state("   ")
        assert len(errors) > 0

    def test_long_text(self):
        """Test text exceeding maximum length"""
        long_text = "a" * 10001
        errors = validate_state(long_text)
        assert len(errors) > 0


class TestValidateQuestions:
    """Test validate_questions function"""

    def test_valid_questions(self):
        """Test valid question definition"""
        questions = {
            "category": {
                "type": "choice",
                "instructions": "test instructions",
                "criteria": {"a": "description a", "b": "description b"}
            }
        }
        errors = validate_questions(questions)
        assert errors == []

    def test_missing_type(self):
        """Test missing type field"""
        questions = {
            "category": {
                "instructions": "test",
                "criteria": {"a": "b"}
            }
        }
        errors = validate_questions(questions)
        assert len(errors) > 0

    def test_missing_instructions(self):
        """Test missing instructions field"""
        questions = {
            "category": {
                "type": "choice",
                "criteria": {"a": "b"}
            }
        }
        errors = validate_questions(questions)
        assert len(errors) > 0

    def test_missing_criteria(self):
        """Test missing criteria field"""
        questions = {
            "category": {
                "type": "choice",
                "instructions": "test"
            }
        }
        errors = validate_questions(questions)
        assert len(errors) > 0

    def test_empty_criteria(self):
        """Test empty criteria"""
        questions = {
            "category": {
                "type": "choice",
                "instructions": "test",
                "criteria": {}
            }
        }
        errors = validate_questions(questions)
        assert len(errors) > 0


class TestDecisionRequest:
    """Test DecisionRequest model"""

    def test_valid_request(self):
        """Test valid decision request"""
        req = DecisionRequest(
            state="test text",
            questions={"category": {"type": "choice", "instructions": "test", "criteria": {"a": "b"}}}
        )
        assert req.state == "test text"

    def test_invalid_state(self):
        """Test invalid state"""
        with pytest.raises(Exception):
            DecisionRequest(
                state="",
                questions={"category": {"type": "choice", "instructions": "test", "criteria": {"a": "b"}}}
            )