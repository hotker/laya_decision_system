"""
场景插件系统测试
================
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestPluginRegister:
    """测试场景注册"""

    def _fresh_plugin(self):
        """获取干净的 plugin 模块（无预注册）"""
        # 清除已注册的场景
        import utils.plugin

        utils.plugin._SCENARIOS.clear()
        return utils.plugin

    def test_register_scenario(self):
        """注册场景"""
        import utils.plugin

        utils.plugin._SCENARIOS.clear()

        def dummy_fn():
            pass

        utils.plugin.register("test", "测试场景", "test_type", dummy_fn)

        assert "test" in utils.plugin._SCENARIOS
        assert utils.plugin._SCENARIOS["test"]["title"] == "测试场景"
        assert utils.plugin._SCENARIOS["test"]["decision_type"] == "test_type"

    def test_get_scenario(self):
        """获取场景"""
        import utils.plugin

        utils.plugin._SCENARIOS.clear()

        def dummy_fn():
            return "result"

        utils.plugin.register("test", "测试", "test_type", dummy_fn)

        plugin = utils.plugin.get_scenario("test")
        assert plugin.name == "test"
        assert plugin.title == "测试"
        assert plugin.run() == "result"

    def test_get_unknown_scenario(self):
        """获取不存在场景"""
        import utils.plugin

        utils.plugin._SCENARIOS.clear()

        with pytest.raises(KeyError, match="Unknown scenario"):
            utils.plugin.get_scenario("nonexistent")

    def test_list_scenarios(self):
        """列出场景"""
        import utils.plugin

        utils.plugin._SCENARIOS.clear()

        utils.plugin.register("a", "场景A", "type1", lambda: None)
        utils.plugin.register("b", "场景B", "type2", lambda: None)

        listed = utils.plugin.list_scenarios()
        assert len(listed) == 2
        names = {s["name"] for s in listed}
        assert names == {"a", "b"}

    def test_scenario_repr(self):
        """场景 repr"""
        import utils.plugin

        utils.plugin._SCENARIOS.clear()

        def fn():
            pass

        utils.plugin.register("test", "测试", "type", fn)
        plugin = utils.plugin.get_scenario("test")
        assert "test" in repr(plugin)
        assert "测试" in repr(plugin)


class TestScenarioPlugin:
    """测试 ScenarioPlugin 类"""

    def test_run_with_kwargs(self):
        """带参数运行"""

        def fn(a, b=10):
            return a + b

        import utils.plugin

        utils.plugin._SCENARIOS.clear()
        utils.plugin.register("kw", "kw", "kw", fn)
        plugin = utils.plugin.get_scenario("kw")
        assert plugin.run(a=5, b=3) == 8


class TestAutoRegister:
    """测试 scenarios/__init__.py 的自动注册"""

    def test_all_scenarios_registered(self):
        """所有场景都应被注册"""
        # 先清除
        import utils.plugin

        utils.plugin._SCENARIOS.clear()

        # 清除 scenarios 模块缓存
        to_remove = [k for k in sys.modules if k.startswith("scenarios")]
        for k in to_remove:
            del sys.modules[k]

        # 重新导入触发注册
        import scenarios

        # 验证 6 个场景都已注册
        names = utils.plugin.get_all_scenario_names()
        expected = {
            "classification",
            "sentiment",
            "intention",
            "product_recommendation",
            "marketing_decision",
            "risk_assessment",
        }
        assert set(names) == expected, f"Missing: {expected - set(names)}"

    def test_risk_scenario_exists(self):
        """风险评估场景存在"""
        import utils.plugin

        utils.plugin._SCENARIOS.clear()
        to_remove = [k for k in sys.modules if k.startswith("scenarios")]
        for k in to_remove:
            del sys.modules[k]

        import scenarios

        assert "risk_assessment" in utils.plugin._SCENARIOS
        plugin = utils.plugin.get_scenario("risk_assessment")
        assert plugin.decision_type == "risk"