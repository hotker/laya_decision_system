"""
HTTP 客户端测试
===============
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from utils.http_client import check_health, make_batch_request, make_predict_request


class TestMakePredictRequest:
    """测试单条预测请求"""

    @pytest.fixture(autouse=True)
    def _mock_env(self, monkeypatch):
        monkeypatch.setenv("LAYA_BASE_URL", "http://localhost:8000")
        monkeypatch.setenv("LAYA_TIMEOUT", "5")

    def test_success_response(self):
        """正常响应"""
        with patch("utils.http_client.requests.Session.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "answers": {"category": {"choice": "quality"}}
            }
            mock_post.return_value = mock_resp

            result = make_predict_request("产品质量很好", {"cat": {"type": "choice", "instructions": "x", "criteria": {"quality": "y"}}})

            assert result["answers"]["category"]["choice"] == "quality"

    def test_http_error(self):
        """HTTP 错误码"""
        with patch("utils.http_client.requests.Session.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_resp.text = "Internal Server Error"
            mock_post.return_value = mock_resp

            result = make_predict_request("test", {"q": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}})

            assert "error" in result
            assert "HTTP 500" in result["error"]

    def test_timeout(self):
        """超时"""
        import requests

        with patch("utils.http_client.requests.Session.post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("timed out")

            result = make_predict_request("test", {"q": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}})

            assert "error" in result

    def test_connection_error(self):
        """连接错误"""
        import requests

        with patch("utils.http_client.requests.Session.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("refused")

            result = make_predict_request("test", {"q": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}})

            assert "error" in result
            assert "Connection error" in result["error"]

    def test_invalid_json(self):
        """无效 JSON"""
        with patch("utils.http_client.requests.Session.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.side_effect = ValueError("Invalid JSON")
            mock_post.return_value = mock_resp

            result = make_predict_request("test", {"q": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}})

            assert "error" in result

    def test_env_override(self, monkeypatch):
        """环境变量覆盖"""
        monkeypatch.setenv("LAYA_BASE_URL", "http://custom:9999")
        monkeypatch.setenv("LAYA_MODEL", "gpt4")

        with patch("utils.http_client.requests.Session.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"answers": {}}
            mock_post.return_value = mock_resp

            make_predict_request("test", {"q": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}})

            # 验证使用了自定义 URL 和模型
            call_args = mock_post.call_args
            assert call_args[1]["json"]["model"] == "gpt4"


class TestMakeBatchRequest:
    """测试批量请求"""

    @pytest.fixture(autouse=True)
    def _mock_env(self, monkeypatch):
        monkeypatch.setenv("LAYA_BASE_URL", "http://localhost:8000")
        monkeypatch.setenv("LAYA_TIMEOUT", "5")

    def test_success(self):
        """正常批量响应"""
        with patch("utils.http_client.requests.Session.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "results": [
                    {"answers": {"sentiment": {"choice": "positive"}}},
                    {"answers": {"sentiment": {"choice": "negative"}}},
                ]
            }
            mock_post.return_value = mock_resp

            result = make_batch_request(
                [{"body": "好"}, {"body": "差"}],
                {"sentiment": {"type": "choice", "instructions": "x", "criteria": {"positive": "a"}}},
            )

            assert len(result["results"]) == 2

    def test_autosplit(self):
        """自动分块：超过 MAX_BATCH_SIZE 时拆分"""
        monkeypatch = pytest.importorskip("pytest")
        # 设置很小的 max_batch_size 来触发分块
        with patch("utils.http_client.requests.Session.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"results": [{"answers": {}}]}
            mock_post.return_value = mock_resp

            # 150 条 > 100 默认最大值，会分 2 次
            with patch.dict("os.environ", {"LAYA_MAX_BATCH_SIZE": "100"}):
                # 需要先重置配置
                import config.config, utils.http_client

                config.config._settings = None
                utils.http_client.reset_session()

                result = make_batch_request(
                    [{"body": f"item{i}"} for i in range(150)],
                    {"sentiment": {"type": "choice", "instructions": "x", "criteria": {"positive": "a"}}},
                )

                # 应该被拆分了
                assert mock_post.call_count >= 2

    def test_error_response(self):
        """批量接口错误"""
        with patch("utils.http_client.requests.Session.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 422
            mock_resp.text = "Validation error"
            mock_post.return_value = mock_resp

            result = make_batch_request(
                [{"body": "test"}],
                {"sentiment": {"type": "choice", "instructions": "x", "criteria": {"a": "b"}}},
            )

            assert "error" in result


class TestCheckHealth:
    """测试健康检查"""

    def test_health_ok(self):
        """服务正常"""
        with patch("utils.http_client.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"status": "ok", "version": "1.0"}
            mock_get.return_value = mock_resp

            result = check_health()

            assert result["status"] == "ok"
            assert "url" in result

    def test_health_connection_error(self):
        """连接失败"""
        with patch("utils.http_client.requests.get") as mock_get:
            mock_get.side_effect = Exception("refused")

            result = check_health()

            assert result["status"] == "error"

    def test_custom_url(self):
        """自定义 URL"""
        with patch("utils.http_client.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"status": "ok"}
            mock_get.return_value = mock_resp

            result = check_health(base_url="http://custom:9999")

            mock_get.assert_called_once_with("http://custom:9999/health", timeout=10)
            assert result["url"] == "http://custom:9999/health"