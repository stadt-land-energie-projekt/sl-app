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
        "potential": "60 [MW]",
    },
    "h2-bpchp": {
        "potential": "150 [MW]",
    },
    "cavern": {
        "potential": "300 [MWh]",
    },
    "electrolyzer": {
        "potential": "100 [MW]",
    },
    "extchp": {
        "potential": "80 [MW]",
    },
    "h2-gt": {
        "potential": "120 [MW]",
    },
    "heatpump_large": {
        "potential": "50 [MW]",
    },
    "heatpump_small": {
        "potential": "15 [MW]",
    },
    "liion_battery": {
        "potential": "200 [MWh]",
    },
    "onshore": {
        "potential": "400 [MW]",
    },
    "pth": {
        "potential": "60 [MW]",
    },
    "pv": {
        "potential": "300 [MW]",
    },
    "ror": {
        "potential": "50 [MW]",
    },
}
