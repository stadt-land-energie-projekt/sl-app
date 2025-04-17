"""Technologies for sensitivity data and Ranges for alternatives."""
import json
import pathlib

CONFIG_DIR = pathlib.Path(__file__).parent.parent / "config"

with (CONFIG_DIR / "technologies.json").open("r", encoding="utf-8") as f:
    TECHNOLOGIES = json.load(f)


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
