"""
结构化日志工具
==============
使用 structlog 提供带 trace_id 的结构化日志

使用方式：
    from logging_utils import get_logger
    logger = get_logger()
    logger.info("request_completed", trace_id="abc123", duration_ms=42)
"""

from __future__ import annotations

import logging
import uuid
from functools import lru_cache
from typing import Any

import structlog

from config.config import get_settings


@lru_cache(maxsize=1)
def setup_logging() -> None:
    """根据配置初始化日志系统（幂等）"""
    settings = get_settings()
    log_level = getattr(logging, settings.logging.level.upper(), logging.INFO)
    use_json = settings.logging.format == "json"

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level_name,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S.%000z", utc=False),
            (
                structlog.processors.JSONRenderer()
                if use_json
                else structlog.dev.ConsoleRenderer()
            ),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(extra: dict[str, Any] | None = None) -> structlog.BoundLogger:
    """获取带可选附加字段的结构化日志器"""
    return structlog.get_logger() | structlog.contextvars.make_filtering_bound_logger(
        logging.DEBUG
    ) if extra else structlog.get_logger()


def inject_trace_id(logger: structlog.BoundLogger | None = None) -> str:
    """生成并注入 trace_id 到当前上下文，返回 trace_id 字符串"""
    import structlog.contextvars

    trace_id = uuid.uuid4().hex[:8]
    structlog.contextvars.bind_contextvars(trace_id=trace_id)
    if logger:
        logger.info("trace_started", trace_id=trace_id)
    return trace_id


def clear_trace() -> None:
    """清除当前上下文中的 trace_id（用于测试）"""
    import structlog.contextvars

    structlog.contextvars.clear_contextvars()