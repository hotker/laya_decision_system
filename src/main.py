"""
🧠 Laya AI Decision System v2.0 — Main Entry
============================================

Enhanced CLI with:
  - Plugin-based scenario registration
  - External data source (--data)
  - Progress bar display
  - Structured logging
  - Output format selection (--format csv)

Usage:
  python src/main.py                  # Interactive menu
  python src/main.py --classification # Intelligent classification
  python src/main.py --batch          # Batch processing
  python src/main.py --data data.json # External data
  python src/main.py --format csv     # CSV output
  python src/main.py --health         # Health check
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

# Import all scenario modules to trigger registration
import scenarios  # noqa: F401
from config.config import DECISION_TYPES, SYSTEM_NAME, VERSION, get_config
from utils.data_source import load_data
from utils.http_client import check_health
from utils.output import clean_all, clean_old_files, list_output_files
from utils.plugin import list_scenarios


def show_menu() -> None:
    """Display main menu"""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI Decision System v2.0                       ║
║                                                              ║
║  Modules:                                                    ║
║                                                              ║
║  1️⃣  Intelligent Classification — Text/comment auto-classify ║
║  2️⃣  Sentiment Analysis — Emotion tendency recognition      ║
║  3️⃣  Intent Recognition — User intent auto-recognition      ║
║  4️⃣  Recommendation Decision — Personalized strategies      ║
║  5️⃣  Risk Assessment — Risk level auto-scoring              ║
║  6️⃣  Batch Processing — Batch decision analysis             ║
║  7️⃣  Data Management — View/cleanup decision data           ║
║  0️⃣  Exit System                                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )


def setup_logging() -> None:
    """Initialize logging"""
    cfg = get_config()
    level = getattr(logging, cfg.logging.level.upper(), logging.INFO)

    if cfg.logging.format == "json":
        try:
            import structlog

            structlog.configure(
                processors=[
                    structlog.contextvars.merge_contextvars,
                    structlog.processors.add_log_level,
                    structlog.processors.StackInfoRenderer(),
                    structlog.dev.set_exc_info,
                    structlog.processors.TimeStamper(
                        fmt="%Y-%m-%dT%H:%M:%S.%000z", utc=False
                    ),
                    structlog.processors.JSONRenderer(),
                ],
                wrapper_class=structlog.make_filtering_bound_logger(level),
                context_class=dict,
                logger_factory=structlog.PrintLoggerFactory(),
                cache_logger_on_first_use=True,
            )
        except ImportError:
            pass

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class DecisionSystem:
    """Decision system main controller"""

    def __init__(self, data_source: str | None = None, output_format: str = "json"):
        self.data_source = data_source
        self.output_format = output_format

    def run_classification(self) -> None:
        from scenarios.classification import run_classification_example
        run_classification_example(self.data_source)

    def run_sentiment(self) -> None:
        from scenarios.sentiment import run_sentiment_analysis
        run_sentiment_analysis(self.data_source)

    def run_intention(self) -> None:
        from scenarios.intention import run_intention_recognition
        run_intention_recognition(self.data_source)

    def run_recommend(self) -> None:
        from scenarios.recommendation import (
            run_marketing_decision,
            run_product_recommendation,
        )
        run_product_recommendation(self.data_source)
        print("\n" + "=" * 70 + "\n")
        run_marketing_decision(self.data_source)

    def run_risk(self) -> None:
        from scenarios.risk import run_risk_assessment
        run_risk_assessment()

    def run_batch(self) -> None:
        """Batch processing: use default data or external data source"""
        from utils.http_client import make_batch_request
        from utils.output import save_results

        print(
            """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI Decision System — Batch Processing         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        )

        # Load data
        if self.data_source:
            items = load_data(self.data_source, text_column="body")
            if items is None:
                print("⚠️  Data file is empty, using default data")
                items = _default_batch_items()
        else:
            items = _default_batch_items()

        states = [{"body": item["body"]} if isinstance(item, dict) else {"body": item} for item in items]

        questions = {
            "sentiment": {
                "type": "choice",
                "instructions": "Analyze sentiment tendency",
                "criteria": {
                    "positive": "Good review, recommended, good quality, cost-effective",
                    "negative": "Bad review, problem, poor, expensive, bad",
                    "neutral": "Average, ordinary, okay",
                },
            }
        }

        print(f"\n📝 Starting batch processing ({len(states)} items)...")
        print("-" * 70)

        t0 = time.monotonic()
        result = make_batch_request(states, questions)
        elapsed = time.monotonic() - t0

        if result and "results" in result:
            for i, item in enumerate(result["results"]):
                answers = item.get("answers", {})
                sentiment = answers.get("sentiment", {}).get("choice", "unknown")
                confidence = item.get("confidence", 0)
                body = states[i]["body"] if i < len(states) else ""
                print(
                    f"  {i+1}. {body[:40]:<40} {sentiment:<8} (Confidence: {confidence:.2f})"
                )

            # Collect results
            results_data = []
            for i, item in enumerate(result["results"]):
                results_data.append(
                    {
                        "index": i + 1,
                        "state": states[i]["body"] if i < len(states) else "",
                        "answers": item.get("answers", {}),
                        "confidence": item.get("confidence", 0),
                    }
                )

            filename = save_results(
                results_data, prefix="batch_all", decision_type="batch"
            )
            print(f"\n💾 Saved: {filename}")
            print(f"⏱  Elapsed: {elapsed:.2f}s ({len(result['results'])} items, {elapsed/len(result['results'])*1000:.0f}ms/item)")
        else:
            error_msg = result.get("error", "Unknown error")
            print(f"❌ Batch processing failed: {error_msg}")

    def run_data_management(self) -> None:
        print("\n📁 Data Management")
        print("-" * 60)

        files = list_output_files()
        if files:
            print("\n📄 Decision files:")
            for f in files:
                size = f.stat().st_size / 1024
                print(f"  • {f.name} ({size:.1f} KB)")
        else:
            print("❌ No decision files")

        print("\nManagement options:")
        print("  1. Delete old files (keep latest 10)")
        print("  2. Clear all data")

        choice = input("\nSelect operation [1-2] or press Enter to exit:").strip()

        if choice == "1":
            deleted = clean_old_files(keep_count=10)
            if deleted > 0:
                print(f"  Deleted {deleted} old files")
            else:
                print("  Nothing to clean")
        elif choice == "2":
            confirm = input("⚠️  Confirm to clear all data? (y/n): ").strip().lower()
            if confirm == "y":
                deleted = clean_all()
                print(f"  ✅ Cleared {deleted} files")


def _default_batch_items() -> list[str]:
    return [
        "Product is good, fast shipping, good customer service",
        "Quality is terrible, broke after two days, return it",
        "Affordable price, cost-effective, worth buying",
        "Good packaging, no damage, five-star review",
        "Shipping too slow, waited half a month, poor experience",
    ]


# ─── Main function ──────────────────────────────────────────────


def main() -> None:
    """Main entry point"""
    setup_logging()

    parser = argparse.ArgumentParser(
        description=f"{SYSTEM_NAME} v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python src/main.py                     # Interactive menu
  python src/main.py --classification    # Intelligent classification
  python src/main.py --sentiment         # Sentiment analysis
  python src/main.py --intention         # Intent recognition
  python src/main.py --recommend         # Recommendation decision
  python src/main.py --risk              # Risk assessment
  python src/main.py --batch             # Batch processing
  python src/main.py --data data.json    # External data source
  python src/main.py --format csv        # CSV output
  python src/main.py --health            # Check service status
        """,
    )

    parser.add_argument("--classification", action="store_true", help="Intelligent classification")
    parser.add_argument("--sentiment", action="store_true", help="Sentiment analysis")
    parser.add_argument("--intention", action="store_true", help="Intent recognition")
    parser.add_argument("--recommend", action="store_true", help="Recommendation decision")
    parser.add_argument("--risk", action="store_true", help="Risk assessment")
    parser.add_argument("--batch", action="store_true", help="Batch processing")
    parser.add_argument("--health", action="store_true", help="Check service status")

    # General options
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="External data file path (.json/.csv/-)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available scenarios",
    )

    args = parser.parse_args()

    system = DecisionSystem(data_source=args.data, output_format=args.format)

    # Health check
    if args.health:
        health = check_health()
        status = health.get("status", "unknown")
        print(f"🔍 Laya service status: {status}")
        if status == "ok":
            print(f"   URL: {health.get('url', 'N/A')}")
            print(f"   Response: {health.get('message', health)}")
        else:
            print(f"   Error: {health.get('message', 'Unknown error')}")
        sys.exit(0 if status == "ok" else 1)

    # List scenarios
    if args.list:
        scenarios_list = list_scenarios()
        print("\n📋 Available scenarios:")
        for s in scenarios_list:
            print(f"  • {s['name']:25s} {s['title']} ({s['decision_type']})")
        print()
        sys.exit(0)

    # Scenario routing
    if args.classification:
        system.run_classification()
    elif args.sentiment:
        system.run_sentiment()
    elif args.intention:
        system.run_intention()
    elif args.recommend:
        system.run_recommend()
    elif args.risk:
        system.run_risk()
    elif args.batch:
        system.run_batch()
    else:
        # Interactive menu
        show_menu()
        print("\nCurrently supported decision types:")
        for dtype, info in DECISION_TYPES.items():
            print(f"  • {info['name']}: {info['description']}")

        while True:
            try:
                choice = input("\nSelect function [0-7]:").strip()

                action_map = {
                    "1": system.run_classification,
                    "2": system.run_sentiment,
                    "3": system.run_intention,
                    "4": system.run_recommend,
                    "5": system.run_risk,
                    "6": system.run_batch,
                    "7": system.run_data_management,
                }

                if choice in action_map:
                    action_map[choice]()
                elif choice == "0":
                    print("\n👋 Thanks for using! Goodbye!")
                    break
                else:
                    print("❌ Invalid selection, please try again")

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                break
            except Exception as e:
                logging.error("Error in interactive mode: %s", e, exc_info=True)
                print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()