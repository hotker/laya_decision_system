"""
风险评估场景
============
自动评估业务、信贷、安全等场景的风险等级

使用方式：
    python main.py --risk
"""

from __future__ import annotations

import logging

from utils.http_client import make_predict_request
from utils.output import save_results

logger = logging.getLogger(__name__)


def run_risk_assessment() -> None:
    """运行风险评估示例"""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 Laya AI 决策系统 — 风险评估决策                     ║
║                                                              ║
║        场景：业务/信贷/安全风险评估                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    questions = {
        "risk_level": {
            "type": "choice",
            "instructions": "评估风险等级",
            "criteria": {
                "high": "欺诈迹象、严重违约、资金链断裂、非法行为",
                "medium": "信用一般、有逾期记录、经营不稳定",
                "low": "信用良好、有稳定收入、历史合规",
                "safe": "零风险记录、优质客户、强担保",
            },
        }
    }

    cases = [
        "新客户申请 50 万贷款，无信用记录，多平台查询征信",
        "企业连续 3 个月拖欠货款，法人变更频繁",
        "老客户申请信用卡提额，历史还款记录良好",
        "用户账户异常登录，异地 IP，频繁修改密码",
        "新商户入驻平台，营业执照齐全，有实体门店",
        "信贷申请人负债率 85%，近半年 6 次逾期",
    ]

    print("\n📝 开始风险评估...")
    print("-" * 70)
    print(f"{'#':<4} {'业务场景':<40} {'风险等级':<8}")
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

    # 统计
    print("\n" + "=" * 70)
    print("📊 风险分布：")
    print("=" * 70)
    stats = {}
    for r in results:
        level = r["risk_level"]
        stats[level] = stats.get(level, 0) + 1
    for level, count in stats.items():
        bar = "█" * count
        print(f"  {level:<12}: {count} {bar}")

    filename = save_results(results, prefix="risk", decision_type="risk")
    print(f"\n💾 已保存：{filename}")