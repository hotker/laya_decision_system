"""
Logging Utilities
=================
Structured logging with JSON output and trace_id support

Usage:
    from logging_utils import setup_logging, get_logger
    logger = get_logger(__name__)
    logger.info("message", extra_data="value")
"""

from __future__ import annotations

import logging
from typing import Any

import structlog


def setup_logging(
    level: str = "INFO",
    fmt: str = "json",
) -> None:
    """Setup structured logging

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        fmt: Log format (json, text)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    if fmt == "json":
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def get_logger(name: str) -> Any:
    """Get logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    if logging.root.manager.loggerDict.get(name):
        return logging.getLogger(name)
    return structlog.get_logger(name)