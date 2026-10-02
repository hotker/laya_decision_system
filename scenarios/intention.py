"""
意图识别场景（增强版）
====================
支持外部数据源输入

使用方式：
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
    """运行意图识别决策"""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI 决策系统 — 意图识别决策                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    questions = {
        "intent": {
            "type": "choice",
            "instructions": "判断客户意图",
            "criteria": {
                "inquiry": "咨询、询问、了解、怎么、什么、如何",
                "complaint": "投诉、问题、故障、坏、差、不满",
                "purchase": "购买、下单、要、买、下单",
                "after_sale": "售后、退换、维修、客服、退款",
                "praise": "好评、推荐、感谢、谢谢、满意",
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
            items = _default_messages()
    else:
        items = _default_messages()

    messages = [{"body": item["body"]} if isinstance(item, dict) else {"body": item} for item in items]

    print(f"\n📝 开始意图识别（{len(messages)} 条）...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(messages), desc="意图") as p:
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
    print(f"\n💾 已保存：{filename}")


def _default_messages() -> list[str]:
    return [
        "你们这个产品怎么使用？有说明书吗？",
        "产品坏了，怎么办？要维修吗？",
        "我要下单，什么时候能发货？",
        "我想退货，可以吗？",
        "产品质量很好，谢谢客服",
        "物流太慢了，等了三天还没到",
        "这个功能在哪里打开？",
        "我要退款，质量太差了",
        "推荐给你们的朋友，很好用",
        "客服态度太差了，我要投诉",
    ]


def _print_stats(results: list[dict]) -> None:
    print("\n📊 意图分布：")
    stats: dict[str, int] = {}
    for r in results:
        s = r.get("intent", "unknown")
        stats[s] = stats.get(s, 0) + 1
    for intent, count in stats.items():
        bar = "█" * count
        print(f"  {intent:<15}: {count} {bar}")