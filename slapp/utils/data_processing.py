"""Module to load (geo-)data into digiplan models."""

from __future__ import annotations

import logging
import pathlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Model

from config.settings.base import GEODATA_DIR
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
    #models.PotentialareaWindSTP2027Repowering,
    #models.PotentialareaWindSTP2027SearchAreaForestArea,
    #models.PotentialareaWindSTP2027SearchAreaOpenArea,
    #models.PotentialareaWindSTP2027VR,
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
