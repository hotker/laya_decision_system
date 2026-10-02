"""
Laya AI 决策系统配置
=====================
集中管理所有配置参数，支持 .env 文件和环境变量覆盖

环境变量前缀: LAYA_
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

SYSTEM_NAME = "Laya AI 决策系统"
VERSION = "2.0.0"


# ─── 模型定义 ──────────────────────────────────────────────────


class LayaServerConfig(BaseSettings):
    """Laya AI 服务连接配置"""

    base_url: str = Field(
        default="http://localhost:8000",
        validation_alias="LAYA_BASE_URL",
        description="Laya 服务基础地址",
    )
    timeout: int = Field(default=30, validation_alias="LAYA_TIMEOUT", ge=1, le=300)
    model: str = Field(
        default="multilingual",
        validation_alias="LAYA_MODEL",
        description="默认使用的模型名称",
    )
    task: Optional[str] = Field(default=None, validation_alias="LAYA_TASK")
    lang: Optional[str] = Field(default=None, validation_alias="LAYA_LANG")


class OutputConfig(BaseSettings):
    """输出配置"""

    directory: Path = Field(
        default=Path("./output"),
        validation_alias="LAYA_OUTPUT_DIR",
    )
    formats: List[str] = Field(default_factory=lambda: ["json", "csv"])
    keep_days: int = Field(default=30, ge=1)
    max_files: int = Field(default=100, ge=1)


class PerformanceConfig(BaseSettings):
    """性能与容错配置"""

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
    """日志配置"""

    level: str = Field(default="INFO", validation_alias="LAYA_LOG_LEVEL")
    format: str = Field(
        default="json",
        validation_alias="LAYA_LOG_FORMAT",
        description="日志格式: json | text",
    )


# ─── 全局配置实例 ──────────────────────────────────────────────


class Settings(BaseSettings):
    """顶层配置，读取 LAYA_ 前缀的环境变量"""

    server: LayaServerConfig = Field(default_factory=LayaServerConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # 系统元信息（不作为配置项，但可通过环境变量覆盖）
    system_name: str = Field(
        default=SYSTEM_NAME,
        validation_alias="LAYA_SYSTEM_NAME",
    )
    version: str = Field(default=VERSION, validation_alias="LAYA_VERSION")

    model_config = SettingsConfigDict(env_prefix="LAYA_")


# 全局单例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局配置单例（惰性初始化）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# 别名
get_config = get_settings


def get_server() -> LayaServerConfig:
    return get_settings().server


def get_performance() -> PerformanceConfig:
    return get_settings().performance


def get_output() -> OutputConfig:
    return get_settings().output


# ─── 向后兼容字典（遗留代码使用） ──────────────────────────────

LAYA_CONFIG: dict = {
    "BASE_URL": "http://localhost:8000",
    "PREDICT_URL": "http://localhost:8000/predict",
    "BATCH_URL": "http://localhost:8000/predict/batch",
    "HEALTH_URL": "http://localhost:8000/health",
    "TIMEOUT": 30,
    "MODEL": "multilingual",
    "TASK": None,
    "LANG": None,
}

DECISION_TYPES: dict = {
    "classification": {
        "name": "智能分类",
        "description": "文本/评论/内容自动分类",
        "use_cases": ["客户评论分类", "工单自动分配", "内容审核", "邮件分类"],
    },
    "sentiment": {
        "name": "情感分析",
        "description": "情感倾向自动识别",
        "use_cases": ["产品评价分析", "舆情监控", "品牌口碑分析", "用户反馈分析"],
    },
    "intention": {
        "name": "意图识别",
        "description": "用户意图自动识别",
        "use_cases": ["客服意图识别", "搜索意图分析", "营销意图判断", "需求理解"],
    },
    "risk": {
        "name": "风险评估",
        "description": "风险等级自动评分",
        "use_cases": ["信贷风险评估", "欺诈检测", "合规审核", "安全预警"],
    },
    "recommendation": {
        "name": "推荐决策",
        "description": "个性化推荐与策略制定",
        "use_cases": ["产品推荐", "营销策略制定", "个性化推送", "内容推荐"],
    },
}

OUTPUT_CONFIG: dict = {
    "DIR": Path("./output"),
    "FORMATS": ["json", "csv"],
    "KEEP_DAYS": 30,
    "MAX_FILES": 100,
    "system_name": SYSTEM_NAME,
    "version": VERSION,
}

PERFORMANCE_CONFIG: dict = {
    "MAX_BATCH_SIZE": 100,
    "MAX_CONCURRENT_REQUESTS": 5,
    "REQUEST_TIMEOUT": 60,
    "RETRY_TIMES": 3,
    "RETRY_DELAY": 1.0,
}