"""
Laya AI Decision System Configuration
=======================================
Centralized configuration management, supports .env files and environment variable overrides

Environment Variable Prefix: LAYA_
  LAYA_BASE_URL=http://localhost:8000
  LAYA_TIMEOUT=30
  LAYA_MODEL=multilingual
  LAYA_OUTPUT_DIR=./output
  LAYA_MAX_BATCH_SIZE=100
  LAYA_RETRY_TIMES=3
  LAYA_LOG_LEVEL=INFO
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SYSTEM_NAME = "Laya AI Decision System"
VERSION = "2.0.0"


# ─── Model Definitions ──────────────────────────────────────────


class LayaServerConfig(BaseSettings):
    """Laya AI service connection configuration"""

    base_url: str = Field(
        default="http://localhost:8000",
        validation_alias="LAYA_BASE_URL",
        description="Laya service base URL",
    )
    timeout: int = Field(default=30, validation_alias="LAYA_TIMEOUT", ge=1, le=300)
    model: str = Field(
        default="multilingual",
        validation_alias="LAYA_MODEL",
        description="Default model name to use",
    )
    task: Optional[str] = Field(default=None, validation_alias="LAYA_TASK")
    lang: Optional[str] = Field(default=None, validation_alias="LAYA_LANG")


class OutputConfig(BaseSettings):
    """Output configuration"""

    directory: Path = Field(
        default=Path("./output"),
        validation_alias="LAYA_OUTPUT_DIR",
    )
    formats: List[str] = Field(default_factory=lambda: ["json", "csv"])
    keep_days: int = Field(default=30, ge=1)
    max_files: int = Field(default=100, ge=1)


class PerformanceConfig(BaseSettings):
    """Performance and fault tolerance configuration"""

    max_batch_size: int = Field(
        default=100,
        validation_alias="LAYA_MAX_BATCH_SIZE",
        ge=1,
        le=10000,
    )
    max_concurrent_requests: int = Field(
        default=5,
        validation_alias="LAYA_MAX_CONCURRENT_REQUESTS",
        ge=1,
        le=50,
    )
    request_timeout: int = Field(default=60, validation_alias="LAYA_REQUEST_TIMEOUT", ge=1)
    retry_times: int = Field(
        default=3,
        validation_alias="LAYA_RETRY_TIMES",
        ge=0,
        le=10,
    )
    retry_delay: float = Field(
        default=1.0,
        validation_alias="LAYA_RETRY_DELAY",
        ge=0.1,
        le=30.0,
    )
    retry_backoff_factor: float = Field(
        default=2.0,
        validation_alias="LAYA_RETRY_BACKOFF_FACTOR",
        ge=1.0,
        le=5.0,
    )


class LoggingConfig(BaseSettings):
    """Logging configuration"""

    level: str = Field(default="INFO", validation_alias="LAYA_LOG_LEVEL")
    format: str = Field(
        default="json",
        validation_alias="LAYA_LOG_FORMAT",
        description="Log format: json | text",
    )


# ─── Global Configuration Instance ──────────────────────────────


class Settings(BaseSettings):
    """Top-level configuration, reads LAYA_ prefixed environment variables"""

    server: LayaServerConfig = Field(default_factory=LayaServerConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # System metadata (not a configuration item, but overridable via env vars)
    system_name: str = Field(
        default=SYSTEM_NAME,
        validation_alias="LAYA_SYSTEM_NAME",
    )
    version: str = Field(default=VERSION, validation_alias="LAYA_VERSION")

    model_config = SettingsConfigDict(env_prefix="LAYA_")


# Global singleton
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global configuration singleton (lazy initialization)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Alias
get_config = get_settings


def get_server() -> LayaServerConfig:
    return get_settings().server


def get_performance() -> PerformanceConfig:
    return get_settings().performance


def get_output() -> OutputConfig:
    return get_settings().output


# ─── Backward Compatible Accessors (for legacy code) ────────────
# These provide dictionary-style access to settings. New code should
# use get_config().server / .performance / .output / .logging directly.


def _build_decision_types() -> dict:
    """Build DECISION_TYPES from registered scenarios and static definitions."""
    from utils.plugin import list_scenarios

    result: dict = {}
    for s in list_scenarios():
        result[s["decision_type"]] = {
            "name": s["title"],
            "description": f"Managed by {s['name']} scenario",
            "use_cases": [],
        }
    # Fallback static definitions for scenarios not yet auto-registered
    fallback = {
        "classification": {
            "name": "Intelligent Classification",
            "description": "Automatic classification of text/comments/content",
            "use_cases": ["Customer review classification", "Ticket auto-assignment"],
        },
        "sentiment": {
            "name": "Sentiment Analysis",
            "description": "Automatic sentiment tendency recognition",
            "use_cases": ["Product review analysis", "Public opinion monitoring"],
        },
        "intention": {
            "name": "Intent Recognition",
            "description": "Automatic user intent recognition",
            "use_cases": ["Customer service intent recognition", "Search intent analysis"],
        },
        "risk": {
            "name": "Risk Assessment",
            "description": "Automatic risk level scoring",
            "use_cases": ["Credit risk assessment", "Fraud detection"],
        },
        "recommendation": {
            "name": "Recommendation Decision",
            "description": "Personalized recommendation and strategy formulation",
            "use_cases": ["Product recommendation", "Marketing strategy formulation"],
        },
    }
    result.update(fallback)
    return result


DECISION_TYPES: dict = _build_decision_types()


OUTPUT_CONFIG: dict = {}


def _build_output_config() -> dict:
    cfg = get_output()
    return {
        "DIR": cfg.directory,
        "FORMATS": cfg.formats,
        "KEEP_DAYS": cfg.keep_days,
        "MAX_FILES": cfg.max_files,
        "system_name": get_settings().system_name,
        "version": get_settings().version,
    }


def get_output_config() -> dict:
    return _build_output_config()


PERFORMANCE_CONFIG: dict = {}


def _build_performance_config() -> dict:
    cfg = get_performance()
    return {
        "MAX_BATCH_SIZE": cfg.max_batch_size,
        "MAX_CONCURRENT_REQUESTS": cfg.max_concurrent_requests,
        "REQUEST_TIMEOUT": cfg.request_timeout,
        "RETRY_TIMES": cfg.retry_times,
        "RETRY_DELAY": cfg.retry_delay,
    }


def get_performance_config() -> dict:
    return _build_performance_config()


# Convenience alias for direct access (eager evaluation at module load)
OUTPUT_CONFIG.update(_build_output_config())
PERFORMANCE_CONFIG.update(_build_performance_config())