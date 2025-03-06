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
            "img_source": "Oderland-Spree-Map.png",
            "text": "Sie ist eine dynamische Region im Osten Brandenburgs, in der ländliche und städtische Strukturen aufeinandertreffen. Die Nähe zu Berlin, die Ansiedlung großer Industrieprojekte und der hohe Anteil erneuerbarer Energien machen sie zu einem spannenden Beispiel für die Energiewende im Stadt-Land-Nexus.",
            "keyfacts": [
                {"title": "Struktur", "fact": "Mischung aus ländlichen Gebieten und kleineren Städten"},
                {"title": "Besonderheit", "fact": "Tesla-Gigafactory als wirtschaftlicher Impulsgeber"},
                {"title": "Erneuerbare Energien", "fact": "Hoher Anteil an Wind- und Solarenergie"},
                {"title": "Herausforderung", "fact": "Energieinfrastruktur für wachsende Industrie und Bevölkerung"},
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
            "img_source": "Kiel-Map.png",
            "text": "Die Stadt ist ein bedeutender Standort für die Schiffbauindustrie, Offshore-Windenergie und innovative Forschung. Die starke Verbindung zur Ostsee prägt das wirtschaftliche und kulturelle Leben Kiels und macht die Region zu einem wichtigen Akteur der nachhaltigen maritimen Entwicklung.",
            "keyfacts": [
                {"title": "Struktur", "fact": "Mischung aus Hafenwirtschaft, Wissenschaft und urbanem Leben"},
                {"title": "Besonderheit", "fact": "Hafen als Knotenpunkt für Schifffahrt und internationale Logistik"},
                {"title": "Erneuerbare Energien", "fact": "Offshore-Windenergie und nachhaltige Mobilitätsprojekte"},
                {"title": "Herausforderung", "fact": "Transformation der Werftindustrie und Anpassung an den Klimawandel"},
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
