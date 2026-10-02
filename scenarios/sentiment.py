"""
Sentiment Analysis Scenario (Enhanced)
======================================
Supports external data source input, structured logging output

Usage:
    python main.py --sentiment
    python main.py --sentiment --data comments.json
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


def run_sentiment_analysis(data_source: Optional[str] = None) -> None:
    """Run sentiment analysis decision

    Args:
        data_source: Data file path, None uses default data
    """
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI Decision System — Sentiment Analysis        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    questions = {
        "sentiment": {
            "type": "choice",
            "instructions": "Determine sentiment tendency",
            "criteria": {
                "very_positive": "Very satisfied, highly recommend, exceeded expectations, amazing",
                "positive": "Satisfied, recommend, good, like, pleasant",
                "neutral": "Average, ordinary, okay, normal",
                "negative": "Dissatisfied, don't recommend, poor, disappointed",
                "very_negative": "Very dissatisfied, strongly not recommend, terrible, avoid",
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
            items = _default_comments()
    else:
        items = _default_comments()

    comments = [{"body": item["body"]} if isinstance(item, dict) else {"body": item} for item in items]

    print(f"\n📝 Starting sentiment analysis ({len(comments)} items)...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(comments), desc="Sentiment") as p:
        for i, comment in enumerate(comments):
            body = comment["body"]

            state_errors = validate_state(body)
            if state_errors:
                sentiment = f"skipped({state_errors[0][:20]})"
            else:
                result = make_predict_request(body, questions)
                sentiment = result.get("answers", {}).get("sentiment", {}).get("choice", "unknown")
                if result.get("error"):
                    sentiment = f"error({result['error'][:20]})"

            print(f"  {i+1:3d}. {body[:40]:<40} → {sentiment:<15}")
            results.append({"comment": body, "sentiment": sentiment})
            p.update(1)

    _print_stats(results)

    filename = save_results(results, prefix="sentiment", decision_type="sentiment")
    print(f"\n💾 Saved: {filename}")


def _default_comments() -> list[str]:
    return [
        "This product is amazing! Great quality, highly recommend!",
        "Pretty good, used for half a month without issues",
        "Just okay, nothing special",
        "Quality is terrible, broke after two days",
        "Very dissatisfied, returned it, don't buy!",
        "Affordable price, high cost-effectiveness, worth buying",
        "Good packaging, fast logistics, five-star review",
        "Customer service attitude is good, issues handled promptly",
        "Product features are powerful, exceeded expectations",
        "Slow logistics, customer service not responsive, poor experience",
    ]


def _print_stats(results: list[dict]) -> None:
    print("\n📊 Sentiment Distribution:")
    stats: dict[str, int] = {}
    for r in results:
        s = r.get("sentiment", "unknown")
        stats[s] = stats.get(s, 0) + 1
    for sentiment, count in stats.items():
        bar = "█" * count
        print(f"  {sentiment:<15}: {count} {bar}")