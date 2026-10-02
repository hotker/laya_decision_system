"""
推荐决策场景（增强版）
====================
产品推荐 + 营销策略，支持外部数据源

使用方式：
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
from utils.validation import validate_state, validate_questions

logger = logging.getLogger(__name__)


def run_product_recommendation(data_source: Optional[str] = None) -> None:
    """运行产品推荐决策"""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI 决策系统 — 产品推荐决策                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    questions = {
        "strategy": {
            "type": "choice",
            "instructions": "选择推荐策略",
            "criteria": {
                "quality_premium": "高端品质、品牌优先、价格不敏感",
                "best_value": "性价比、价格优先、实惠选择",
                "trend_popular": "热门趋势、流行款式、社交驱动",
                "personalized": "个性化定制、精准匹配、用户画像",
                "comprehensive": "综合推荐、平衡品质价格、全维度考虑",
            },
        }
    }

    errors = validate_questions(questions)
    if errors:
        print(f"❌ 问题定义校验失败: {'; '.join(errors)}")
        return

    if data_source:
        items = load_data(data_source, text_column="body")
        if items is None:
            print("⚠️  数据文件为空，使用默认数据")
            items = _default_profiles()
    else:
        items = _default_profiles()

    profiles = [{"body": item["body"]} if isinstance(item, dict) else {"body": item} for item in items]

    print(f"\n📝 开始产品推荐决策（{len(profiles)} 条）...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(profiles), desc="推荐") as p:
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

            print(f"  {i+1:3d}. {body[:40]:<40} → {strategy:<18}")
            results.append({"profile": body, "strategy": strategy})
            p.update(1)

    _print_stats(results)

    filename = save_results(results, prefix="recommendation", decision_type="recommendation")
    print(f"\n💾 已保存：{filename}")


def run_marketing_decision(data_source: Optional[str] = None) -> None:
    """运行营销策略决策"""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI 决策系统 — 营销策略决策                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    questions = {
        "marketing_strategy": {
            "type": "choice",
            "instructions": "制定营销策略",
            "criteria": {
                "discount": "折扣促销、降价优惠、限时抢购",
                "content": "内容营销、种草推荐、KOL 合作",
                "social": "社交裂变、拼团砍价、分享返利",
                "loyalty": "会员体系、积分兑换、专属特权",
                "personalized": "个性化推送、精准营销、千人千面",
            },
        }
    }

    errors = validate_questions(questions)
    if errors:
        print(f"❌ 问题定义校验失败: {'; '.join(errors)}")
        return

    if data_source:
        items = load_data(data_source, text_column="body")
        if items is None:
            print("⚠️  数据文件为空，使用默认数据")
            items = _default_scenarios()
    else:
        items = _default_scenarios()

    scenarios = [{"body": item["body"]} if isinstance(item, dict) else {"body": item} for item in items]

    print(f"\n📝 开始营销策略决策（{len(scenarios)} 条）...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(scenarios), desc="营销") as p:
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

            print(f"  {i+1:3d}. {body[:40]:<40} → {strategy:<18}")
            results.append({"scenario": body, "marketing_strategy": strategy})
            p.update(1)

    _print_stats(results)

    filename = save_results(results, prefix="marketing", decision_type="marketing")
    print(f"\n💾 已保存：{filename}")


def _default_profiles() -> list[str]:
    return [
        "白领女性，预算 5000 元，注重品质和品牌",
        "学生党，预算 500 元，追求性价比",
        "科技爱好者，关注最新科技产品",
        "家庭用户，需要全家用的产品",
        "时尚达人，追求设计感和潮流",
    ]


def _default_scenarios() -> list[str]:
    return [
        "新品上市，预算充足，需要快速打开市场",
        "季末清仓，库存压力大，需要快速回笼资金",
        "双 11 大促，竞争激烈，需要差异化策略",
        "会员日，针对老客户的专属活动",
        "社交媒体营销，需要提升品牌曝光度",
    ]


def _print_stats(results: list[dict]) -> None:
    print("\n📊 策略分布：")
    stats: dict[str, int] = {}
    key = "strategy" if "strategy" in results[0] else "marketing_strategy"
    for r in results:
        s = r.get(key, "unknown")
        stats[s] = stats.get(s, 0) + 1
    for strategy, count in stats.items():
        bar = "█" * count
        print(f"  {strategy:<15}: {count} {bar}")