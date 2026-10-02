"""
Intent Recognition Scenario (Enhanced)
======================================
Supports external data source input

Usage:
    python main.py --intention
    python main.py --intention --data messages.json
"""

from __future__ import annotations

import logging
from typing import Optional

from utils.data_source import load_data
from utils.http_client import make_predict_request
from utils.output import save_results
from utils.progress import ProgressBar
from utils.validation import validate_state, validate_questions

logger = logging.getLogger(__name__)


def run_intention_recognition(data_source: Optional[str] = None) -> None:
    """Run intent recognition decision"""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI Decision System — Intent Recognition        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    questions = {
        "intent": {
            "type": "choice",
            "instructions": "Determine customer intent",
            "criteria": {
                "inquiry": "Inquiry, ask, understand, how, what, which",
                "complaint": "Complaint, problem, fault, broken, poor, dissatisfied",
                "purchase": "Purchase, order, want, buy, checkout",
                "after_sale": "After-sales, return, repair, customer service, refund",
                "praise": "Positive review, recommend, thank, thanks, satisfied",
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
            items = _default_messages()
    else:
        items = _default_messages()

    messages = [{"body": item["body"]} if isinstance(item, dict) else {"body": item} for item in items]

    print(f"\n📝 Starting intent recognition ({len(messages)} items)...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(messages), desc="Intent") as p:
        for i, msg in enumerate(messages):
            body = msg["body"]

            state_errors = validate_state(body)
            if state_errors:
                intent = f"skipped({state_errors[0][:20]})"
            else:
                result = make_predict_request(body, questions)
                intent = result.get("answers", {}).get("intent", {}).get("choice", "unknown")
                if result.get("error"):
                    intent = f"error({result['error'][:20]})"

            print(f"  {i+1:3d}. {body[:40]:<40} → {intent:<15}")
            results.append({"message": body, "intent": intent})
            p.update(1)

    _print_stats(results)

    filename = save_results(results, prefix="intention", decision_type="intention")
    print(f"\n💾 Saved: {filename}")


def _default_messages() -> list[str]:
    return [
        "How do you use this product? Is there a manual?",
        "The product is broken, what should I do? Need repair?",
        "I want to place an order, when can you ship?",
        "I want to return it, is that possible?",
        "Product quality is very good, thank you customer service",
        "Logistics is too slow, waited three days and not arrived yet",
        "Where can I open this feature?",
        "I want a refund, quality is too poor",
        "Recommending to your friends, very easy to use",
        "Customer service attitude is too bad, I want to complain",
    ]


def _print_stats(results: list[dict]) -> None:
    print("\n📊 Intent Distribution:")
    stats: dict[str, int] = {}
    for r in results:
        s = r.get("intent", "unknown")
        stats[s] = stats.get(s, 0) + 1
    for intent, count in stats.items():
        bar = "█" * count
        print(f"  {intent:<15}: {count} {bar}")