"""
Pytest 公共配置和 fixtures
"""

import os
import sys
from pathlib import Path

import pytest

# 确保项目根在路径中
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))


def _reset_all():
    """重置所有全局状态"""
    for key in list(os.environ.keys()):
        if key.startswith("LAYA_"):
            del os.environ[key]

    import config.config

    config.config._settings = None

    try:
        import utils.http_client

        utils.http_client.reset_session()
    except Exception:
        pass

    try:
        import utils.plugin

        utils.plugin._SCENARIOS.clear()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def _reset_config():
    _reset_all()
    yield
    _reset_all()