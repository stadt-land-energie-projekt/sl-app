"""Charts and Data for Regions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.gis.db.models.functions import Envelope
from django.db.models import Sum
from django.db.models.functions import Round
from django.http import HttpResponse, JsonResponse

if TYPE_CHECKING:
    from django.http.request import HttpRequest

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
            "img_source": "Oderland-Spree.png",
            "text": "Text und Key Facts für Oderland-Spree",
            "keyfacts": [
                "keyfact1",
                "keyfact2",
                "keyfact3",
                "keyfact4",
            ],
            "plans": {
                "2023": {"wind": 40, "pv": 80, "moor": 1},
                "2030": {"wind": 70, "pv": 100, "moor": 2},
                "2040": {"wind": 80, "pv": 120, "moor": 4},
            },
            "area": "5.5%",
            "co2": 1500.81,
        },
        {
            "title": "Region Kiel",
            "bbox": region_bbox["Kiel"],
            "info": "Hier steht mehr Info über die Region Kiel",
            "img_source": "Kiel.png",
            "text": "Text und Key Facts für Kiel",
            "keyfacts": [
                "keyfact1",
                "keyfact2",
                "keyfact3",
                "keyfact4",
            ],
            "plans": {
                "2023": {"wind": 60, "pv": 80, "moor": 0},
                "2030": {"wind": 100, "pv": 120, "moor": 1},
                "2040": {"wind": 150, "pv": 140, "moor": 2},
            },
            "area": "3.5%",
            "co2": 1829.81,
        },
    ]


def all_charts(request: HttpRequest) -> HttpResponse:
    """Build all charts."""
    if request.method != "GET":
        return HttpResponse(status=405)

    region_name = request.GET.get("region", "")

    regions = get_regions_data()

    selected_region = None
    for reg in regions:
        if reg["title"] == region_name:
            selected_region = reg
            break

    if not selected_region:
        selected_region = regions[0]

    plans = selected_region["plans"]
    x_axis_data = list(plans.keys())

    response_data = {
        "production": {
            "x_data": x_axis_data,
            "y_data": {
                "Production": [p["wind"] + p["pv"] for p in plans.values()],
                "Consumption": [p["wind"] * 1.5 for p in plans.values()],
            },
            "y_label": "kWh",
        },
        "tech": {
            "x_data": x_axis_data,
            "y_data": {
                "Wind": [p["wind"] for p in plans.values()],
                "PV": [p["pv"] for p in plans.values()],
            },
            "y_label": "MW",
            "target": {"Target 2040": 100},
        },
        "another": {
            "x_data": x_axis_data,
            "y_data": {
                "Moor": [p["moor"] for p in plans.values()],
            },
            "y_label": "Moor KPI [dummy]",
        },
        "demand": {
            "x_data": x_axis_data,
            "y_data": {
                "Households": [p["pv"] / 2 for p in plans.values()],
                "Industry": [p["wind"] / 2 for p in plans.values()],
            },
            "y_label": "Energy Demand [GWh]",
        },
        "area": {
            "x_data": ["dummy"],
            "y_data": {
                "Used Land": [45],
                "Unused Land": [55],
            },
        },
        "co2": {
            "icon_url": "/static/images/co2_icon.png",
            "co2_text": f"Region: {selected_region['title']} - CO₂ Emissions: {selected_region['co2']} tons",
        },
    }

    return JsonResponse(response_data)


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
    elif region == "Kiel":
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
        ]
    return energy_data


def flow_chart(request: HttpRequest) -> JsonResponse:
    """Return requested data."""
    chart_type = request.GET.get("type", "verbu")

    if chart_type == "verbu":
        flow_data = get_energy_data("verbu")
    elif chart_type == "einzeln":
        flow_data = get_energy_data("einzeln")
    elif chart_type == "kiel":
        flow_data = get_energy_data("Kiel")
    else:
        flow_data = {
            "title": "Unbekannter Typ",
            "energyData": [],
            "nodes": [],
        }

    response_data = {"data": flow_data}

    return JsonResponse(response_data)


def cost_capacity_chart(request: HttpRequest) -> JsonResponse:
    """Return chosen data for cost capacity chart."""
    data_type = request.GET.get("type", "")

    if data_type == "Technologie":
        cost_capacity_data = {
            "line_data": [
                [0, 0],
                [50, 20],
                [100, 50],
                [150, 80],
                [200, 120],
            ],
            "bar_data": [
                {"name": "Kategorie A", "value": 100},
                {"name": "Kategorie B", "value": 60},
                {"name": "Kategorie C", "value": 130},
                {"name": "Kategorie D", "value": 90},
            ],
        }
    elif data_type == "Etwas anderes":
        cost_capacity_data = {
            "line_data": [
                [0, 0],
                [50, 10],
                [100, 30],
                [150, 70],
                [200, 130],
            ],
            "bar_data": [
                {"name": "Andere A", "value": 75},
                {"name": "Andere B", "value": 50},
                {"name": "Andere C", "value": 110},
            ],
        }
    elif data_type == "Sonstiges":
        cost_capacity_data = {
            "line_data": [
                [0, 0],
                [50, 40],
                [100, 200],
                [150, 300],
                [200, 350],
            ],
            "bar_data": [
                {"name": "Sonstige 1", "value": 20},
                {"name": "Sonstige 2", "value": 40},
                {"name": "Sonstige 3", "value": 60},
                {"name": "Sonstige 4", "value": 100},
            ],
        }
    else:
        cost_capacity_data = {
            "line_data": [],
            "bar_data": [],
        }

    return JsonResponse(cost_capacity_data)
