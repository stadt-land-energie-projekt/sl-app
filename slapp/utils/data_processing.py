"""Module to load (geo-)data into digiplan models."""

from __future__ import annotations

import json
import logging
import pathlib
import re
from typing import TYPE_CHECKING

import pandas as pd

from slapp.explorer.models import Scenario

if TYPE_CHECKING:
    from django.db.models import Model

from config.settings.base import GEODATA_DIR, ZIB_DATA
from slapp.explorer import models
from slapp.utils.ogr_layer_mapping import RelatedModelLayerMapping

ALTERNATIVES_FILENAME = "mga_converted.json"
ALTERNATIVES_REGIONS = ("r120640428428", "r120640472472", "r120670124124", "r120670201201")

REGIONS = [models.Region, models.Municipality]

MODELS = [
    # Clusters
    models.WindTurbine,
    models.PVroof,
    models.PVground,
    models.Hydro,
    models.Biomass,
    models.Combustion,
    models.GSGK,
    models.Storage,
    # Static
    models.AirTraffic,
    models.Aviation,
    models.BiosphereReserve,
    models.DrinkingWaterArea,
    models.FaunaFloraHabitat,
    models.Floodplain,
    models.Forest,
    models.Grid,
    models.Industry,
    models.LandscapeProtectionArea,
    models.LessFavouredAreasAgricultural,
    models.Military,
    models.NatureConservationArea,
    models.Railway,
    models.Road,
    models.RoadRailway500m,
    models.Settlement0m,
    models.SoilQualityLow,
    models.SoilQualityHigh,
    models.SpecialProtectionArea,
    models.Water,
    # PotentialAreas
    models.PotentialareaPVAgricultureLFAOff,
    models.PotentialareaPVRoadRailway,
    models.PotentialareaWindSTP2018Vreg,
    models.PotentialareaWindSTP2027Repowering,
    models.PotentialareaWindSTP2027SearchAreaForestArea,
    models.PotentialareaWindSTP2027SearchAreaOpenArea,
    models.PotentialareaWindSTP2027VR,
]


def load_regions(regions: list[Model] | None = None, *, verbose: bool = True) -> None:
    """Load region geopackages into region models."""
    regions = regions or REGIONS
    for region in regions:
        if region.objects.exists():
            logging.info(
                f"Skipping data for model '{region.__name__}' - Please empty model first if you want to update data.",
            )
            continue
        logging.info(f"Upload data for region '{region.__name__}'")
        if hasattr(region, "data_folder"):
            data_path = pathlib.Path(GEODATA_DIR) / region.data_folder / f"{region.data_file}.gpkg"
        else:
            data_path = pathlib.Path(GEODATA_DIR) / f"{region.data_file}.gpkg"
        instance = RelatedModelLayerMapping(
            model=region,
            data=data_path,
            mapping=region.mapping,
            layer=region.layer,
            transform=4326,
        )
        instance.save(strict=True, verbose=verbose)


def load_data(models: list[Model] | None = None) -> None:
    """Load geopackage-based data into models."""
    models = models or MODELS
    for model in models:
        if model.objects.exists():
            logging.info(
                f"Skipping data for model '{model.__name__}' - Please empty model first if you want to update data.",
            )
            continue
        logging.info(f"Upload data for model '{model.__name__}'")
        if hasattr(model, "data_folder"):
            data_path = pathlib.Path(GEODATA_DIR) / model.data_folder / f"{model.data_file}.gpkg"
        else:
            data_path = pathlib.Path(GEODATA_DIR) / f"{model.data_file}.gpkg"
        instance = RelatedModelLayerMapping(
            model=model,
            data=data_path,
            mapping=model.mapping,
            layer=model.layer,
            transform=4326,
        )
        instance.save(strict=True)


def empty_data(models: list[Model] | None = None) -> None:
    """Delete all data from given models."""
    models = models or MODELS
    for model in models:
        model.objects.all().delete()


def load_base_scenario() -> None:
    """Import base data from ZIB."""
    scenario, created = models.Scenario.objects.get_or_create(
        name="base_scenario",
        defaults={"parameters": {}},
    )
    if not created:
        scenario.result_set.all().delete()

    base_file = pathlib.Path(ZIB_DATA) / "capacities/base" / "scalars.csv"
    results_df = pd.read_csv(base_file, delimiter=";", encoding="utf-8")
    if "scenario" in results_df.columns:
        results_df = results_df.drop("scenario", axis=1)

    results = [models.Result(scenario=scenario, **record) for record in results_df.to_dict(orient="records")]
    models.Result.objects.bulk_create(results)


def load_sensitivities() -> None:
    """Import data from sensitivity runs at ZIB."""
    for sensitivity, sensitivity_lookup in (("capacities", "CapacityCosts"), ("marginal", "MarginalCosts")):
        for folder in (pathlib.Path(ZIB_DATA) / sensitivity).iterdir():
            if not folder.is_dir():
                continue
            if len(folder.name.split("_")) != 2:  # noqa: PLR2004
                # Skip folders which do not follow schema "x_y"
                continue

            # Create Scenario for current sensitivity results
            scenario_name = f"{sensitivity}_{folder.name}"

            if Scenario.objects.filter(name=scenario_name).exists():
                logging.info("Sensitivity scenario '{scenario_name}' already exists. Skipping.")
                continue

            logging.info(f"Upload data for sensitivity '{sensitivity}' from folder '{folder.name}'.")

            with (folder / "scenario.json").open("r", encoding="utf-8") as f:
                scenario_details = json.load(f)
            scenario = models.Scenario(name=scenario_name, parameters=scenario_details)
            scenario.save()

            # Create Sensitivity instance
            sensitivity_data = scenario_details["CostPerturbations"][sensitivity_lookup][0]
            models.Sensitivity(
                scenario=scenario,
                attribute=sensitivity_lookup,
                component=sensitivity_data["VariableName"],
                region=sensitivity_data.get("Region", None),
                perturbation_method=sensitivity_data["PerturbationMethod"],
                # Only one (first) parameter is taken into account
                perturbation_parameter=sensitivity_data["PerturbationParameter"][0],
            ).save()

            # Add results to Scenario
            results_df = pd.read_csv(folder / "scalars.csv", delimiter=";", encoding="utf-8")
            results_df = results_df.drop("scenario", axis=1)
            results = [models.Result(scenario=scenario, **result) for result in results_df.to_dict(orient="records")]
            models.Result.objects.bulk_create(results)


def load_alternatives() -> None:  # noqa: C901, PLR0915
    """Import data for alternative results into related models."""

    def get_region_carrier_component(raw_component: str) -> tuple[str, str, str | None]:
        # Unfortunately composed component name is incompatible with name in results
        # (compare "BB_electricity_liion_battery" with BB-electricity-liion_battery)
        region_ = raw_component.split("_")[0]
        carrier_names = []
        carrier_underscores = 1
        while not (min_results["carrier"] == "_".join(carrier_names)).any():
            carrier_names.append(raw_component.split("_")[carrier_underscores])
            carrier_underscores += 1
        carrier_ = "_".join(carrier_names)
        if len(raw_component) == len(region_) + len(carrier_) + 1:
            # In this case component is only a bus:
            return region_, carrier_, None
        # Strip region and carrier from component name to get component
        component_ = raw_component[len(region_) + len(carrier_) + 2 :]
        return region_, carrier_, component_

    with (pathlib.Path(ZIB_DATA) / ALTERNATIVES_FILENAME).open("r", encoding="utf-8") as f:
        alternative_data = json.load(f)

    for divergence, components in alternative_data.items():
        if models.Alternative.objects.filter(divergence=divergence).exists():
            logging.info("Alternative scenario '{divergence}' already exists. Skipping.")
            continue

        alternative = models.Alternative(divergence=divergence)
        alternative.save()
        for component_raw, result in components.items():
            if "min_results" not in result or "max_results" not in result:
                continue
            min_file = result["min_results"]
            min_results = pd.read_csv(pathlib.Path(ZIB_DATA) / min_file, delimiter=";", encoding="utf-8")
            max_file = result["max_results"]
            max_results = pd.read_csv(pathlib.Path(ZIB_DATA) / max_file, delimiter=";", encoding="utf-8")

            if component_raw.startswith("GenericInvestmentStorageBlock"):
                component_type = "storage capacity"
                # In this case we have an investment of storage capacity
                # Extract component between brackets (i.e. extract "BB_electricity_liion_battery_0" from
                # "GenericInvestmentStorageBlock_invest(BB_electricity_liion_battery_0)")
                composed_component = re.findall(
                    rf"\w*\(((?:{'|'.join(ALTERNATIVES_REGIONS)})\w*)_0\)",
                    component_raw,
                )[0]
                region, carrier, component = get_region_carrier_component(composed_component)
                var_name = "invest_costs"
            else:
                component_type = "capacity"
                # In this case a flow with two components is given
                # i.e. "InvestmentFlowBlock_invest(Brandenburg_heat_decentral_Bayern_heat_decentral_storage_0)"
                matches = re.findall(
                    rf"\w*\(((?:{'|'.join(ALTERNATIVES_REGIONS)})_\w*)_"
                    rf"(((?:{'|'.join(ALTERNATIVES_REGIONS)})\w*))_0\)",
                    component_raw,
                )
                first_component = get_region_carrier_component(matches[0][0])
                second_component = get_region_carrier_component(matches[0][1])
                if first_component[2] is None:
                    region, carrier, component = second_component
                    var_name = f"invest_costs_in_{first_component[1]}"
                    if "storage" in component_raw:
                        component_type = "capacity in"
                else:
                    region, carrier, component = first_component
                    var_name = f"invest_costs_out_{second_component[1]}"
                    if "storage" in component_raw:
                        component_type = "capacity out"

            min_capacity = result["min_obj"]
            max_capacity = result["max_obj"]

            if min_capacity is None or max_capacity is None:
                continue

            min_cost = float(
                min_results.loc[
                    (min_results["region"] == region)
                    & (min_results["carrier"] == carrier)
                    & (min_results["tech"] == component)
                    & (min_results["var_name"] == var_name),
                    "var_value",
                ].iloc[0],
            )

            max_cost = float(
                max_results.loc[
                    (max_results["region"] == region)
                    & (max_results["carrier"] == carrier)
                    & (max_results["tech"] == component)
                    & (max_results["var_name"] == var_name),
                    "var_value",
                ].iloc[0],
            )

            models.AlternativeResult(
                alternative=alternative,
                region=region,
                component=component,
                type=component_type,
                carrier=carrier,
                min_capacity=min_capacity,
                max_capacity=max_capacity,
                min_cost=min_cost,
                max_cost=max_cost,
            ).save()
