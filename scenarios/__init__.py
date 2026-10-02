"""
Scenarios Package
=================
Scenario auto-registration package

Importing this module will register all scenario modules.
"""

from __future__ import annotations

from utils.plugin import register

# Import all scenario modules to trigger registration
from scenarios.classification import run_classification_example  # noqa: F401
from scenarios.sentiment import run_sentiment_analysis  # noqa: F401
from scenarios.intention import run_intention_recognition  # noqa: F401
from scenarios.recommendation import run_product_recommendation, run_marketing_decision  # noqa: F401
from scenarios.risk import run_risk_assessment  # noqa: F401

# Register scenarios
register("classification", "Intelligent Classification", "classification", run_classification_example)
register("sentiment", "Sentiment Analysis", "sentiment", run_sentiment_analysis)
register("intention", "Intent Recognition", "intention", run_intention_recognition)
register("recommend", "Recommendation Decision", "recommendation", run_product_recommendation)
register("risk", "Risk Assessment", "risk", run_risk_assessment)