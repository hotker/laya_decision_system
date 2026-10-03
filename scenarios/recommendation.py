"""Recommendation Decision Scenario (Enhanced)
============================================
Product recommendation + marketing strategy, supports external data source

Usage:
    python main.py --recommend
    python main.py --recommend --data profiles.json
"""

from __future__ import annotations

import logging
from typing import Optional

from utils.data_source import load_data
from utils.http_client import make_predict_request
from utils.output import save_results
from utils.progress import ProgressBar
from utils.validation import validate_questions, validate_state

logger = logging.getLogger(__name__)


def run_product_recommendation(data_source: Optional[str] = None) -> None:
    """Run product recommendation decision"""
    print(
        """
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551                                                              \u2551
\u2551        \U0001f9a0 Laya AI Decision System \u2014 Product Recommendation    \u2551
\u2551                                                              \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
"""
    )

    questions = {
        "strategy": {
            "type": "choice",
            "instructions": "Select recommendation strategy",
            "criteria": {
                "quality_premium": "Premium quality, brand priority, price insensitive",
                "best_value": "Cost-effectiveness, price priority, affordable choice",
                "trend_popular": "Trending, popular styles, social-driven",
                "personalized": "Personalized customization, precise matching, user profile",
                "comprehensive": "Comprehensive recommendation, balanced quality and price, full-dimensional consideration",
            },
        }
    }

    errors = validate_questions(questions)
    if errors:
        print(f"❌ Question definition validation failed: {'; '.join(errors)}")
        return

    if data_source:
        items = load_data(data_source, text_column="body")
        if items is None:
            print("⚠️  Data file is empty, using default data")
            items = _default_profiles()
    else:
        items = _default_profiles()

    profiles = [
        {"body": item["body"]} if isinstance(item, dict) else {"body": item}
        for item in items
    ]

    print(f"\n📝 Starting product recommendation decision ({len(profiles)} items)...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(profiles), desc="Recommendation") as p:
        for i, profile in enumerate(profiles):
            body = profile["body"]

            state_errors = validate_state(body)
            if state_errors:
                strategy = f"skipped({state_errors[0][:20]})"
            else:
                result = make_predict_request(body, questions)
                strategy = result.get("answers", {}).get("strategy", {}).get("choice", "unknown")
                if result.get("error"):
                    strategy = f"error({result['error'][:20]})"

            print(f"  {i+1:<3d}. {body[:40]:<40} → {strategy:<18}")
            results.append({"profile": body, "strategy": strategy})
            p.update(1)

    _print_stats(results)

    filename = save_results(results, prefix="recommendation", decision_type="recommendation")
    print(f"\n💾 Saved: {filename}")


def run_marketing_decision(data_source: Optional[str] = None) -> None:
    """Run marketing strategy decision"""
    print(
        """
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551                                                              \u2551
\u2551        \U0001f9a0 Laya AI Decision System \u2014 Marketing Strategy        \u2551
\u2551                                                              \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
"""
    )

    questions = {
        "marketing_strategy": {
            "type": "choice",
            "instructions": "Formulate marketing strategy",
            "criteria": {
                "discount": "Discount promotion, price reduction, limited-time flash sale",
                "content": "Content marketing, recommendation, KOL cooperation",
                "social": "Social viral, group buying, share and rebate",
                "loyalty": "Membership system, points exchange, exclusive privileges",
                "personalized": "Personalized push, precise marketing, personalized for everyone",
            },
        }
    }

    errors = validate_questions(questions)
    if errors:
        print(f"❌ Question definition validation failed: {'; '.join(errors)}")
        return

    if data_source:
        items = load_data(data_source, text_column="body")
        if items is None:
            print("⚠️  Data file is empty, using default data")
            items = _default_scenarios()
    else:
        items = _default_scenarios()

    scenarios = [
        {"body": item["body"]} if isinstance(item, dict) else {"body": item}
        for item in items
    ]

    print(f"\n📝 Starting marketing strategy decision ({len(scenarios)} items)...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(scenarios), desc="Marketing") as p:
        for i, scenario in enumerate(scenarios):
            body = scenario["body"]

            state_errors = validate_state(body)
            if state_errors:
                strategy = f"skipped({state_errors[0][:20]})"
            else:
                result = make_predict_request(body, questions)
                strategy = result.get("answers", {}).get("marketing_strategy", {}).get("choice", "unknown")
                if result.get("error"):
                    strategy = f"error({result['error'][:20]})"

            print(f"  {i+1:<3d}. {body[:40]:<40} → {strategy:<18}")
            results.append({"scenario": body, "marketing_strategy": strategy})
            p.update(1)

    _print_stats(results, "marketing_strategy")

    filename = save_results(results, prefix="marketing", decision_type="marketing")
    print(f"\n💾 Saved: {filename}")


def _default_profiles() -> list[str]:
    return [
        "White-collar female, budget 5000 yuan, values quality and brand",
        "Students, budget 500 yuan, pursue cost-effectiveness",
        "Tech enthusiast, focusing on the latest tech products",
        "Family user, needs products for the whole family",
        "Fashion influencer, pursuing design and trends",
    ]


def _default_scenarios() -> list[str]:
    return [
        "New product launch, ample budget, need to quickly open the market",
        "End-of-season clearance, high inventory pressure, need quick cash return",
        "Double 11 shopping festival, fierce competition, need differentiated strategy",
        "Member day, exclusive event for existing customers",
        "Social media marketing, need to increase brand exposure",
    ]


def _print_stats(results: list[dict], key: str = "strategy") -> None:
    """Print strategy distribution statistics.

    Args:
        results: List of result dicts
        key: The key to count by (strategy or marketing_strategy)
    """
    if not results:
        print("\n  No results to display")
        return

    print(f"\n📊 Strategy Distribution:")
    stats: dict[str, int] = {}
    for r in results:
        s = r.get(key, "unknown")
        stats[s] = stats.get(s, 0) + 1
    for strategy, count in stats.items():
        bar = "█" * count
        print(f"  {strategy:<15}: {count} {bar}")