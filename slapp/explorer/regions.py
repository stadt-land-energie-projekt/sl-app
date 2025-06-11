"""Charts and Data for Regions."""
from __future__ import annotations

import numpy as np
import pandas as pd
from django.contrib.gis.db.models.functions import Envelope
from django.db.models import Sum
from django.db.models.functions import Round

from .models import Municipality, Region


def get_regions_data() -> list:
    """Return the list of dictionaries containing region data."""
    region_bbox = {
        entry["name"]: entry["bounding_box"]
        for entry in Region.objects.annotate(bounding_box=Envelope("geom")).values("bounding_box", "name")
    }
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
                    "fact": "Tesla-Gigafactory als wirtschaftlicher Impulsgeber, Großes, erfolgreiches H2-Kavernen-Speicherprojekt",
                    "icon": "/static/images/icons/case-study-particularity.svg",
                },
                {
                    "title": "Erneuerbare Energien",
                    "fact": "Hoher Anteil an Wind- und Solarenergie, Genehmigter Anschlusspunkt an das Wasserstoffkernnetz",
                    "icon": "/static/images/icons/case-study-renewable.svg",
                },
                {
                    "title": "Herausforderung",
                    "fact": "Energieinfrastruktur für wachsende Industrie und Bevölkerung",
                    "icon": "/static/images/icons/case-study-challenge.svg",
                },
            ],
            "basic_data": {
                "Rüdersdorf": {"area": 70.1, "population": 16079},
                "Strausberg": {"area": 67.6, "population": 27456},
                "Erkner": {"area": 17.7, "population": 12019},
                "Grünheide": {"area": 126.4, "population": 9189},
            },
            "capacity": {
                "Rüdersdorf": {"wind": 4.2, "pv_ground": 20.4, "pv_roof": 6.8, "bio": 2.2},
                "Strausberg": {"wind": 0, "pv_ground": 2.3, "pv_roof": 4.0, "bio": 3.1},
                "Erkner": {"wind": 0, "pv_ground": 0, "pv_roof": 1.6, "bio": 0},
                "Grünheide": {"wind": 0, "pv_ground": 0, "pv_roof": 4.5, "bio": 0},
            },
            "capacity_potential": {
                "Rüdersdorf": {"wind": 0, "pv_ground": 1509.7, "pv_roof": 132.3},
                "Strausberg": {"wind": 0, "pv_ground": 733.2, "pv_roof": 135.6},
                "Erkner": {"wind": 0, "pv_ground": 0, "pv_roof": 49.1},
                "Grünheide": {"wind": 92.0, "pv_ground": 163.0, "pv_roof": 77.9},
            },
            "full_load_hours": {
                "wind": 1500,
                "pv_ground": 910,
                "pv_roof": 750,
                "bio": 6000,
            },
            "demand_power": {
                "Rüdersdorf": {"hh": 21.8, "cts": 30.4, "ind": 259.5},
                "Strausberg": {"hh": 37.3, "cts": 42.8, "ind": 38.7},
                "Erkner": {"hh": 16.3, "cts": 10.3, "ind": 12.5},
                "Grünheide": {"hh": 12.3, "cts": 53.5, "ind": 1012.5},
            },
            "demand_heat_cen": {
                "Rüdersdorf": {"hh": 1.3, "cts": 0.4, "ind": 0.1},
                "Strausberg": {"hh": 19.5, "cts": 6.8, "ind": 1.4},
                "Erkner": {"hh": 0.1, "cts": 0, "ind": 0},
                "Grünheide": {"hh": 6.0, "cts": 1.1, "ind": 11.7},
            },
            "demand_heat_dec": {
                "Rüdersdorf": {"hh": 59.5, "cts": 18.9, "ind": 6.6},
                "Strausberg": {"hh": 58.3, "cts": 20.4, "ind": 4.3},
                "Erkner": {"hh": 37.4, "cts": 7.6, "ind": 4.0},
                "Grünheide": {"hh": 53.5, "cts": 10.0, "ind": 103.7},
            },
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
            # TODO: Insert data for Kiel
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

    basic_data = selected_region["basic_data"]
    capacity = selected_region["capacity"]
    capacity_potential = selected_region["capacity_potential"]
    full_load_hours = selected_region["full_load_hours"]
    production_data = {
        "Wind": [round(p["wind"] * full_load_hours["wind"] / 1e3, 1) for p in capacity.values()],
        "PV Freifläche": [round(p["pv_ground"] * full_load_hours["pv_ground"] / 1e3, 1) for p in capacity.values()],
        "PV Dach": [round(p["pv_roof"] * full_load_hours["pv_roof"] / 1e3, 1) for p in capacity.values()],
        "Bioenergie": [round(p["bio"] * full_load_hours["bio"] / 1e3, 1) for p in capacity.values()]
    }
    demand_power = selected_region["demand_power"]
    demand_heat_cen = selected_region["demand_heat_cen"]
    demand_heat_cen_sum = sum([sum(_.values()) for _ in demand_heat_cen.values()])
    demand_heat_dec = selected_region["demand_heat_dec"]
    demand_heat_dec_sum = sum([sum(_.values()) for _ in demand_heat_dec.values()])
    demand_heat_total = {
        mun: {k: round(v1 + v2, 1)
              for (k, v1), (_, v2) in
              zip(demand_heat_cen[mun].items(), demand_heat_dec[mun].items())
              } for mun in demand_heat_cen
    }

    x_axis_data = list(capacity.keys())

    charts_data = {
        "area": {
            "x_data": [""],
            "y_data": {k: [v["area"]] for k, v in basic_data.items()},
            "y_label": "km²",
        },
        "population": {
            "x_data": x_axis_data,
            "y_data": {k: [v["population"]] for k, v in basic_data.items()},
            "y_label": "",
        },
        "capacity": {
            "x_data": x_axis_data,
            "y_data": {
                "Wind": [p["wind"] for p in capacity.values()],
                "PV Freifläche": [p["pv_ground"] for p in capacity.values()],
                "PV Dach": [p["pv_roof"] for p in capacity.values()],
                "Bioenergie": [p["bio"] for p in capacity.values()],
            },
            "y_label": "MW",
            # "target": {"Regionalziel 2032": 100},
        },
        "capacity_potential": {
            "x_data": x_axis_data,
            "y_data": {
                "Wind": [p["wind"] for p in capacity_potential.values()],
                "PV Freifläche": [p["pv_ground"] for p in capacity_potential.values()],
                "PV Dach": [p["pv_roof"] for p in capacity_potential.values()],
            },
            "y_label": "MW",
        },
        "capacity_potential_usage": {
            "x_data": x_axis_data,
            "y_data": (
                pd.DataFrame(capacity).T[
                    ["wind", "pv_ground", "pv_roof"]
                ].T.div(
                    pd.DataFrame(capacity_potential)
                ).fillna(0).mul(100).replace(np.inf, 0).round(1).T.rename(
                    columns={"wind": "Wind", "pv_ground": "PV Freifläche", "pv_roof": "PV Dach"}
                ).to_dict("list")
            ),
            "y_label": "%",
        },
        "production": {
            "x_data": x_axis_data,
            "y_data": production_data,
            "y_label": "GWh",
        },
        "production_specific": {
            "x_data": x_axis_data,
            "y_data": {
                "pro Hektar": (pd.DataFrame(production_data).sum(axis=1) / pd.DataFrame(basic_data).T.reset_index()["area"] / 100 * 1e3).round(1).tolist(),
                "pro Kopf": (pd.DataFrame(production_data).sum(axis=1) / pd.DataFrame(basic_data).T.reset_index()["population"] * 1e3).round(1).tolist(),
            },
            "y_label": "MWh",
        },
        "demand_power": {
            "x_data": x_axis_data,
            "y_data": {
                "Haushalte": [p["hh"] for p in demand_power.values()],
                "GHD": [p["cts"] for p in demand_power.values()],
                "Industrie": [p["ind"] for p in demand_power.values()],
            },
            "y_label": "GWh",
        },
        "self_generation": {
            "x_data": x_axis_data,
            "y_data": {
                "Deckung": (
                    pd.DataFrame(production_data).sum(axis=1) /
                    pd.DataFrame(demand_power).T.sum(axis=1).reset_index(drop=True)
                ).mul(1e2).round(1).to_list(),
            },
            "y_label": "%",
        },
        "demand_heat": {
            "x_data": x_axis_data,
            "y_data": {
                "Haushalte": [p["hh"] for p in demand_heat_total.values()],
                "GHD": [p["cts"] for p in demand_heat_total.values()],
                "Industrie": [p["ind"] for p in demand_heat_total.values()],
            },
            "y_label": "GWh",
        },
        "demand_heat_type": {
            "x_data": [""],
            "y_data": {
                "Fernwärme": [round(demand_heat_cen_sum / (demand_heat_cen_sum + demand_heat_dec_sum) * 100, 1)],
                "Dezentral": [round(demand_heat_dec_sum / (demand_heat_cen_sum + demand_heat_dec_sum) * 100, 1)],
            },
        },
    }

    return charts_data


def municipalities_details(ids: list[int]) -> list[Municipality]:
    """Return municipalities."""
    municipalities = (
        Municipality.objects.filter(id__in=ids)
        .annotate(area_rounded=Round("area", precision=1))
        .annotate(biomass_net=Round(Sum("biomass__capacity_net", default=0) / 1000, precision=1))
        .annotate(pvground_net=Round(Sum("pvground__capacity_net", default=0) / 1000, precision=1))
        .annotate(pvroof_net=Round(Sum("pvroof__capacity_net", default=0) / 1000, precision=1))
        .annotate(wind_net=Round(Sum("windturbine__capacity_net", default=0) / 1000, precision=1))
        .annotate(hydro_net=Round(Sum("hydro__capacity_net", default=0) / 1000, precision=1))
        .annotate(
            total_net=Round(
                (
                    Sum("windturbine__capacity_net", default=0)
                    + Sum("hydro__capacity_net", default=0)
                    + Sum("pvroof__capacity_net", default=0)
                    + Sum("pvground__capacity_net", default=0)
                    + Sum("biomass__capacity_net", default=0)
                )
                / 1000,
                precision=1,
            ),
        )
        .annotate(storage_net=Round(Sum("storage__capacity_net", default=0) / 1000, precision=1))
        .annotate(kwk_el_net=Round(Sum("combustion__capacity_net", default=0) / 1000, precision=1))
        .annotate(kwk_th_net=Round(Sum("combustion__th_capacity", default=0) / 1000, precision=1))
    )
    return municipalities


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
