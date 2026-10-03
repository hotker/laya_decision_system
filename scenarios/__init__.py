"""
Scenarios Package
=================
Scenario auto-registration package

Importing this module will auto-discover and register all scenario modules
using the plugin system.

Additional aliases are registered for scenarios with compound function names
(e.g., run_product_recommendation → "recommend") so that CLI flags
(--recommend) map correctly.
"""

from __future__ import annotations

from utils.plugin import (
    get_scenario,
    register,
    register_scenarios,
    reset,
)

# Reset and auto-discover
reset()
register_scenarios()

# Register aliases for scenarios that have compound names
# These ensure CLI flags like --recommend map to the right scenario
_aliases = {
    "product_recommendation": "recommend",
    "risk_assessment": "risk",
    "intention_recognition": "intention",
    "marketing_decision": "marketing",
}
for _old_name, _new_name in _aliases.items():
    scenario = get_scenario(_old_name)
    if scenario and not get_scenario(_new_name):
        register(
            _new_name,
            scenario["title"],
            scenario["decision_type"],
            scenario["run_func"],
        )