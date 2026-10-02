"""
Tests for configuration management
===================================
"""

from __future__ import annotations

import os
from pathlib import Path

from config.config import get_config, get_settings, Settings


class TestConfig:
    """Test configuration management"""

    def test_get_config_returns_settings(self):
        """Test that get_config returns Settings instance"""
        cfg = get_config()
        assert isinstance(cfg, Settings)

    def test_default_server_url(self):
        """Test default server URL"""
        cfg = get_config()
        assert cfg.server.base_url == "http://localhost:8000"

    def test_default_timeout(self):
        """Test default timeout"""
        cfg = get_config()
        assert cfg.server.timeout == 30

    def test_default_model(self):
        """Test default model"""
        cfg = get_config()
        assert cfg.server.model == "multilingual"

    def test_env_override(self):
        """Test environment variable override"""
        os.environ["LAYA_BASE_URL"] = "http://test:9000"
        cfg = get_settings()  # Get fresh settings
        assert cfg.server.base_url == "http://test:9000"
        del os.environ["LAYA_BASE_URL"]

    def test_output_directory(self):
        """Test output directory configuration"""
        cfg = get_config()
        assert cfg.output.directory == Path("./output")

    def test_max_batch_size(self):
        """Test max batch size configuration"""
        cfg = get_config()
        assert cfg.performance.max_batch_size == 100