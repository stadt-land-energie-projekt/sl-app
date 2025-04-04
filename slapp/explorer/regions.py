"""Charts and Data for Regions."""
from __future__ import annotations

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
                    "title": "Besonderheit",
                    "fact": "Tesla-Gigafactory als wirtschaftlicher Impulsgeber",
                    "icon": "/static/images/icons/case-study-particularity.svg",
                },
                {
                    "title": "Erneuerbare Energien",
                    "fact": "Hoher Anteil an Wind- und Solarenergie",
                    "icon": "/static/images/icons/case-study-renewable.svg",
                },
                {
                    "title": "Herausforderung",
                    "fact": "Energieinfrastruktur für wachsende Industrie und Bevölkerung",
                    "icon": "/static/images/icons/case-study-challenge.svg",
                },
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
            "plans": {
                "2023": {"wind": 60, "pv": 80, "moor": 0},
                "2030": {"wind": 100, "pv": 120, "moor": 1},
                "2040": {"wind": 150, "pv": 140, "moor": 2},
            },
            "area": "3.5%",
            "co2": 1829.81,
        },
    ]


def get_basic_charts_data(region: str) -> dict:
    """Return basic chart data."""
    if region == "verbu":
        chart_data = {
            "electricity": {
                "categories": ["Jan", "Feb", "Mar"],
                "series": {
                    "Generation": [120, 200, 150],
                    "Consumption": [90, 50, 110],
                },
            },
            "heat": {
                "categories": ["Jan", "Feb", "Mar"],
                "series": {
                    "Generation": [80, 60, 90],
                    "Consumption": [40, 30, 55],
                },
            },
            "capacity": {
                "categories": ["Wind", "Solar", "Biomass"],
                "series": {
                    "Existing": [300, 200, 100],
                    "Addition": [30, 20, 10],
                },
            },
            "costs": {
                "categories": ["Project A", "Project B", "Project C"],
                "series": {
                    "Variable costs": [50000, 30000, 45000],
                    "Investment": [200000, 150000, 250000],
                },
            },
        }
    elif region == "einzeln":
        chart_data = {
            "electricity": {
                "categories": ["Jan", "Feb", "Mar"],
                "series": {
                    "Generation": [100, 190, 150],
                    "Consumption": [80, 40, 110],
                },
            },
            "heat": {
                "categories": ["Jan", "Feb", "Mar"],
                "series": {
                    "Generation": [100, 80, 90],
                    "Consumption": [60, 45, 55],
                },
            },
            "capacity": {
                "categories": ["Wind", "Solar", "Biomass"],
                "series": {
                    "Existing": [200, 150, 100],
                    "Addition": [20, 10, 5],
                },
            },
            "costs": {
                "categories": ["Project A", "Project B", "Project C"],
                "series": {
                    "Variable costs": [40000, 30000, 45000],
                    "Investment": [180000, 150000, 250000],
                },
            },
        }
    elif region == "kiel":
        chart_data = {
            "electricity": {
                "categories": ["Jan", "Feb", "Mar"],
                "series": {
                    "Generation": [200, 290, 150],
                    "Consumption": [100, 60, 110],
                },
            },
            "heat": {
                "categories": ["Jan", "Feb", "Mar"],
                "series": {
                    "Generation": [100, 120, 40],
                    "Consumption": [80, 55, 50],
                },
            },
            "capacity": {
                "categories": ["Wind", "Solar", "Biomass"],
                "series": {
                    "Existing": [400, 300, 100],
                    "Addition": [40, 20, 5],
                },
            },
            "costs": {
                "categories": ["Project A", "Project B", "Project C"],
                "series": {
                    "Variable costs": [80000, 30000, 48000],
                    "Investment": [190000, 160000, 270000],
                },
            },
        }
    else:
        chart_data = {}

    return chart_data


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

    plans = selected_region["plans"]
    x_axis_data = list(plans.keys())

    charts_data = {
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


def random_pastel_color() -> str:
    """Generate a random pastel color."""
    r = secrets.randbelow(106) + 150
    g = secrets.randbelow(106) + 150
    b = secrets.randbelow(106) + 150
    return f"#{r:02x}{g:02x}{b:02x}"


def parse_range(value_str: str) -> tuple[float, float]:
    """Parse a string such as '20-80 [MW]' and returns (min_value, max_value)."""
    if value_str.strip() == "-":
        return (0, 0)

    tuple_count = 2
    # Find all numbers in the string
    numbers = re.findall(r"\d+(?:\.\d+)?", value_str)
    if len(numbers) == tuple_count:
        # e.g. '20' and '80'
        return (float(numbers[0]), float(numbers[1]))
    if len(numbers) == tuple_count - 1:
        # e.g. '300'
        n = float(numbers[0])
        return (n, n)

    return (0, 0)


def get_dataframes() -> tuple[pd.DataFrame, pd.DataFrame, float]:
    """Return dataframe for table."""
    data_1 = {
        "pv_roof": {"per_cap": "20-80 [MW]", "pot": "300 [MW]", "cost": "20-80 [mio €]"},
        "bio": {"per_cap": "30-40 [MW]", "pot": "60 [MW]", "cost": "30-40 [mio €]"},
        "bat": {"per_cap": "50-55 [MW/h]", "pot": "-", "cost": "100-110 [mio €]"},
    }
    data_2 = {
        "pv_roof": {"per_cap": "10-100 [MW]", "pot": "300 [MW]", "cost": "10-100 [mio €]"},
        "bio": {"per_cap": "20-60 [MW]", "pot": "60 [MW]", "cost": "20-60 [mio €]"},
        "bat": {"per_cap": "40-60 [MW/h]", "pot": "-", "cost": "80-120 [mio €]"},
    }

    # Create DataFrames (index = technology name)
    df1 = pd.DataFrame.from_dict(data_1, orient="index")
    df2 = pd.DataFrame.from_dict(data_2, orient="index")

    # Optional: force a specific column order
    df1 = df1[["per_cap", "pot", "cost"]]
    df2 = df2[["per_cap", "pot", "cost"]]

    # Determine the global max difference for both tables combined
    all_ranges = []
    for row in df1.itertuples():
        vmin, vmax = parse_range(row.per_cap)
        all_ranges.append(vmax - vmin)
    for row in df2.itertuples():
        vmin, vmax = parse_range(row.per_cap)
        all_ranges.append(vmax - vmin)

    max_diff = max(all_ranges) if all_ranges else 0
    scale = max_diff + 10  # "about 10 more than the largest difference"
    return df1, df2, scale


def build_table_data(dataframe: pd.DataFrame, scale: float) -> list[dict]:
    """Convert the given DataFrame into a list of dictionaries for templating."""
    # Fixed colors for first three rows
    fixed_colors = ["#cdf4d3", "#ffe0c2", "#ffcdc2"]

    # Reset index so we have a column "index"
    dataframe = dataframe.reset_index()
    dataframe = dataframe.rename(columns={"index": "Technologie"})

    rows = []
    for idx, row in dataframe.iterrows():
        color = fixed_colors[idx] if idx < len(fixed_colors) else random_pastel_color()

        vmin, vmax = parse_range(row["per_cap"])
        diff = vmax - vmin

        if scale > 0:
            offset_pct = (vmin / scale) * 100
            width_pct = (diff / scale) * 100

        else:
            offset_pct = 0
            width_pct = 0

        offset_str = f"{offset_pct:.1f}"
        width_str = f"{width_pct:.1f}"
        rows.append(
            {
                "technologie": row["Technologie"],
                "per_cap": row["per_cap"],
                "pot": row["pot"],
                "cost": row["cost"],
                "offset_pct": offset_str,
                "width_pct": width_str,
                "color": color,
            },
        )
    return rows
