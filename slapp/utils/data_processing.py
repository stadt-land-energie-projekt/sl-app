"""Module to load (geo-)data into digiplan models."""

from __future__ import annotations

import json
import logging
import pathlib
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from django.db.models import Model

from config.settings.base import GEODATA_DIR, ZIB_DATA
from slapp.explorer import models
from slapp.utils.ogr_layer_mapping import RelatedModelLayerMapping

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


def load_sensitivities() -> None:
    """Import data from sensitivity runs at ZIB."""
    for sensitivity, sensitivity_lookup in (("capacities", "CapacityCosts"), ("marginal", "MarginalCosts")):
        for folder in (pathlib.Path(ZIB_DATA) / sensitivity).iterdir():
            if not folder.is_dir():
                continue
            if len(folder.name.split("_")) != 2:  # noqa: PLR2004
                # Skip folders which do not follow schema "x_y"
                continue

            logging.info(f"Upload data for sensitivity '{sensitivity}' from folder '{folder.name}'.")

            # Create Scenario for current sensitivity results
            scenario_name = f"{sensitivity}_{folder.name}"
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
