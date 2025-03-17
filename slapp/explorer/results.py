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
    "boiler_large": {
        "name": "Großer Erdgas-Kessel",
        "color": "#FF8C00",
    },
    "boiler_small": {
        "name": "Kleiner Erdgas-Kessel",
        "color": "#B22222",
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
    )
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


def add_baseline_results(sensitivity_data: dict) -> dict:
    """Add a baseline scenario (with cost 0) to sensitivity_data."""
    baseline_cost = 0.0
    if baseline_cost not in sensitivity_data:
        sorted_costs = sorted(sensitivity_data.keys())
        baseline_result = {}
        if sorted_costs:
            for inner_key in sensitivity_data[sorted_costs[0]]:
                values = [
                    (cost, sensitivity_data[cost][inner_key])
                    for cost in sorted_costs
                    if inner_key in sensitivity_data[cost]
                ]
                negatives = [(cost, val) for cost, val in values if cost < 0]
                positives = [(cost, val) for cost, val in values if cost > 0]

                if negatives and positives:
                    cost_neg, val_neg = negatives[-1]
                    cost_pos, val_pos = positives[0]

                    interpolated_value = val_neg + (val_pos - val_neg) * (
                        (baseline_cost - cost_neg) / (cost_pos - cost_neg)
                    )
                    baseline_result[inner_key] = interpolated_value

        sensitivity_data[baseline_cost] = baseline_result
    return sensitivity_data


def get_tech_category(full_key: str) -> str | None:
    """DCheck the full_key against the keys in TECHNOLOGIES."""
    for tech_key in TECHNOLOGIES:
        if tech_key in full_key:
            return tech_key
    return None


def build_tech_comp_data(bar_entry: dict, current_tech: str) -> list:
    """Build a list of dictionaries for tech comparison chart."""
    bar_data_list = []
    for full_key, value in bar_entry.items():
        category = get_tech_category(full_key)
        if category is None or category == current_tech:
            continue
        if category in TECHNOLOGIES:
            display_name = TECHNOLOGIES[category]["name"]
            color = TECHNOLOGIES[category]["color"]
            bar_data_list.append(
                {
                    "name": display_name,
                    "value": value,
                    "color": color,
                },
            )
    return bar_data_list


def build_cost_cap_data(sensitivity_data: dict, current_tech: str) -> dict:
    """Build a dictionary for the cost capacity chart data for the selected technology."""
    cost_cap_data = {}
    for x, inner_dict in sensitivity_data.items():
        for key in inner_dict:
            if current_tech in key:
                cost_cap_data[x] = inner_dict[key]
                break
    return cost_cap_data


def filter_region_and_tech(sensitivity_data: dict, region: str) -> dict:
    """Filter data with region."""
    filtered_data = {}

    for cost, inner_dict in sensitivity_data.items():
        filtered_inner_dict = {}
        for full_key, value in inner_dict.items():
            for tech_key in TECHNOLOGIES:
                if tech_key in full_key:
                    parts = full_key.split("-", 1)
                    if parts[0] == region:
                        filtered_inner_dict[full_key] = value
        if filtered_inner_dict:
            filtered_data[cost] = filtered_inner_dict

    return filtered_data
