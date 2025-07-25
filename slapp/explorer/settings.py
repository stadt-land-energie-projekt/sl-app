"""Settings for slapp."""

from __future__ import annotations

import json
import pathlib

from . import chart_data

CONFIG_DIR = pathlib.Path(__file__).parent.parent / "config"

with (CONFIG_DIR / "technologies.json").open("r", encoding="utf-8") as f:
    TECHNOLOGIES = json.load(f)

with (CONFIG_DIR / "nodes.json").open("r", encoding="utf-8") as f:
    NODES = json.load(f)

with (CONFIG_DIR / "demand_colors.json").open("r", encoding="utf-8") as f:
    DEMAND_COLORS = json.load(f)


REGIONS = {
    "r120640428428": "Rüdersdorf",
    "r120640472472": "Strausberg",
    "r120670201201": "Grünheide",
    "r120670124124": "Erkner",
}

TECHNOLOGIES_SELECTED = [
    # "electricity-large_battery_storage",
    # "electricity-small_battery_storage",
    # "heat_low_central-storage",
    # "heat_low_decentral-storage",
    "biomass_gas-bpchp_heat_high",
    "biomass_gas-bpchp_heat_low_central",
    "biomass_gas-bpchp_heat_low_decentral",
    "biomass_solid-boiler_heat_high",
    "biomass_solid-bpchp_heat_high",
    "biomass_solid-bpchp_heat_low_central",
    "biomass_solid-bpchp_heat_low_decentral",
    "electricity-boiler_heat_high",
    "electricity-electrolyzer",
    "electricity-heatpump_central",
    "electricity-heatpump_decentral",
    "electricity-heatpump_heat_high",
    "electricity-pv_agri_horizontal",
    "electricity-pv_agri_vertical",
    "electricity-pv_ground",
    "electricity-pv_rooftop",
    "electricity-wind",
    "h2-boiler_heat_high",
    "h2-bpchp_heat_high",
    "heat_low_decentral-solarthermal_plant",
    "residual_waste-bpchp_heat_high",
    "residual_waste-bpchp_heat_low_central",
]

PREPROCESSED_DATA = chart_data.get_preprocessed_file_df()


def remove_region(row: str) -> str:
    """Remove region string from technology name."""
    return row.split("-", 1)[1]


def get_potentials(scenario: str) -> dict[str, float]:
    """Read through preprocessed datapackage and get all potentials."""
    if scenario == "single":
        return {}  # Only potentials for ALL scenario are used currently

    capacity_potentials = PREPROCESSED_DATA.loc[
        (~PREPROCESSED_DATA["capacity_potential"].isna()) & (PREPROCESSED_DATA["region"].isin(REGIONS)),
        ["name", "capacity_potential"],
    ]
    capacity_potentials["name"] = capacity_potentials["name"].apply(remove_region)
    capacity_potentials = capacity_potentials.groupby("name").sum()
    return capacity_potentials.to_dict()["capacity_potential"]


POTENTIALS = {scenario: get_potentials(scenario) for scenario in ("all", "single")}


def get_capacity_cost_for_technology() -> dict[str, float]:
    """Return capacity cost per technology from preprocessed data."""
    capacity_cost = PREPROCESSED_DATA.loc[
        (~PREPROCESSED_DATA["capacity_cost"].isna()) & (PREPROCESSED_DATA["region"] == next(iter(REGIONS))),
        ["name", "capacity_cost"],
    ]
    capacity_cost["name"] = capacity_cost["name"].apply(remove_region)
    return capacity_cost.set_index("name").to_dict()["capacity_cost"]


CAPACITY_COST = get_capacity_cost_for_technology()
