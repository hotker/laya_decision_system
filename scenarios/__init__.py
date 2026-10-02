"""
场景模块初始化 — 自动注册所有场景
==================================

每个场景模块在模块加载时通过 register() 自注册。

使用方式：
    from plugin import register_scenarios
    register_scenarios()
"""

from __future__ import annotations

import logging

from utils.plugin import register

# 导入所有场景模块（触发模块级注册）
from scenarios.classification import run_classification_example  # noqa: F401
from scenarios.intention import run_intention_recognition  # noqa: F401
from scenarios.recommendation import (
    run_marketing_decision,  # noqa: F401
    run_product_recommendation,  # noqa: F401
)
from scenarios.risk import run_risk_assessment  # noqa: F401
from scenarios.sentiment import run_sentiment_analysis  # noqa: F401

logger = logging.getLogger(__name__)


# 注册所有场景
register(
    "classification",
    "智能分类",
    "classification",
    run_classification_example,
)
register(
    "sentiment",
    "情感分析",
    "sentiment",
    run_sentiment_analysis,
)
register(
    "intention",
    "意图识别",
    "intention",
    run_intention_recognition,
)
register(
    "product_recommendation",
    "产品推荐",
    "recommendation",
    run_product_recommendation,
)
register(
    "marketing_decision",
    "营销策略",
    "recommendation",
    run_marketing_decision,
)
register(
    "risk_assessment",
    "风险评估",
    "risk",
    run_risk_assessment,
)

logger.info(
    "all_scenarios_registered count=%d",
    len(__import__("utils.plugin", fromlist=["_SCENARIOS"])._SCENARIOS),
)