"""
配置测试
========
验证环境变量覆盖和默认值
"""

import os
from pathlib import Path

import pytest

from config.config import (
    Settings,
    get_config,
    get_output,
    get_performance,
    get_server,
)


class TestSettingsDefaults:
    """测试默认配置值"""

    @pytest.fixture(autouse=True)
    def _clear(self):
        import config.config

        config.config._settings = None

    def test_default_base_url(self):
        s = Settings()
        assert s.server.base_url == "http://localhost:8000"

    def test_default_timeout(self):
        s = Settings()
        assert s.server.timeout == 30

    def test_default_model(self):
        s = Settings()
        assert s.server.model == "multilingual"

    def test_default_retry(self):
        s = Settings()
        assert s.performance.retry_times == 3
        assert s.performance.retry_delay == 1.0
        assert s.performance.retry_backoff_factor == 2.0

    def test_default_max_batch(self):
        s = Settings()
        assert s.performance.max_batch_size == 100

    def test_default_output_dir(self):
        s = Settings()
        assert s.output.directory == Path("./output")


class TestEnvOverride:
    """测试环境变量覆盖"""

    @pytest.fixture(autouse=True)
    def _clear(self):
        import config.config

        config.config._settings = None

    def test_base_url_env(self, monkeypatch):
        monkeypatch.setenv("LAYA_BASE_URL", "http://staging:8080")
        s = Settings()
        assert s.server.base_url == "http://staging:8080"

    def test_timeout_env(self, monkeypatch):
        monkeypatch.setenv("LAYA_TIMEOUT", "60")
        s = Settings()
        assert s.server.timeout == 60

    def test_model_env(self, monkeypatch):
        monkeypatch.setenv("LAYA_MODEL", "gpt4")
        s = Settings()
        assert s.server.model == "gpt4"

    def test_max_batch_env(self, monkeypatch):
        monkeypatch.setenv("LAYA_MAX_BATCH_SIZE", "50")
        s = Settings()
        assert s.performance.max_batch_size == 50

    def test_log_level_env(self, monkeypatch):
        monkeypatch.setenv("LAYA_LOG_LEVEL", "DEBUG")
        s = Settings()
        assert s.logging.level == "DEBUG"

    def test_output_dir_env(self, monkeypatch):
        monkeypatch.setenv("LAYA_OUTPUT_DIR", "/tmp/test_output")
        s = Settings()
        assert str(s.output.directory) == "/tmp/test_output"


class TestGetConfig:
    """测试 get_config() 单例"""

    @pytest.fixture(autouse=True)
    def _clear(self):
        import config.config

        config.config._settings = None

    def test_singleton(self):
        """get_config() 返回相同实例"""
        a = get_config()
        b = get_config()
        assert a is b

    def test_get_server(self):
        s = get_server()
        assert s.base_url == "http://localhost:8000"

    def test_get_performance(self):
        p = get_performance()
        assert p.retry_times == 3