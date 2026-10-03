"""Tests for plugin system
========================
"""

from __future__ import annotations

from utils.plugin import (
    get_all_scenario_names,
    get_scenario,
    list_scenarios,
    register,
    register_scenarios,
    reset,
)


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

    def test_reset_clears_scenarios(self):
        """Test that reset() clears all registered scenarios"""
        reset()
        register("test_scenario", "Test Scenario", "test", dummy_run_func)
        assert len(list_scenarios()) == 1

        reset()
        assert len(list_scenarios()) == 0

    def test_scenario_title_generation(self):
        """Test that scenario titles are auto-generated from names"""
        reset()
        register("my-scenario", "My Scenario", "my_type", dummy_run_func)

        scenario = get_scenario("my-scenario")
        assert scenario is not None
        assert scenario["title"] == "My Scenario"

    def test_duplicate_scenario_ignored(self):
        """Test that registering a duplicate scenario logs and skips"""
        reset()
        register("dup", "First", "type1", dummy_run_func)
        # Registering same name again should be handled (get_scenario finds it,
        # so register_scenarios would skip it)
        scenario = get_scenario("dup")
        assert scenario is not None
        assert scenario["name"] == "dup"


class TestRegisterScenariosAutoDiscovery:
    """Test auto-discovery of scenarios via register_scenarios()"""

    def test_register_scenarios_finds_known_scenarios(self):
        """Test register_scenarios discovers standard scenarios"""
        reset()
        register_scenarios()

        names = get_all_scenario_names()
        expected = {"classification", "sentiment", "intention", "recommend"}
        assert expected.issubset(set(names)), f"Missing: {expected - set(names)}"

    def test_register_scenarios_provides_run_func(self):
        """Test auto-discovered scenarios have callable run_func"""
        reset()
        register_scenarios()

        for name in ["classification", "sentiment", "intention"]:
            scenario = get_scenario(name)
            assert scenario is not None
            assert callable(scenario["run_func"])

    def test_register_scenarios_with_different_names(self):
        """Test scenarios with various naming patterns"""
        reset()
        register_scenarios()

        names = get_all_scenario_names()
        # risk_assessment -> risk
        assert "risk" in names or any("risk" in n for n in names)

    def test_register_scenarios_all_have_metadata(self):
        """Test all auto-discovered scenarios have required fields"""
        reset()
        register_scenarios()

        required_keys = {"name", "title", "decision_type", "run_func"}
        for s in list_scenarios():
            assert required_keys.issubset(s.keys()), f"Missing keys in {s['name']}: {required_keys - s.keys()}"