"""
Tests for HTTP client
=====================
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from utils.http_client import make_predict_request, make_batch_request, check_health


class TestMakePredictRequest:
    """Test make_predict_request function"""

    @patch("utils.http_client._get_session")
    def test_success_response(self, mock_session):
        """Test successful prediction request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "test"}
        mock_session.return_value.post.return_value = mock_response

        result = make_predict_request(
            "test text",
            {"category": {"type": "choice", "instructions": "test", "criteria": {"a": "b"}}}
        )

        assert result == {"result": "test"}

    @patch("utils.http_client._get_session")
    def test_http_error(self, mock_session):
        """Test HTTP error response"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_session.return_value.post.return_value = mock_response

        result = make_predict_request(
            "test text",
            {"category": {"type": "choice", "instructions": "test", "criteria": {"a": "b"}}}
        )

        assert "error" in result

    @patch("utils.http_client._get_session")
    def test_timeout_error(self, mock_session):
        """Test timeout error"""
        import requests

        mock_session.return_value.post.side_effect = requests.exceptions.Timeout()

        result = make_predict_request(
            "test text",
            {"category": {"type": "choice", "instructions": "test", "criteria": {"a": "b"}}}
        )

        assert "error" in result


class TestCheckHealth:
    """Test check_health function"""

    @patch("utils.http_client.requests.get")
    def test_health_ok(self, mock_get):
        """Test healthy service"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response

        result = check_health()

        assert result["status"] == "ok"

    @patch("utils.http_client.requests.get")
    def test_health_error(self, mock_get):
        """Test unhealthy service"""
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()

        result = check_health()

        assert result["status"] == "error"