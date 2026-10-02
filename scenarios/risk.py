"""
Risk Assessment Scenario
=========================
Automatically assesses risk levels in business, credit, security scenarios

Usage:
    python main.py --risk
"""

from __future__ import annotations

import logging

from utils.http_client import make_predict_request
from utils.output import save_results

logger = logging.getLogger(__name__)


def run_risk_assessment() -> None:
    """Run risk assessment example"""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI Decision System — Risk Assessment           ║
║                                                              ║
║        Scenarios: Business/Credit/Security Risk Assessment    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
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

    cases = [
        "New customer applying for 500k loan, no credit history, multiple platform credit checks",
        "Enterprise has been in arrears for 3 consecutive months, frequent legal representative changes",
        "Existing customer applying for credit limit increase, good historical repayment record",
        "User account abnormal login, foreign IP, frequent password changes",
        "New merchant joining platform, complete business license, has physical store",
        "Credit applicant with 85% debt-to-income ratio, 6 overdue in last half year",
    ]

    print("\n📝 Starting risk assessment...")
    print("-" * 70)
    print(f"{'#':<4} {'Business Case':<40} {'Risk Level':<8}")
    print("-" * 70)

    results = []
    for i, case in enumerate(cases):
        result = make_predict_request(case, questions)
        risk = result.get("answers", {}).get("risk_level", {}).get("choice", "unknown")
        error = result.get("error")
        if error:
            logger.warning("Case %d failed: %s", i + 1, error)
            risk = f"error({error[:20]})"
        print(f"{i+1:<4} {case[:40]:<40} {risk:<8}")
        results.append({"case": case, "risk_level": risk})

    # Statistics
    print("\n" + "=" * 70)
    print("📊 Risk Distribution:")
    print("=" * 70)
    stats = {}
    for r in results:
        level = r["risk_level"]
        stats[level] = stats.get(level, 0) + 1
    for level, count in stats.items():
        bar = "█" * count
        print(f"  {level:<12}: {count} {bar}")

    filename = save_results(results, prefix="risk", decision_type="risk")
    print(f"\n💾 Saved: {filename}")