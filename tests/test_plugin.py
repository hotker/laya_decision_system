"""Tests for plugin system
========================
"""

from __future__ import annotations

from utils.plugin import get_all_scenario_names, get_scenario, list_scenarios, register, reset


def dummy_run_func():
    """Dummy run function for testing"""
    pass


class TestPluginSystem:
    """Test plugin system"""

    def test_register_scenario(self):
        """Test registering a scenario"""
        reset()

        register("test_scenario", "Test Scenario", "test", dummy_run_func)

        scenarios = list_scenarios()
        assert len(scenarios) == 1
        assert scenarios[0]["name"] == "test_scenario"
        assert scenarios[0]["title"] == "Test Scenario"

    def test_get_all_scenario_names(self):
        """Test getting all scenario names"""
        reset()
        register("test_scenario", "Test Scenario", "test", dummy_run_func)

        names = get_all_scenario_names()
        assert isinstance(names, list)
        assert "test_scenario" in names

    def test_get_scenario_by_name(self):
        """Test getting scenario by name"""
        reset()
        register("test_scenario", "Test Scenario", "test", dummy_run_func)

        scenario = get_scenario("test_scenario")
        assert scenario is not None
        assert scenario["name"] == "test_scenario"

    def test_get_nonexistent_scenario(self):
        """Test getting non-existent scenario"""
        reset()
        scenario = get_scenario("nonexistent")
        assert scenario is None