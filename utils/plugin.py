"""
Scenario Plugin System
=======================
Automatic scenario registration and discovery

Usage:
    from utils.plugin import register, list_scenarios, get_all_scenario_names
    register("my_scenario", "My Scenario", "decision_type", run_func)
"""

from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Global scenario registry
_scenarios: list[dict[str, Any]] = []


def register(
    name: str,
    title: str,
    decision_type: str,
    run_func: Callable,
) -> None:
    """Register a scenario

    Args:
        name: Scenario identifier
        title: Human-readable title
        decision_type: Decision type category
        run_func: Function to execute
    """
    _scenarios.append({
        "name": name,
        "title": title,
        "decision_type": decision_type,
        "run_func": run_func,
    })
    logger.info("scenario_registered name=%s title=%s", name, title)


def register_scenarios() -> None:
    """Register all scenarios by importing scenarios module"""
    # This is called automatically when importing scenarios
    pass


def list_scenarios() -> list[dict[str, Any]]:
    """List all registered scenarios

    Returns:
        List of scenario dicts
    """
    return list(_scenarios)


def get_all_scenario_names() -> list[str]:
    """Get all registered scenario names

    Returns:
        List of scenario names
    """
    return [s["name"] for s in _scenarios]


def get_scenario(name: str) -> dict[str, Any] | None:
    """Get scenario by name

    Args:
        name: Scenario identifier

    Returns:
        Scenario dict or None
    """
    for s in _scenarios:
        if s["name"] == name:
            return s
    return None