"""
Tests for HTTP client
=====================
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from utils.http_client import (
    make_predict_request,
    make_batch_request,
    check_health,
    reset_session,
)


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

    @patch("utils.http_client._get_session")
    def test_connection_error(self, mock_session):
        """Test connection error"""
        import requests

        mock_session.return_value.post.side_effect = requests.exceptions.ConnectionError()

        result = make_predict_request(
            "test text",
            {"category": {"type": "choice", "instructions": "test", "criteria": {"a": "b"}}}
        )

        assert "error" in result

    @patch("utils.http_client._get_session")
    def test_invalid_json_response(self, mock_session):
        """Test invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("No JSON")
        mock_session.return_value.post.return_value = mock_response

        result = make_predict_request(
            "test text",
            {"category": {"type": "choice", "instructions": "test", "criteria": {"a": "b"}}}
        )

        assert "error" in result
        assert "Invalid JSON" in result["error"]

    @patch("utils.http_client._get_session")
    def test_request_with_extra_params(self, mock_session):
        """Test request with model, task, lang, trace_id"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "ok"}
        mock_session.return_value.post.return_value = mock_response

        result = make_predict_request(
            "test text",
            {"category": {"type": "choice", "instructions": "test", "criteria": {"a": "b"}}},
            model="custom",
            task="classify",
            lang="en",
            trace_id="abc-123",
        )

        assert result == {"result": "ok"}
        # Verify payload
        call_kwargs = mock_session.return_value.post.call_args[1]
        payload = call_kwargs["json"]
        assert payload["model"] == "custom"
        assert payload["task"] == "classify"
        assert payload["lang"] == "en"
        assert payload["trace_id"] == "abc-123"


class TestMakeBatchRequest:
    """Test make_batch_request function"""

    @patch("utils.http_client._get_session")
    def test_batch_success(self, mock_session):
        """Test successful batch request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"body": "a", "answers": {}}, {"body": "b", "answers": {}}]
        }
        mock_session.return_value.post.return_value = mock_response

        states = [{"body": "a"}, {"body": "b"}]
        result = make_batch_request(states, {"q": {"type": "choice", "instructions": "i", "criteria": {}}})

        assert "results" in result
        assert len(result["results"]) == 2

    @patch("utils.http_client._get_session")
    def test_batch_http_error(self, mock_session):
        """Test batch HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 502
        mock_response.text = "Bad Gateway"
        mock_session.return_value.post.return_value = mock_response

        result = make_batch_request([{"body": "a"}], {"q": {"type": "choice", "instructions": "i", "criteria": {}}})

        assert "error" in result

    @patch("utils.http_client._get_session")
    def test_batch_invalid_json(self, mock_session):
        """Test batch invalid JSON"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("bad")
        mock_session.return_value.post.return_value = mock_response

        result = make_batch_request([{"body": "a"}], {"q": {"type": "choice", "instructions": "i", "criteria": {}}})

        assert "error" in result
        assert "Invalid JSON" in result["error"]

    @patch("utils.http_client._get_session")
    def test_batch_timeout(self, mock_session):
        """Test batch timeout"""
        import requests

        mock_session.return_value.post.side_effect = requests.exceptions.Timeout()

        result = make_batch_request([{"body": "a"}], {"q": {"type": "choice", "instructions": "i", "criteria": {}}})

        assert "error" in result

    @patch("utils.http_client._get_session")
    def test_batch_connection_error(self, mock_session):
        """Test batch connection error"""
        import requests

        mock_session.return_value.post.side_effect = requests.exceptions.ConnectionError()

        result = make_batch_request([{"body": "a"}], {"q": {"type": "choice", "instructions": "i", "criteria": {}}})

        assert "error" in result

    @patch("utils.http_client._get_session")
    def test_batch_autosplit(self, mock_session):
        """Test batch auto-split when exceeding max batch size"""
        # Patch config to return max_batch_size=2
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [{"body": "x", "answers": {}}]}
        mock_session.return_value.post.return_value = mock_response

        # 3 items with max_batch=2 → should split into 2 calls
        with patch("utils.http_client.get_config") as mock_get_config:
            cfg = Mock()
            cfg.performance.max_batch_size = 2
            mock_get_config.return_value = cfg

            states = [{"body": f"item_{i}"} for i in range(3)]
            result = make_batch_request(states, {"q": {"type": "choice", "instructions": "i", "criteria": {}}})

        assert "results" in result
        # Should have made 2 POST calls (3 items / 2 max = 2 chunks)
        assert mock_session.return_value.post.call_count == 2

    @patch("utils.http_client._get_session")
    def test_batch_autosplit_error_returns_error(self, mock_session):
        """Test that autosplit returns error from failed chunk"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_session.return_value.post.return_value = mock_response

        with patch("utils.http_client.get_config") as mock_get_config:
            cfg = Mock()
            cfg.performance.max_batch_size = 2
            mock_get_config.return_value = cfg

            states = [{"body": f"item_{i}"} for i in range(3)]
            result = make_batch_request(states, {"q": {"type": "choice", "instructions": "i", "criteria": {}}})

        assert "error" in result

    @patch("utils.http_client._get_session")
    def test_batch_with_trace_id(self, mock_session):
        """Test batch request with trace_id"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_session.return_value.post.return_value = mock_response

        make_batch_request(
            [{"body": "a"}],
            {"q": {"type": "choice", "instructions": "i", "criteria": {}}},
            trace_id="trace-42",
        )

        payload = mock_session.return_value.post.call_args[1]["json"]
        assert payload["trace_id"] == "trace-42"


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

    @patch("utils.http_client.requests.get")
    def test_health_custom_url(self, mock_get):
        """Test health check with custom URL"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "2.0"}
        mock_get.return_value = mock_response

        result = check_health(base_url="http://custom:9000")

        assert result["status"] == "ok"
        assert result["url"] == "http://custom:9000/health"
        assert mock_get.call_args[0][0] == "http://custom:9000/health"


class TestResetSession:
    """Test reset_session function"""

    def test_reset_session(self):
        """Test session reset"""
        # First build a session
        from utils.http_client import _get_session
        session = _get_session()
        assert session is not None

        # Reset
        reset_session()

        # Verify it's cleared
        from utils.http_client import _session
        assert _session is None