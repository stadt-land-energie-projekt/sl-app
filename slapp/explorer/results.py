"""Module to calculate results."""

from __future__ import annotations

from .models import Sensitivity

CAPACITIES = {
    "B-wind-onshore": "invest_out_electricity",
    "BB-wind-onshore": "invest_out_electricity",
    "BB-solar-pv": "invest_out_electricity",
    "B-solar-pv": "invest_out_electricity",
    "B-electricity-electrolyzer": "invest_out_h2",
    "BB-electricity-electrolyzer": "invest_out_h2",
    "B-electricity-heatpump_small": "invest_out_heat_decentral",
    "BB-electricity-heatpump_small": "invest_out_heat_decentral",
    "B-electricity-liion_battery": "invest",
    "BB-electricity-liion_battery": "invest",
    "B-electricity-pth": "invest_out_heat_central",
    "BB-electricity-pth": "invest_out_heat_central",
    "B-h2-bpchp": "invest_out_electricity",
    "BB-h2-bpchp": "invest_out_electricity",
    "B-h2-cavern": "invest",
    "BB-h2-cavern": "invest",
    "B-h2-gt": "invest_out_electricity",
    "BB-h2-gt": "invest_out_electricity",
    "B-heat_central-storage": "invest",
    "BB-heat_central-storage": "invest",
    "B-heat_decentral-storage": "invest",
    "BB-heat_decentral-storage": "invest",
    "B-hydro-ror": "invest_out_electricity",
    "BB-hydro-ror": "invest_out_electricity",
    "B-ch4-boiler_large": "invest_out_heat_central",
    "BB-ch4-boiler_large": "invest_out_heat_central",
    "B-ch4-boiler_small": "invest_out_heat_decentral",
    "BB-ch4-boiler_small": "invest_out_heat_decentral",
    "B-ch4-bpchp": "invest_out_electricity",
    "BB-ch4-bpchp": "invest_out_electricity",
    "B-ch4-gt": "invest_out_electricity",
    "BB-ch4-gt": "invest_out_electricity",
}


def get_sensitivity_result(sensitivity: str, technology: str) -> dict[float, dict[str, float]]:
    """Return resulting capacities for given sensitivity."""
    sensitivities = Sensitivity.objects.filter(attribute=sensitivity, component=technology)
    results = {
        sensitivity.perturbation_parameter: sensitivity.scenario.result_set.filter(name__in=CAPACITIES)
        for sensitivity in sensitivities
    }
    return {
        sensitivity: {
            technology: queryset.filter(name=technology, var_name=capacity).values("var_value").first()["var_value"]
            for technology, capacity in CAPACITIES.items()
        }
        for sensitivity, queryset in results.items()
    }
