"""
Pytest Common Configuration and Fixtures
==========================================
"""

import os

import pytest


def _reset_all():
    """Reset all global state"""
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

        utils.plugin.reset()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def _reset_config():
    _reset_all()
    yield
    _reset_all()