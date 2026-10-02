"""
智能分类场景（增强版）
====================
支持外部数据源输入，结构化日志输出

使用方式：
    python main.py --classification                 # 默认数据
    python main.py --classification --data reviews.json  # 外部数据
    python main.py --classification --data reviews.csv     # CSV 数据
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from utils.data_source import load_data
from utils.http_client import make_predict_request
from utils.output import save_results
from utils.progress import ProgressBar
from utils.validation import validate_state, validate_questions

logger = logging.getLogger(__name__)


def run_classification_example(data_source: Optional[str] = None) -> None:
    """运行智能分类决策

    Args:
        data_source: 数据文件路径（.json / .csv / "-"），None 使用默认数据
    """
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI 决策系统 — 智能分类决策                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    questions = {
        "category": {
            "type": "choice",
            "instructions": "判断评论类别",
            "criteria": {
                "quality": "质量、做工、耐用、材质、工艺",
                "price": "价格、贵、便宜、性价比、值",
                "service": "客服、物流、安装、售后、发货",
                "function": "功能、智能、操作、效果、体验",
                "design": "外观、颜值、设计、款式、颜色",
            },
        }
    }

    # 校验
    errors = validate_questions(questions)
    if errors:
        print(f"❌ 问题定义校验失败: {'; '.join(errors)}")
        return

    # 加载数据
    if data_source:
        items = load_data(data_source, text_column="body")
        if items is None:
            print("⚠️  数据文件为空，使用默认数据")
            items = _default_reviews()
    else:
        items = _default_reviews()

    reviews = [{"body": item["body"]} if isinstance(item, dict) else {"body": item} for item in items]

    print(f"\n📝 开始分类决策（{len(reviews)} 条）...")
    print("-" * 70)

    results = []
    with ProgressBar(total=len(reviews), desc="分类") as p:
        for i, review in enumerate(reviews):
            body = review["body"]

            # 校验输入
            state_errors = validate_state(body)
            if state_errors:
                logger.warning("review %d validation failed: %s", i + 1, state_errors)
                category = f"skipped({state_errors[0][:20]})"
            else:
                result = make_predict_request(body, questions)
                category = result.get("answers", {}).get("category", {}).get("choice", "unknown")
                if result.get("error"):
                    logger.warning("review %d HTTP error: %s", i + 1, result["error"])
                    category = f"error({result['error'][:20]})"

            print(f"  {i+1:3d}. {body[:40]:<40} → {category:<10}")
            results.append({"review": body, "category": category})
            p.update(1)

    # 统计
    _print_stats(results, "category", "📊 分类结果统计")

    filename = save_results(results, prefix="classification", decision_type="classification")
    print(f"\n💾 已保存：{filename}")


def _default_reviews() -> list[str]:
    return [
        "这个产品质量很好，做工精细，材质上乘",
        "价格太贵了，性价比不高，不值得购买",
        "客服态度很好，物流也很快，安装师傅专业",
        "智能功能很实用，操作简便，体验不错",
        "外观设计简约大方，颜色很喜欢，放在家里很搭",
        "商品收到有破损，客服处理及时，给了补偿",
        "用了三个月了，没什么问题，质量可靠",
        "物流太慢了，等了半个月才到",
        "产品功能强大，智能联动很方便",
        "颜值很高，做工也不错，值得推荐",
    ]


def _print_stats(results: list[dict], key: str, title: str) -> None:
    """打印分类统计"""
    print(f"\n{title}")
    print("=" * 70)
    stats: dict[str, int] = {}
    for r in results:
        cat = r.get(key, "unknown")
        stats[cat] = stats.get(cat, 0) + 1
    for cat, count in stats.items():
        pct = count / len(results) * 100
        bar = "█" * int(pct / 5)
        print(f"  {cat:<12}: {count:3d} ({pct:5.1f}%) {bar}")