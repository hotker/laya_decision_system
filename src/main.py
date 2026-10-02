"""
🧠 Laya AI 决策系统 v2.0 — 主入口
================================

增强版 CLI，支持：
  - 插件化场景注册
  - 外部数据源 (--data)
  - 进度条显示
  - 结构化日志
  - 输出格式选择 (--format csv)

使用方式：
  python src/main.py                  # 交互式菜单
  python src/main.py --classification # 智能分类
  python src/main.py --batch          # 批量处理
  python src/main.py --data data.json # 外部数据
  python src/main.py --format csv     # CSV 输出
  python src/main.py --health         # 健康检查
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# 确保项目根在路径中
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.config import DECISION_TYPES, SYSTEM_NAME, VERSION, get_config
from utils.data_source import load_data, save_output
from utils.http_client import check_health
from utils.output import clean_all, clean_old_files, list_output_files
from utils.plugin import get_all_scenario_names, list_scenarios, register_scenarios
from utils.progress import ProgressBar

# 导入所有场景模块以触发注册
import scenarios  # noqa: F401


def show_menu() -> None:
    """显示主菜单"""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI 决策系统 v2.0                              ║
║                                                              ║
║  功能模块：                                                  ║
║                                                              ║
║  1️⃣  智能分类 — 文本/评论自动分类                            ║
║  2️⃣  情感分析 — 情感倾向自动识别                            ║
║  3️⃣  意图识别 — 用户意图自动识别                            ║
║  4️⃣  推荐决策 — 个性化推荐与营销策略                        ║
║  5️⃣  风险评估 — 风险等级自动评分                            ║
║  6️⃣  批量处理 — 批量决策分析                                ║
║  7️⃣  数据管理 — 查看/清理决策数据                           ║
║  0️⃣  退出系统                                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )


def setup_logging() -> None:
    """初始化日志"""
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
    """决策系统主控制器"""

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
        """批量处理：使用默认数据或外部数据源"""
        from utils.http_client import make_batch_request
        from utils.output import save_results

        print(
            """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI 决策系统 — 批量处理                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        )

        # 加载数据
        if self.data_source:
            items = load_data(self.data_source, text_column="body")
            if items is None:
                print("⚠️  数据文件为空，使用默认数据")
                items = _default_batch_items()
        else:
            items = _default_batch_items()

        states = [{"body": item["body"]} if isinstance(item, dict) else {"body": item} for item in items]

        questions = {
            "sentiment": {
                "type": "choice",
                "instructions": "分析情感倾向",
                "criteria": {
                    "positive": "好评、推荐、质量好、性价比高",
                    "negative": "差评、问题、不好、贵、差",
                    "neutral": "一般、普通、还行",
                },
            }
        }

        print(f"\n📝 开始批量处理（{len(states)} 条）...")
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
                    f"  {i+1}. {body[:40]:<40} {sentiment:<8} (置信度：{confidence:.2f})"
                )

            # 收集结果
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
            print(f"\n💾 已保存：{filename}")
            print(f"⏱  耗时：{elapsed:.2f}s ({len(result['results'])} 条, {elapsed/len(result['results'])*1000:.0f}ms/条)")
        else:
            error_msg = result.get("error", "未知错误")
            print(f"❌ 批量处理失败：{error_msg}")

    def run_data_management(self) -> None:
        print("\n📁 数据管理")
        print("-" * 60)

        files = list_output_files()
        if files:
            print("\n📄 决策文件列表：")
            for f in files:
                size = f.stat().st_size / 1024
                print(f"  • {f.name} ({size:.1f} KB)")
        else:
            print("❌ 没有决策文件")

        print("\n管理操作：")
        print("  1. 删除旧文件（保留最近 10 个）")
        print("  2. 清空所有数据")

        choice = input("\n请选择操作 [1-2] 或直接回车退出：").strip()

        if choice == "1":
            deleted = clean_old_files(keep_count=10)
            if deleted > 0:
                print(f"  已删除 {deleted} 个旧文件")
            else:
                print("  无需清理")
        elif choice == "2":
            confirm = input("⚠️  确认清空所有数据？(y/n): ").strip().lower()
            if confirm == "y":
                deleted = clean_all()
                print(f"  ✅ 已清空 {deleted} 个文件")


def _default_batch_items() -> list[str]:
    return [
        "产品很好，物流很快，客服态度也不错",
        "质量太差了，用了两天就坏了，退货",
        "价格实惠，性价比高，值得购买",
        "包装很好，没有破损，五星好评",
        "物流太慢了，等了半个月才到，体验很差",
    ]


# ─── 主函数 ────────────────────────────────────────────────────


def main() -> None:
    """主入口"""
    setup_logging()

    parser = argparse.ArgumentParser(
        description=f"{SYSTEM_NAME} v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python src/main.py                     # 交互式菜单
  python src/main.py --classification    # 智能分类
  python src/main.py --sentiment         # 情感分析
  python src/main.py --intention         # 意图识别
  python src/main.py --recommend         # 推荐决策
  python src/main.py --risk              # 风险评估
  python src/main.py --batch             # 批量处理
  python src/main.py --data data.json    # 外部数据源
  python src/main.py --format csv        # CSV 输出
  python src/main.py --health            # 检查服务状态
        """,
    )

    parser.add_argument("--classification", action="store_true", help="智能分类")
    parser.add_argument("--sentiment", action="store_true", help="情感分析")
    parser.add_argument("--intention", action="store_true", help="意图识别")
    parser.add_argument("--recommend", action="store_true", help="推荐决策")
    parser.add_argument("--risk", action="store_true", help="风险评估")
    parser.add_argument("--batch", action="store_true", help="批量处理")
    parser.add_argument("--health", action="store_true", help="检查服务状态")

    # 通用选项
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="外部数据文件路径 (.json/.csv/-)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="输出格式 (default: json)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有可用场景",
    )

    args = parser.parse_args()

    system = DecisionSystem(data_source=args.data, output_format=args.format)

    # 健康检查
    if args.health:
        health = check_health()
        status = health.get("status", "unknown")
        print(f"🔍 Laya 服务状态：{status}")
        if status == "ok":
            print(f"   URL: {health.get('url', 'N/A')}")
            print(f"   响应: {health.get('message', health)}")
        else:
            print(f"   错误: {health.get('message', '未知错误')}")
        sys.exit(0 if status == "ok" else 1)

    # 列出场景
    if args.list:
        scenarios_list = list_scenarios()
        print("\n📋 可用场景：")
        for s in scenarios_list:
            print(f"  • {s['name']:25s} {s['title']} ({s['decision_type']})")
        print()
        sys.exit(0)

    # 场景路由
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
        # 交互式菜单
        show_menu()
        print(f"\n当前支持的决策类型：")
        for dtype, info in DECISION_TYPES.items():
            print(f"  • {info['name']}：{info['description']}")

        while True:
            try:
                choice = input("\n请选择功能 [0-7]：").strip()

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
                    print("\n👋 感谢使用！再见！")
                    break
                else:
                    print("❌ 无效选择，请重新输入")

            except KeyboardInterrupt:
                print("\n\n⚠️  用户中断")
                break
            except Exception as e:
                logging.error("Error in interactive mode: %s", e, exc_info=True)
                print(f"❌ 错误：{e}")


if __name__ == "__main__":
    main()