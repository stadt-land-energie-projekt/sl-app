"""Charts and Data for Regions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from django.conf import settings
from django.contrib.gis.db.models.functions import Envelope

from .models import Region


def get_regions_data() -> list:
    """Return the list of dictionaries containing region data."""
    region_bbox = {
        entry["name"]: entry["bounding_box"]
        for entry in Region.objects.annotate(bounding_box=Envelope("geom")).values("bounding_box", "name")
    }
    region_data = pd.read_csv(str(settings.DATA_DIR.path("regions").path("municipality_data.csv")), index_col="name")
    region_data.columns = region_data.columns.map(lambda x: x.split("_", 1)[1] if "capacity" in x else x)

    basic_data = region_data.loc[:, ["area", "population"]].to_dict(orient="index")

    capacity = region_data.loc[:, ["wind", "pv_ground", "pv_roof", "bio"]].to_dict(orient="index")

    capacity_potential = region_data.loc[
        :,
        [column for column in region_data.columns if column.startswith("potential")],
    ]
    capacity_potential.columns = ["pv_ground", "pv_roof", "wind"]
    capacity_potential = capacity_potential.to_dict(orient="index")

    power_demand = region_data.loc[
        :,
        [column for column in region_data.columns if "demand" in column and "power" in column],
    ]
    power_demand.columns = [column.split("_")[1] for column in power_demand.columns]
    power_demand = power_demand.to_dict(orient="index")

    heat_demand_central = region_data.loc[
        :,
        [column for column in region_data.columns if "demand" in column and "heat" in column and "cen" in column],
    ]
    heat_demand_central.columns = [column.split("_")[1] for column in heat_demand_central.columns]
    heat_demand_central = heat_demand_central.to_dict(orient="index")

    heat_demand_decentral = region_data.loc[
        :,
        [column for column in region_data.columns if "demand" in column and "heat" in column and "dec" in column],
    ]
    heat_demand_decentral.columns = [column.split("_")[1] for column in heat_demand_decentral.columns]
    heat_demand_decentral = heat_demand_decentral.to_dict(orient="index")
    return [
        {
            "title": "Region Oderland-Spree",
            "bbox": region_bbox["Oderland-Spree"],
            "info": "Hier steht mehr Info über die Region Oderland-Spree",
            "img_source": "Oderland-Spree-Map.png",
            "text": "Sie ist eine dynamische Region im Osten Brandenburgs, in der ländliche und städtische Strukturen "
            "aufeinandertreffen. Die Nähe zu Berlin, die Ansiedlung großer Industrieprojekte und der hohe Anteil "
            "erneuerbarer Energien machen sie zu einem spannenden Beispiel für die Energiewende im Stadt-Land-Nexus.",
            "keyfacts": [
                {
                    "title": "Struktur",
                    "fact": "Mischung aus ländlichen Gebieten und kleineren Städten",
                    "icon": "/static/images/icons/case-study-structure.svg",
                },
                {
                    "title": "Besonderheiten",
                    "fact": "Tesla-Gigafactory als wirtschaftlicher Impulsgeber, Großes, "
                    "erfolgreiches H2-Kavernen-Speicherprojekt",
                    "icon": "/static/images/icons/case-study-particularity.svg",
                },
                {
                    "title": "Erneuerbare Energien",
                    "fact": "Hoher Anteil an Wind- und Solarenergie, "
                    "Genehmigter Anschlusspunkt an das Wasserstoffkernnetz",
                    "icon": "/static/images/icons/case-study-renewable.svg",
                },
                {
                    "title": "Herausforderung",
                    "fact": "Energieinfrastruktur für wachsende Industrie und Bevölkerung",
                    "icon": "/static/images/icons/case-study-challenge.svg",
                },
            ],
            "basic_data": basic_data,
            "capacity": capacity,
            "capacity_potential": capacity_potential,
            "full_load_hours": {
                "wind": 1500,
                "pv_ground": 910,
                "pv_roof": 750,
                "bio": 6000,
            },
            "demand_power": power_demand,
            "demand_heat_cen": heat_demand_central,
            "demand_heat_dec": heat_demand_decentral,
        },
        {
            "title": "Region Kiel",
            "bbox": region_bbox["Kiel"],
            "info": "Hier steht mehr Info über die Region Kiel",
            "img_source": "Kiel-Map.png",
            "text": "Die Stadt ist ein bedeutender Standort für die Schiffbauindustrie, Offshore-Windenergie und "
            "innovative Forschung. Die starke Verbindung zur Ostsee prägt das wirtschaftliche und kulturelle "
            "Leben Kiels und macht die Region zu einem wichtigen Akteur der nachhaltigen maritimen Entwicklung.",
            "keyfacts": [
                {
                    "title": "Struktur",
                    "fact": "Mischung aus Hafenwirtschaft, Wissenschaft und urbanem Leben",
                    "icon": "/static/images/icons/case-study-structure.svg",
                },
                {
                    "title": "Besonderheit",
                    "fact": "Hafen als Knotenpunkt für Schifffahrt und internationale Logistik",
                    "icon": "/static/images/icons/case-study-particularity.svg",
                },
                {
                    "title": "Erneuerbare Energien",
                    "fact": "Offshore-Windenergie und nachhaltige Mobilitätsprojekte",
                    "icon": "/static/images/icons/case-study-renewable.svg",
                },
                {
                    "title": "Herausforderung",
                    "fact": "Transformation der Werftindustrie und Anpassung an den Klimawandel",
                    "icon": "/static/images/icons/case-study-challenge.svg",
                },
            ],
            # TODO: Insert data for Kiel  # noqa: TD002, TD003
        },
    ]


def get_case_studies_charts_data(region_name: str) -> dict:
    """Get data for all case studies charts."""
    regions = get_regions_data()

    selected_region = None
    for reg in regions:
        if reg["title"] == region_name:
            selected_region = reg
            break

    if not selected_region:
        selected_region = regions[0]

    region_data = pd.DataFrame(municipalities_details(None)).sort_values("id").set_index("name")

    x_axis_data = region_data.index.to_list()

    charts_data = {
        "area": {
            "x_data": [""],
            "y_data": region_data["area"].apply(lambda _: [_]).to_dict(),
            "y_label": "km²",
        },
        "population": {
            "x_data": [""],
            "y_data": region_data["population"].apply(lambda _: [_]).to_dict(),
            "y_label": "",
        },
        "capacity": {
            "x_data": x_axis_data,
            "y_data": {
                "Wind": region_data["capacity_wind"].to_list(),
                "PV Freifläche": region_data["capacity_pv_ground"].to_list(),
                "PV Dach": region_data["capacity_pv_roof"].to_list(),
                "Bioenergie": region_data["capacity_bio"].to_list(),
            },
            "y_label": "MW",
            # "target": {"Regionalziel 2032": 100},  # noqa: ERA001
        },
        "capacity_potential": {
            "x_data": x_axis_data,
            "y_data": {
                "Wind": region_data["potentialarea_wind_installable_power"].to_list(),
                "PV Freifläche": region_data["potentialarea_pv_ground_installable_power"].to_list(),
                "PV Dach": region_data["potentialarea_pv_roof_installable_power"].to_list(),
            },
            "y_label": "MW",
        },
        "capacity_potential_usage": {
            "x_data": x_axis_data,
            "y_data": {
                "Wind": region_data["capacity_potential_usage_wind"].to_list(),
                "PV Freifläche": region_data["capacity_potential_usage_pv_ground"].to_list(),
                "PV Dach": region_data["capacity_potential_usage_pv_roof"].to_list(),
            },
            "y_label": "%",
        },
        "production": {
            "x_data": x_axis_data,
            "y_data": {
                "Wind": region_data["production_wind"].to_list(),
                "PV Freifläche": region_data["production_pv_ground"].to_list(),
                "PV Dach": region_data["production_pv_roof"].to_list(),
                "Bioenergie": region_data["production_bio"].to_list(),
            },
            "y_label": "GWh",
        },
        "production_specific": {
            "x_data": x_axis_data,
            "y_data": {
                "pro Hektar": region_data["production_total_per_ha"].to_list(),
                "pro Kopf": region_data["production_total_per_capita"].to_list(),
            },
            "y_label": "MWh",
        },
        "demand_power": {
            "x_data": x_axis_data,
            "y_data": {
                "Haushalte": region_data["demand_hh_power_demand"].to_list(),
                "GHD": region_data["demand_cts_power_demand"].to_list(),
                "Industrie": region_data["demand_ind_power_demand"].to_list(),
            },
            "y_label": "GWh",
        },
        "self_generation": {
            "x_data": x_axis_data,
            "y_data": {
                "Deckung": region_data["production_total"]
                .div(region_data["power_demand_total"])
                .mul(100)
                .round(1)
                .to_list(),
            },
            "y_label": "%",
        },
        "demand_heat": {
            "x_data": x_axis_data,
            "y_data": {
                "Haushalte": region_data[["demand_hh_heat_demand_cen", "demand_hh_heat_demand_dec"]]
                .sum(axis=1)
                .round(1)
                .to_list(),
                "GHD": region_data[["demand_cts_heat_demand_cen", "demand_cts_heat_demand_dec"]]
                .sum(axis=1)
                .round(1)
                .to_list(),
                "Industrie": region_data[["demand_ind_heat_demand_cen", "demand_ind_heat_demand_dec"]]
                .sum(axis=1)
                .round(1)
                .to_list(),
            },
            "y_label": "GWh",
        },
        "demand_heat_type": {
            "x_data": [""],
            "y_data": {
                "Fernwärme": [
                    round(
                        region_data["heat_demand_cen_total"].sum()
                        / region_data[["heat_demand_cen_total", "heat_demand_dec_total"]].sum().sum()
                        * 100,
                        1,
                    ),
                ],
                "Dezentral": [
                    round(
                        region_data["heat_demand_dec_total"].sum()
                        / region_data[["heat_demand_cen_total", "heat_demand_dec_total"]].sum().sum()
                        * 100,
                        1,
                    ),
                ],
            },
        },
    }

    return charts_data


def municipalities_details(names: list[str]) -> list[dict[str, Any]]:  # noqa: ARG001
    """Return data for given municipalities from CSV."""
    # TODO (henhuy): Get data depending on selected region
    # https://github.com/stadt-land-energie-projekt/sl-app/issues/242

    municipalities = pd.read_csv(str(settings.DATA_DIR.path("regions").path("municipality_data.csv")))
    with Path.open(str(settings.DATA_DIR.path("regions").path("technology_data.json"))) as f:
        tech_data = json.load(f)
    flh = pd.Series(tech_data["full_load_hours"])

    production_cols = {
        f"production_{tech}": municipalities[f"capacity_{tech}"].mul(flh[tech]).div(1e3).round(1)
        for tech in ["wind", "pv_ground", "pv_roof", "bio"]
    }
    capacity_potential_usage_cols = {
        f"capacity_potential_usage_{tech}": municipalities[f"capacity_{tech}"]
        .div(
            municipalities[f"potentialarea_{tech}_installable_power"],
        )
        .fillna(0)
        .mul(100)
        .replace(np.inf, 100)
        .round(1)
        for tech in ["wind", "pv_ground", "pv_roof"]
    }

    # Aggregate production, demand, potentials
    municipalities = municipalities.assign(
        capacity_total=municipalities.filter(like="capacity_").sum(axis=1).round(1),
        potentialarea_total_installable_power=municipalities.filter(like="potentialarea_").sum(axis=1).round(1),
        power_demand_total=municipalities.filter(like="_power_demand").sum(axis=1).round(1),
        heat_demand_total=municipalities.filter(like="_heat_demand_").sum(axis=1).round(1),
        heat_demand_cen_total=municipalities.filter(like="_heat_demand_cen").sum(axis=1).round(1),
        heat_demand_dec_total=municipalities.filter(like="_heat_demand_dec").sum(axis=1).round(1),
        **production_cols,
        **capacity_potential_usage_cols,
    )
    municipalities["production_total"] = municipalities.filter(like="production_").sum(axis=1).round(1)
    municipalities["production_total_per_ha"] = (
        municipalities["production_total"].div(municipalities["area"] * 100).mul(1e3).round(1)
    )
    municipalities["production_total_per_capita"] = (
        municipalities["production_total"].div(municipalities["population"]).mul(1e3).round(1)
    )
    municipalities["capacity_potential_usage_total"] = (
        municipalities["capacity_total"]
        .div(
            municipalities["potentialarea_total_installable_power"],
        )
        .mul(100)
        .round(1)
    )
    municipalities["energy_demand_total"] = (
        municipalities[["power_demand_total", "heat_demand_total"]].sum(axis=1).round(1)
    )

    return municipalities.to_dict(orient="records")


def get_energy_data(region: str) -> list:
    """Return energy data."""
    energy_data = {}
    if region == "verbu":
        energy_data = [
            {
                "title": "Stromaustausch (Verbund)",
                "energyData": [
                    {"source": "Strausberg", "target": "Rüdersdorf bei Berlin", "value": 120},
                    {"source": "Rüdersdorf bei Berlin", "target": "Strausberg", "value": 20},
                    {"source": "Rüdersdorf bei Berlin", "target": "Grünheide (Mark)", "value": 80},
                    {"source": "Grünheide (Mark)", "target": "Rüdersdorf bei Berlin", "value": 200},
                    {"source": "Grünheide (Mark)", "target": "Erkner", "value": 150},
                    {"source": "Erkner", "target": "Grünheide (Mark)", "value": 50},
                    {"source": "Erkner", "target": "Strausberg", "value": 100},
                    {"source": "Strausberg", "target": "Erkner", "value": 10},
                    {"source": "Strausberg", "target": "Grünheide (Mark)", "value": 50},
                    {"source": "Grünheide (Mark)", "target": "Strausberg", "value": 5},
                    {"source": "Rüdersdorf bei Berlin", "target": "Erkner", "value": 90},
                    {"source": "Erkner", "target": "Rüdersdorf bei Berlin", "value": 120},
                    {"source": "Strausberg", "target": "Netz", "value": 120},
                    {"source": "Netz", "target": "Strausberg", "value": 20},
                    {"source": "Grünheide (Mark)", "target": "Netz ", "value": 10},
                    {"source": "Netz ", "target": "Grünheide (Mark)", "value": 100},
                    {"source": "Erkner", "target": "Netz  ", "value": 120},
                    {"source": "Netz  ", "target": "Erkner", "value": 20},
                    {"source": "Rüdersdorf bei Berlin", "target": "Netz   ", "value": 100},
                    {"source": "Netz   ", "target": "Rüdersdorf bei Berlin", "value": 40},
                ],
                "nodes": [
                    {"name": "Strausberg", "x": 50, "y": -50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
                    {
                        "name": "Rüdersdorf bei Berlin",
                        "x": 0,
                        "y": 0,
                        "itemStyle": {"color": "#798897"},
                        "symbolSize": 30,
                    },
                    {
                        "name": "Grünheide (Mark)",
                        "x": 50,
                        "y": 50,
                        "itemStyle": {"color": "#798897"},
                        "symbolSize": 30,
                    },
                    {"name": "Erkner", "x": -10, "y": 50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
                    {"name": "Netz", "x": 80, "y": -25, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz ", "x": 60, "y": 75, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz  ", "x": -20, "y": 75, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz   ", "x": -20, "y": -20, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                ],
            },
            {
                "title": "Wasserstoffaustausch (Verbund)",
                "energyData": [
                    {"source": "Strausberg", "target": "Rüdersdorf bei Berlin", "value": 120},
                    {"source": "Rüdersdorf bei Berlin", "target": "Strausberg", "value": 20},
                    {"source": "Rüdersdorf bei Berlin", "target": "Grünheide (Mark)", "value": 80},
                    {"source": "Grünheide (Mark)", "target": "Rüdersdorf bei Berlin", "value": 200},
                    {"source": "Grünheide (Mark)", "target": "Erkner", "value": 150},
                    {"source": "Erkner", "target": "Grünheide (Mark)", "value": 50},
                    {"source": "Erkner", "target": "Strausberg", "value": 100},
                    {"source": "Strausberg", "target": "Erkner", "value": 10},
                    {"source": "Strausberg", "target": "Grünheide (Mark)", "value": 50},
                    {"source": "Grünheide (Mark)", "target": "Strausberg", "value": 5},
                    {"source": "Rüdersdorf bei Berlin", "target": "Erkner", "value": 90},
                    {"source": "Erkner", "target": "Rüdersdorf bei Berlin", "value": 120},
                    {"source": "Strausberg", "target": "Netz", "value": 120},
                    {"source": "Netz", "target": "Strausberg", "value": 20},
                    {"source": "Grünheide (Mark)", "target": "Netz ", "value": 10},
                    {"source": "Netz ", "target": "Grünheide (Mark)", "value": 100},
                    {"source": "Erkner", "target": "Netz  ", "value": 120},
                    {"source": "Netz  ", "target": "Erkner", "value": 20},
                    {"source": "Rüdersdorf bei Berlin", "target": "Netz   ", "value": 100},
                    {"source": "Netz   ", "target": "Rüdersdorf bei Berlin", "value": 40},
                ],
                "nodes": [
                    {"name": "Strausberg", "x": 50, "y": -50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
                    {
                        "name": "Rüdersdorf bei Berlin",
                        "x": 0,
                        "y": 0,
                        "itemStyle": {"color": "#798897"},
                        "symbolSize": 30,
                    },
                    {
                        "name": "Grünheide (Mark)",
                        "x": 50,
                        "y": 50,
                        "itemStyle": {"color": "#798897"},
                        "symbolSize": 30,
                    },
                    {"name": "Erkner", "x": -10, "y": 50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
                    {"name": "Netz", "x": 80, "y": -25, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz ", "x": 60, "y": 75, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz  ", "x": -20, "y": 75, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz   ", "x": -20, "y": -20, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                ],
            },
        ]
    elif region == "einzeln":
        energy_data = [
            {
                "title": "Stromaustausch (einzeln)",
                "energyData": [
                    {"source": "Strausberg", "target": "Netz", "value": 120},
                    {"source": "Netz", "target": "Strausberg", "value": 20},
                    {"source": "Grünheide (Mark)", "target": "Netz ", "value": 10},
                    {"source": "Netz ", "target": "Grünheide (Mark)", "value": 100},
                    {"source": "Erkner", "target": "Netz  ", "value": 120},
                    {"source": "Netz  ", "target": "Erkner", "value": 20},
                    {"source": "Rüdersdorf bei Berlin", "target": "Netz   ", "value": 100},
                    {"source": "Netz   ", "target": "Rüdersdorf bei Berlin", "value": 40},
                ],
                "nodes": [
                    {"name": "Strausberg", "x": 50, "y": -50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
                    {
                        "name": "Rüdersdorf bei Berlin",
                        "x": 0,
                        "y": 0,
                        "itemStyle": {"color": "#798897"},
                        "symbolSize": 30,
                    },
                    {
                        "name": "Grünheide (Mark)",
                        "x": 50,
                        "y": 50,
                        "itemStyle": {"color": "#798897"},
                        "symbolSize": 30,
                    },
                    {"name": "Erkner", "x": -10, "y": 50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
                    {"name": "Netz", "x": 80, "y": -25, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz ", "x": 60, "y": 75, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz  ", "x": -20, "y": 75, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz   ", "x": -20, "y": -20, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                ],
            },
            {
                "title": "Wasserstoffaustausch (einzeln)",
                "energyData": [
                    {"source": "Strausberg", "target": "Netz", "value": 120},
                    {"source": "Netz", "target": "Strausberg", "value": 20},
                    {"source": "Grünheide (Mark)", "target": "Netz ", "value": 10},
                    {"source": "Netz ", "target": "Grünheide (Mark)", "value": 100},
                    {"source": "Erkner", "target": "Netz  ", "value": 120},
                    {"source": "Netz  ", "target": "Erkner", "value": 20},
                    {"source": "Rüdersdorf bei Berlin", "target": "Netz   ", "value": 100},
                    {"source": "Netz   ", "target": "Rüdersdorf bei Berlin", "value": 40},
                ],
                "nodes": [
                    {"name": "Strausberg", "x": 50, "y": -50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
                    {
                        "name": "Rüdersdorf bei Berlin",
                        "x": 0,
                        "y": 0,
                        "itemStyle": {"color": "#798897"},
                        "symbolSize": 30,
                    },
                    {
                        "name": "Grünheide (Mark)",
                        "x": 50,
                        "y": 50,
                        "itemStyle": {"color": "#798897"},
                        "symbolSize": 30,
                    },
                    {"name": "Erkner", "x": -10, "y": 50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
                    {"name": "Netz", "x": 80, "y": -25, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz ", "x": 60, "y": 75, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz  ", "x": -20, "y": 75, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                    {"name": "Netz   ", "x": -20, "y": -20, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                ],
            },
        ]
    elif region == "kiel":
        energy_data = [
            {
                "title": "Stromaustausch (Kiel)",
                "energyData": [
                    {"source": "Kiel", "target": "Netz", "value": 120},
                    {"source": "Netz", "target": "Kiel", "value": 20},
                ],
                "nodes": [
                    {"name": "Kiel", "x": 0, "y": 0, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
                    {"name": "Netz", "x": 25, "y": 0, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                ],
            },
            {
                "title": "Wasserstoffaustausch (Kiel)",
                "energyData": [
                    {"source": "Kiel", "target": "Netz", "value": 120},
                    {"source": "Netz", "target": "Kiel", "value": 20},
                ],
                "nodes": [
                    {"name": "Kiel", "x": 0, "y": 0, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
                    {"name": "Netz", "x": 25, "y": 0, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
                ],
            },
        ]
    return energy_data
