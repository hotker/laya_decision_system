"""Intelligent Classification Scenario (Enhanced)
==============================================
Supports external data source input, structured logging output

Usage:
    python main.py --classification                 # Default data
    python main.py --classification --data reviews.json  # External data
    python main.py --classification --data reviews.csv     # CSV data
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


def run_classification_example(data_source: Optional[str] = None) -> None:
    """Run intelligent classification decision

    Args:
        data_source: Data file path (.json / .csv / "-"), None uses default data
    """
    print(
        """
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551                                                              \u2551
\u2551        \U0001f9a0 Laya AI Decision System \u2014 Intelligent Classification \u2551
\u2551                                                              \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
"""
    )

    questions = {
        "category": {
            "type": "choice",
            "instructions": "Determine review category",
            "criteria": {
                "quality": "Quality, workmanship, durability, material, craftsmanship",
                "price": "Price, expensive, cheap, cost-effective, value",
                "service": "Customer service, logistics, installation, after-sales, shipping",
                "function": "Features, smart, operation, effect, experience",
                "design": "Appearance,颜值，design, style, color",
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
            items = _default_reviews()
    else:
        items = _default_reviews()

    reviews = [
        {"body": item["body"]} if isinstance(item, dict) else {"body": item}
        for item in items
    ]

    print(f"\n📝 Starting classification decision ({len(reviews)} items)...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(reviews), desc="Classification") as p:
        for i, review in enumerate(reviews):
            body = review["body"]

            state_errors = validate_state(body)
            if state_errors:
                category = f"skipped({state_errors[0][:20]})"
            else:
                result = make_predict_request(body, questions)
                category = result.get("answers", {}).get("category", {}).get("choice", "unknown")
                if result.get("error"):
                    logger.warning("review %d HTTP error: %s", i + 1, result["error"])
                    category = f"error({result['error'][:20]})"

            print(f"  {i+1:<3d}. {body[:40]:<40} → {category:<10}")
            results.append({"review": body, "category": category})
            p.update(1)

    _print_stats(results, "category")

    filename = save_results(results, prefix="classification", decision_type="classification")
    print(f"\n💾 Saved: {filename}")


def _default_reviews() -> list[str]:
    return [
        "This product is of good quality, fine workmanship, premium material",
        "The price is too expensive, not cost-effective, not worth buying",
        "Customer service attitude is good, logistics is also fast, installation master is professional",
        "Smart features are very practical, easy to operate, good experience",
        "Simple and elegant appearance design, like the color, matches well at home",
        "Product received with damage, customer service handled promptly, gave compensation",
        "Used for three months, no problems, reliable quality",
        "Logistics was too slow, waited half a month to arrive",
        "Product features are powerful, smart linkage is convenient",
        "High颜值，good workmanship, worth recommending",
    ]


def _print_stats(results: list[dict], key: str = "category") -> None:
    """Print classification statistics.

    Args:
        results: List of result dicts
        key: The key to count by
    """
    if not results:
        print("\n  No results to display")
        return

    print("\n" + "=" * 70)
    title = f"📊 {key.title()} Results Statistics"
    print(title)
    print("=" * 70)
    stats: dict[str, int] = {}
    for r in results:
        cat = r.get(key, "unknown")
        stats[cat] = stats.get(cat, 0) + 1
    for cat, count in stats.items():
        pct = count / len(results) * 100
        bar = "█" * int(pct / 5)
        print(f"  {cat:<12}: {count:3d} ({pct:5.1f}%) {bar}")