"""
情感分析场景（增强版）
====================
支持外部数据源输入，结构化日志输出

使用方式：
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
from utils.validation import validate_state, validate_questions

logger = logging.getLogger(__name__)


def run_sentiment_analysis(data_source: Optional[str] = None) -> None:
    """运行情感分析决策

    Args:
        data_source: 数据文件路径，None 使用默认数据
    """
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI 决策系统 — 情感分析决策                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    questions = {
        "sentiment": {
            "type": "choice",
            "instructions": "判断情感倾向",
            "criteria": {
                "very_positive": "非常满意、强烈推荐、超出预期、太棒了",
                "positive": "满意、推荐、不错、好、喜欢",
                "neutral": "一般、普通、还好、正常",
                "negative": "不满意、不推荐、差、失望",
                "very_negative": "非常不满意、强烈不推荐、太糟糕了、避雷",
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
            items = _default_comments()
    else:
        items = _default_comments()

    comments = [{"body": item["body"]} if isinstance(item, dict) else {"body": item} for item in items]

    print(f"\n📝 开始情感分析（{len(comments)} 条）...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(comments), desc="情感") as p:
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
    print(f"\n💾 已保存：{filename}")


def _default_comments() -> list[str]:
    return [
        "这个产品太棒了！质量超好，强烈推荐！",
        "挺好的，用了半个月没出问题",
        "一般般吧，没什么特别的感觉",
        "质量太差了，用了两天就坏了",
        "非常不满意，退货了，大家别买！",
        "价格实惠，性价比很高，值得购买",
        "包装很好，物流也快，五星好评",
        "客服态度好，处理问题及时",
        "产品功能强大，超出预期",
        "物流慢，客服回复不及时，体验差",
    ]


def _print_stats(results: list[dict]) -> None:
    print("\n📊 情感分布：")
    stats: dict[str, int] = {}
    for r in results:
        s = r.get("sentiment", "unknown")
        stats[s] = stats.get(s, 0) + 1
    for sentiment, count in stats.items():
        bar = "█" * count
        print(f"  {sentiment:<15}: {count} {bar}")