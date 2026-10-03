"""
Scenario Plugin System
=======================
Automatic scenario registration and discovery

Usage:
    from utils.plugin import register, list_scenarios, get_all_scenario_names, get_scenario
    register("my_scenario", "My Scenario", "decision_type", run_func)
"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
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
    """Auto-discover and register all scenarios from the scenarios package.

    Discovers modules in the scenarios package, imports them, and registers
    any function whose name starts with 'run_' as a scenario.

    Scenario name mapping:
        run_xxx_example  -> xxx
        run_xxx_analysis -> xxx
        run_xxx          -> xxx
    """
    scenarios_pkg = importlib.import_module("scenarios")
    scenarios_dir = inspect.getfile(scenarios_pkg)

    if not scenarios_dir.endswith("__init__.py"):
        scenarios_dir = scenarios_dir.replace("__init__.py", "")
    else:
        scenarios_dir = scenarios_dir.rsplit("/", 1)[0] + "/"

    for _finder, mod_name, is_pkg in pkgutil.iter_modules(
        [scenarios_dir], prefix="scenarios."
    ):
        if is_pkg or mod_name in ("scenarios", "scenarios.__init__"):
            continue

        try:
            module = importlib.import_module(mod_name)
        except Exception as exc:
            logger.error(
                "scenario_discovery_import_failed module=%s error=%s", mod_name, exc
            )
            continue

        for attr_name in dir(module):
            if not attr_name.startswith("run_"):
                continue

            attr = getattr(module, attr_name)
            if not callable(attr):
                continue

            # Derive scenario name from function name
            # run_xxx_example  -> xxx
            # run_xxx_analysis -> xxx
            # run_xxx_decision -> xxx
            # run_xxx_assessment -> xxx
            # run_xxx_recognition -> xxx
            suffixes = ["_example", "_analysis", "_decision", "_assessment", "_recognition"]
            short = attr_name[len("run_"):]
            for suffix in suffixes:
                if short.endswith(suffix):
                    short = short[: -len(suffix)]
                    break

            # Skip internal functions like _default_xxx
            scenario_name = short.replace("_", "-")

            # Only register if not already registered
            existing = get_scenario(short)
            if existing:
                logger.info(
                    "scenario_ignored duplicate name=%s func=%s",
                    short,
                    attr_name,
                )
                continue

            register(short, short.title().replace("-", " "), short, attr)
            logger.info(
                "scenario_auto_registered name=%s func=%s", short, attr_name
            )


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


def reset() -> None:
    """Clear all registered scenarios (mainly for testing)."""
    _scenarios.clear()