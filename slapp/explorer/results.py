"""Module to calculate results."""

from __future__ import annotations

from collections import namedtuple
from functools import reduce
from operator import or_

from django.db.models import Prefetch, Q

from .models import AlternativeResult, Result, Scenario, Sensitivity
from .settings import TECHNOLOGIES, TECHNOLOGIES_RANGES

ResultEntry = namedtuple("ResultEntry", ["name", "var_name"])  # noqa: PYI024

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


def get_alternative_result(region: str, divergence: int) -> dict:
    """Return Alternative Results for ranges by region."""
    results = AlternativeResult.objects.filter(
        region=region,
        alternative_id=divergence,
    )

    data_for_region_and_divergence = {}
    for r in results:
        data_for_region_and_divergence[r.component] = {
            "min_capacity": r.min_capacity,
            "max_capacity": r.max_capacity,
            "min_cost": r.min_cost,
            "max_cost": r.max_cost,
            "carrier": r.carrier,
            "type": r.type,
        }

    return data_for_region_and_divergence


def get_base_scenario() -> dict:
    """Return base_scenarios."""
    try:
        scenario = Scenario.objects.get(name="base_scenario")
    except Scenario.DoesNotExist:
        return {}

    base_scenario = {}

    for tech, cap in CAPACITIES.items():
        result = scenario.result_set.filter(name=tech, var_name=cap).first()
        if result:
            base_scenario[tech] = result.var_value

    return base_scenario


def get_tech_category(full_key: str) -> str | None:
    """Check the full_key against the keys in TECHNOLOGIES."""
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
        display_name = TECHNOLOGIES[category]["name"]
        color = TECHNOLOGIES[category]["color"]
        bar_data_list.append(
            {
                "name": display_name,
                "value": value,
                "color": color,
            },
        )
    bar_data_list = sorted(bar_data_list, key=lambda tech: tech["value"])
    return bar_data_list


def build_cost_cap_data(sensitivity_data: dict, current_tech: str) -> [float, float]:
    """Build a dictionary for the cost capacity chart data for the selected technology."""
    cost_cap_data = {}
    for x, inner_dict in sensitivity_data.items():
        for key in inner_dict:
            if current_tech in key:
                cost_cap_data[x] = inner_dict[key]
                break

    array_data = sorted(
        ([float(k), v] for k, v in cost_cap_data.items()),
        key=lambda item: item[0],
    )

    return array_data


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


def filter_alternatives(alternatives: dict, selected_tech: dict) -> dict:
    """Filter alternatives with selected technologies in settings.py."""
    selected = {}
    for tech in alternatives:
        if tech in selected_tech:
            selected[tech] = alternatives[tech]
    return selected


def get_potential(technology: str) -> str:
    """Return potential per technology."""
    return TECHNOLOGIES_RANGES.get(technology, {}).get("potential", None)


def get_potential_unit(technology: str) -> str:
    """Return potential unit per technology."""
    return TECHNOLOGIES_RANGES.get(technology, {}).get("unit", "")


def get_technology_color(technology: str) -> str:
    """Return color per technology."""
    return TECHNOLOGIES.get(technology, {}).get("color", "#000000")


def prepare_table_data(alternatives: dict) -> dict:
    """Return given dictionary prepared for table."""
    for tech, data in alternatives.items():
        data["tech_name"] = TECHNOLOGIES[tech]["name"]
        data["cap_str"] = format_min_max(data["min_capacity"], data["max_capacity"], "cap")
        data["cost_str"] = format_min_max(data["min_cost"], data["max_cost"], "cost")
        data["pot_str"] = f"{data['potential']} {data['potential_unit']}"
    return alternatives


def format_min_max(min_value: float, max_value: float, unit: str) -> str:
    """Return formatted string for table."""
    # Decide if both values should be converted to millions:
    million = 1_000_000
    if min_value >= million or min_value == 0 and max_value >= million:
        # Convert both to millions
        converted_min = round(min_value / million)
        converted_max = round(max_value / million)

        if unit == "cost":
            unit_str = "Mio €"
        elif unit == "cap":
            unit_str = "MW"
        else:
            unit_str = ""

        return f"{converted_min} - {converted_max} {unit_str}"
    # Otherwise, use thousands
    thousand = 1_000
    converted_min = round((min_value / thousand), 1)
    converted_max = round((max_value / thousand), 1)

    if unit == "cost":
        unit_str = "k€"
    elif unit == "cap":
        unit_str = "kW"
    else:
        unit_str = ""

    return f"{converted_min} - {converted_max} {unit_str}"
