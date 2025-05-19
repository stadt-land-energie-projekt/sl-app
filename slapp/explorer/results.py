"""Module to calculate results."""

from __future__ import annotations

from collections import defaultdict
from functools import reduce
from operator import or_

from django.db.models import Prefetch, Q

from .models import AlternativeResult, Result, Scenario, Sensitivity
from .settings import CAPACITY_COST, POTENTIALS, TECHNOLOGIES

INF_STRING = "Keine obere Grenze"


def get_technologies() -> set[str]:
    """
    Get technologies from results.

    Exclude transmissions and system.
    """
    technologies = Result.objects.distinct().values_list("name", flat=True)
    return {
        com.split("-", 1)[1] if len(com.split("-", 1)) > 1 else com
        for com in technologies
        if "transmission" not in com and com != "system"
    }


def get_invests_in_results() -> dict[str, str]:
    """
    Return technologies and related invest attributes.

    For storages return "invest", otherwise return "invest_out_<bus_name>".
    """
    invests = Result.objects.filter(var_name__startswith="invest").distinct().values_list("name", "var_name")
    return {
        name: var_name
        for (name, var_name) in invests
        if ("storage" in name and var_name == "invest")
        or ("storage" not in name and var_name.startswith("invest_out"))
    }


def get_sensitivity_result(sensitivity: str, region: str, technology: str) -> dict[float, dict[str, float]]:
    """Return resulting capacities for given sensitivity."""
    invest_technologies = get_invests_in_results()
    capacity_query = reduce(
        or_,
        [Q(name=technology, var_name=capacity_name) for technology, capacity_name in invest_technologies.items()],
    )
    sensitivities = (
        Sensitivity.objects.filter(attribute=sensitivity, component=technology, region=region)
        .select_related("scenario")
        .prefetch_related(
            Prefetch(
                "scenario__result_set",
                queryset=Result.objects.filter(capacity_query, var_value__gt=0),
                to_attr="results",
            ),
        )
        .all()
    )

    results = {
        sensitivity.perturbation_parameter: {result.name: result.var_value for result in sensitivity.scenario.results}
        for sensitivity in sensitivities
    }
    return results


def merge_sensitivity_results(results: dict[float, dict[str, float]]) -> dict[float, dict[str, float]]:
    """Combine technologies, regions and central/decentral sensitivity results."""
    merged_results = {}
    for key in results:
        merged_results[key] = defaultdict(float)
        for technology_raw, value in results[key].items():
            # Strip region
            technology = technology_raw.split("-", 1)[1]
            # Group technologies
            if "pv" in technology:
                technology = "electricity-pv"
            if "heatpump" in technology:
                technology = "electricity-heatpump"
            if "storage" in technology and "electricity" in technology:
                technology = "electricity-storage"
            if "storage" in technology and "heat" in technology:
                technology = "heat-storage"
            if "bpchp" in technology and "h2" not in technology:
                technology = "bpchp"
            if "boiler" in technology and "h2" not in technology:
                technology = "boiler"
            merged_results[key][technology] += value
    return merged_results


def get_alternative_result(region: str, divergence: float) -> dict:  # noqa: ARG001
    """Return Alternative Results for ranges by region."""
    results = AlternativeResult.objects.filter(
        # region=region,  # Not used currently, only Verbund available
        alternative__divergence=divergence,
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


def get_base_scenario(**result_filter) -> dict:
    """Return base_scenarios."""
    try:
        scenario = Scenario.objects.get(name="base_scenario")
    except Scenario.DoesNotExist:
        return {}

    base_scenario = {}

    investment_technologies = get_invests_in_results()
    for tech, cap in investment_technologies.items():
        result = scenario.result_set.filter(name=tech, var_name=cap, **result_filter).first()
        if result:
            base_scenario[tech] = result.var_value

    return base_scenario


def get_tech_category(full_key: str) -> str | None:
    """Check the full_key against the keys in TECHNOLOGIES."""
    for tech_key in TECHNOLOGIES:
        if tech_key in full_key:
            return tech_key
    return None


def calculate_capacity_cost_for_technology(technology: str, sensitivity_data: dict[float, dict]) -> dict[float, dict]:
    """Multiply capacity cost for technology from preprocessed data with sensitivity data perturbations."""
    base_technology_cost = CAPACITY_COST.get(technology, 0)
    sensitivity_data = {
        round(cost * base_technology_cost if cost != 0 else base_technology_cost): technologies
        for cost, technologies in sensitivity_data.items()
    }
    return sensitivity_data


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
        ([round(float(k)), v] for k, v in cost_cap_data.items()),
        key=lambda item: item[0],
    )

    return array_data


def filter_alternatives(alternatives: dict, selected_tech: dict) -> dict:
    """Filter alternatives with selected technologies in settings.py."""
    selected = {}
    for tech in alternatives:
        if tech in selected_tech:
            selected[tech] = alternatives[tech]
    return selected


def get_potential(technology: str) -> str | float:
    """Return potential per technology."""
    potential = POTENTIALS["all"].get(technology, INF_STRING)
    if isinstance(potential, float):
        return round(potential, 1)
    return potential


def get_potential_unit(technology: str, value: str | float) -> str:
    """Return potential unit per technology."""
    if value == INF_STRING:
        return ""
    return "MWh" if "storage" in technology else "MW"


def get_technology_color(technology: str) -> str:
    """Return color per technology."""
    if technology in TECHNOLOGIES:
        return TECHNOLOGIES[technology]["color"]
    if technology_stripped := technology.split("-", 1)[1] in TECHNOLOGIES:
        return TECHNOLOGIES[technology_stripped]["color"]
    return "#000000"


def prepare_table_data(alternatives: dict) -> dict:
    """Return given dictionary prepared for table."""
    for tech, data in alternatives.items():
        data["tech_name"] = TECHNOLOGIES.get(tech, {"name": tech})["name"]
        data["cap_str"] = format_min_max(data["min_capacity"], data["max_capacity"], "cap")
        data["cost_str"] = format_min_max(data["min_cost"], data["max_cost"], "cost")
        data["pot_str"] = f"{data['potential']} {data['potential_unit']}"
    return alternatives


def format_min_max(min_value: float, max_value: float, unit: str) -> str:
    """Return formatted string for table."""
    # Decide if both values should be converted to millions:
    million = 1_000_000
    if max_value >= million:
        # Convert both to millions
        converted_min = round(min_value / million, 1)
        converted_max = round(max_value / million, 1)

        if unit == "cost":
            unit_str = "Mio €"
        elif unit == "cap":
            unit_str = "TW"
        else:
            unit_str = ""

        return f"{converted_min} - {converted_max} {unit_str}"

    # Otherwise, use thousands
    thousand = 1_000
    if max_value >= thousand:
        converted_min = round((min_value / thousand), 1)
        converted_max = round((max_value / thousand), 1)

        if unit == "cost":
            unit_str = "k€"
        elif unit == "cap":
            unit_str = "GW"
        else:
            unit_str = ""

        return f"{converted_min} - {converted_max} {unit_str}"

    converted_min = round(min_value, 1)
    converted_max = round(max_value, 1)

    if unit == "cost":
        unit_str = "k€"
    elif unit == "cap":
        unit_str = "MW"
    else:
        unit_str = ""

    return f"{converted_min} - {converted_max} {unit_str}"
