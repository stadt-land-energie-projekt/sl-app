"""Module to calculate results."""

from __future__ import annotations

from functools import reduce
from operator import or_

from django.db.models import Prefetch, Q

from .models import Result, Sensitivity

TECHNOLOGIES = {
    "electrolyzer": {
        "name": "Wasserstoff-Elektrolyseur",
        "color": "#1E90FF",
    },
    "pv": {
        "name": "Photovoltaik",
        "color": "#FFD700",
    },
    "heatpump_small": {
        "name": "Kleine Wärmepumpe",
        "color": "#FF4500",
    },
    "heat_decentral_storage": {
        "name": "Dezentrale Wärmespeicherung",
        "color": "#8B0000",
    },
    "ror": {
        "name": "Laufwasserkraftwerk",
        "color": "#4682B4",
    },
}

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


def get_sensitivity_result(sensitivity: str, region: str, technology: str) -> dict[float, dict[str, float]]:
    """Return resulting capacities for given sensitivity."""
    capacity_query = reduce(
        or_,
        [Q(name=technology, var_name=capacity_name) for technology, capacity_name in CAPACITIES.items()],
    ) & Q(region=region)
    sensitivities = (
        Sensitivity.objects.filter(attribute=sensitivity, component=technology, region=region)
        .select_related("scenario")
        .prefetch_related(
            Prefetch("scenario__result_set", queryset=Result.objects.filter(capacity_query), to_attr="results"),
        )
        .all()
    )

    results = {
        sensitivity.perturbation_parameter: {result.name: result.var_value for result in sensitivity.scenario.results}
        for sensitivity in sensitivities
    }
    return results
