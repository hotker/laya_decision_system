"""
场景插件系统
============
自动发现和注册决策场景

使用方式：
    from plugin import register, get_scenario, list_scenarios

    register("classification", "智能分类", "classification", fn)
    scenario = get_scenario("classification")
    scenario.run()
"""

from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

# 场景注册表: name -> {plugin: ScenarioPlugin, title: str, decision_type: str}
_SCENARIOS: dict[str, dict[str, Any]] = {}


class ScenarioPlugin:
    """场景插件封装"""

    def __init__(
        self,
        name: str,
        title: str,
        decision_type: str,
        fn: Callable,
    ):
        self.name = name
        self.title = title
        self.decision_type = decision_type
        self._fn = fn

    def run(self, **kwargs: Any) -> Any:
        """运行场景"""
        return self._fn(**kwargs)

    def __repr__(self) -> str:
        return f"<Scenario {self.name}: {self.title}>"


def register(name: str, title: str, decision_type: str, fn: Callable) -> None:
    """注册一个场景插件"""
    _SCENARIOS[name] = {
        "fn": fn,
        "title": title,
        "decision_type": decision_type,
        "plugin": ScenarioPlugin(name, title, decision_type, fn),
    }
    logger.debug("scenario_registered name=%s title=%s", name, title)


def register_scenarios() -> None:
    """从 scenarios 包导入所有子模块（触发注册装饰器）"""
    import scenarios  # noqa: F401


def get_scenario(name: str) -> ScenarioPlugin:
    """获取已注册的场景插件"""
    if name not in _SCENARIOS:
        raise KeyError(
            f"Unknown scenario: {name!r}. Available: {list(_SCENARIOS.keys())}"
        )
    return _SCENARIOS[name]["plugin"]


def list_scenarios() -> list[dict[str, str]]:
    """列出所有已注册的场景"""
    return [
        {
            "name": k,
            "title": v["title"],
            "decision_type": v["decision_type"],
        }
        for k, v in _SCENARIOS.items()
    ]


def get_all_scenario_names() -> list[str]:
    """返回所有场景名称列表"""
    return list(_SCENARIOS.keys())


# 导出 _SCENARIOS 供 scenarios/__init__.py 使用
__all__ = [
    "register",
    "register_scenarios",
    "get_scenario",
    "list_scenarios",
    "get_all_scenario_names",
]