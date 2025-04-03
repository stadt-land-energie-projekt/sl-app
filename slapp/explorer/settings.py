"""Technologies for sensitivity data and Ranges for alternatives."""
TECHNOLOGIES = {
    "boiler_large": {
        "name": "Großer Erdgas-Kessel",
        "color": "#FF8C00",
    },
    "h2-bpchp": {
        "name": "Biomasse-BHKW",
        "color": "#489F46",
    },
    "cavern": {
        "name": "Speicherkaverne",
        "color": "#587B8E",
    },
    "electrolyzer": {
        "name": "Wasserstoff-Elektrolyseur",
        "color": "#1E90FF",
    },
    "extchp": {
        "name": "Externes BHKW",
        "color": "#E57C3A",
    },
    "h2-gt": {
        "name": "Gasturbine",
        "color": "#7A8288",
    },
    "heatpump_large": {
        "name": "große Wärmepumpe",
        "color": "#3DAFAA",
    },
    "heatpump_small": {
        "name": "kleine Wärmepumpe",
        "color": "#71D5D0",
    },
    "liion_battery": {
        "name": "Lithium-Ionen-Akku",
        "color": "#4B8FE3",
    },
    "onshore": {
        "name": "Onshore-Windkraft",
        "color": "#8CC542",
    },
    "pth": {
        "name": "Strom-Wärme-Kopplung",
        "color": "#B25AA2",
    },
    "pv": {
        "name": "Photovoltaik",
        "color": "#FFD700",
    },
    "ror": {
        "name": "Laufwasserkraftwerk",
        "color": "#4682B4",
    },
}


TECHNOLOGIES_RANGES = {
    "boiler_large": {
        "potential": 60,
        "unit": "MW",
    },
    "h2-bpchp": {
        "potential": 150,
        "unit": "MW",
    },
    "cavern": {
        "potential": 300,
        "unit": "MWh",
    },
    "electrolyzer": {
        "potential": 100,
        "unit": "MW",
    },
    "extchp": {
        "potential": 80,
        "unit": "MW",
    },
    "h2-gt": {
        "potential": 120,
        "unit": "MW",
    },
    "heatpump_large": {
        "potential": 50,
        "unit": "MW",
    },
    "heatpump_small": {
        "potential": 15,
        "unit": "MW",
    },
    "liion_battery": {
        "potential": 200,
        "unit": "MWh",
    },
    "onshore": {
        "potential": 400,
        "unit": "MW",
    },
    "pth": {
        "potential": 60,
        "unit": "MW",
    },
    "pv": {
        "potential": 300,
        "unit": "MW",
    },
    "ror": {
        "potential": 50,
        "unit": "MW",
    },
}

TECHNOLOGIES_SELECTED = {
    "electrolyzer",
    "heatpump_small",
    "liion_battery",
    "onshore",
    "pv",
}
