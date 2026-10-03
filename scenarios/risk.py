"""Risk Assessment Scenario
=========================
Automatically assesses risk levels in business, credit, security scenarios

Usage:
    python main.py --risk
    python main.py --risk --data cases.json
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


def run_risk_assessment(data_source: Optional[str] = None) -> None:
    """Run risk assessment example

    Args:
        data_source: Data file path (.json/.csv/\"-\"), None uses default cases
    """
    print(
        """
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551                                                              \u2551
\u2551        \U0001f9a0 Laya AI Decision System \u2014 Risk Assessment           \u2551
\u2551                                                              \u2551
\u2551        Scenarios: Business/Credit/Security Risk Assessment    \u2551
\u2551                                                              \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
"""
    )

    questions = {
        "risk_level": {
            "type": "choice",
            "instructions": "Assess risk level",
            "criteria": {
                "high": "Fraud indicators, serious default, capital chain rupture, illegal behavior",
                "medium": "Average credit, overdue records, unstable operations",
                "low": "Good credit, stable income, compliant history",
                "safe": "Zero risk record, premium customer, strong guarantee",
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
            items = _default_cases()
    else:
        items = _default_cases()

    cases = [
        {"body": item["body"]} if isinstance(item, dict) else {"body": item}
        for item in items
    ]

    print("\n📝 Starting risk assessment...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(cases), desc="Risk") as p:
        for i, case in enumerate(cases):
            body = case["body"]

            state_errors = validate_state(body)
            if state_errors:
                risk = f"skipped({state_errors[0][:20]})"
            else:
                result = make_predict_request(body, questions)
                risk = result.get("answers", {}).get("risk_level", {}).get("choice", "unknown")
                error = result.get("error")
                if error:
                    logger.warning("Case %d failed: %s", i + 1, error)
                    risk = f"error({error[:20]})"

            print(f"{i+1:<4} {body[:40]:<40} {risk:<8}")
            results.append({"case": body, "risk_level": risk})
            p.update(1)

    _print_stats(results)

    filename = save_results(results, prefix="risk", decision_type="risk")
    print(f"\n💾 Saved: {filename}")


def _default_cases() -> list[str]:
    return [
        "New customer applying for 500k loan, no credit history, multiple platform credit checks",
        "Enterprise has been in arrears for 3 consecutive months, frequent legal representative changes",
        "Existing customer applying for credit limit increase, good historical repayment record",
        "User account abnormal login, foreign IP, frequent password changes",
        "New merchant joining platform, complete business license, has physical store",
        "Credit applicant with 85% debt-to-income ratio, 6 overdue in last half year",
    ]


def _print_stats(results: list[dict]) -> None:
    """Print risk assessment statistics."""
    if not results:
        print("\n  No results to display")
        return
    print("\n" + "=" * 70)
    print("📊 Risk Distribution:")
    print("=" * 70)
    stats: dict[str, int] = {}
    for r in results:
        level = r["risk_level"]
        stats[level] = stats.get(level, 0) + 1
    for level, count in stats.items():
        bar = "█" * count
        print(f"  {level:<12}: {count} {bar}")