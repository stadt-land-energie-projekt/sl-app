"""Settings for slapp."""

from __future__ import annotations

import json
import pathlib

from . import chart_data

CONFIG_DIR = pathlib.Path(__file__).parent.parent / "config"

with (CONFIG_DIR / "technologies.json").open("r", encoding="utf-8") as f:
    TECHNOLOGIES = json.load(f)


REGIONS = [
    "r120640428428",
    "r120640472472",
    "r120670124124",
    "r120670201201",
]


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


def get_potentials(scenario: str) -> dict[str, float]:
    """Read through preprocessed datapackage and get all potentials."""

    def remove_region(row: str) -> str:
        return row.split("-", 2)[2]

    if scenario == "single":
        return {}  # Only potentials for ALL scenario are used currently

    preprocessed_data = chart_data.get_preprocessed_file_df()
    capacity_potentials = preprocessed_data.loc[
        (~preprocessed_data["capacity_potential"].isna()) & (preprocessed_data["region"].isin(REGIONS)),
        ["name", "capacity_potential"],
    ]
    capacity_potentials["name"] = capacity_potentials["name"].apply(remove_region)
    capacity_potentials = capacity_potentials.groupby("name").sum()
    return capacity_potentials.to_dict()["capacity_potential"]


POTENTIALS = {scenario: get_potentials(scenario) for scenario in ("all", "single")}
