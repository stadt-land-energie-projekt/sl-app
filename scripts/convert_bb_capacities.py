"""Script to transform old sensitivity format into new format."""

import json
import pathlib
import shutil

import pandas as pd

SOURCE_FOLDER = pathlib.Path(__file__).parent.parent / "slapp" / "data" / "zib" / "bb" / "capacities"
TARGET_FOLDER = pathlib.Path(__file__).parent.parent / "slapp" / "data" / "zib" / "cost_bb"


TARGET_FOLDER.mkdir(exist_ok=True)


for folder in SOURCE_FOLDER.iterdir():
    if folder.is_dir():
        # Copy and transform scenario.json
        scenario_file = folder / "scenario.json"
        if not scenario_file.exists():
            continue
        with scenario_file.open("r", encoding="utf-8") as f:
            scenario_data = json.load(f)
        scenario_data["CostPerturbations"]["Perturbation1"] = scenario_data["CostPerturbations"]["CapacityCosts"]
        del scenario_data["CostPerturbations"]["CapacityCosts"]
        scenario_data["CostPerturbations"]["Perturbation1"][0]["FileName"] = scenario_data["CostPerturbations"][
            "Perturbation1"
        ][0]["VariableName"]
        del scenario_data["CostPerturbations"]["Perturbation1"][0]["VariableName"]
        scenario_data["CostPerturbations"]["Perturbation1"][0]["Column"] = "capacity_cost"
        (TARGET_FOLDER / folder.name).mkdir(exist_ok=True)
        with (TARGET_FOLDER / folder.name / "scenario.json").open("w", encoding="utf-8") as f:
            json.dump(scenario_data, f, indent=4)

        # Copy scalars.csv
        (TARGET_FOLDER / folder.name / "2045_scenario" / "postprocessed").mkdir(exist_ok=True, parents=True)
        source = folder / "scalars.csv"
        target = TARGET_FOLDER / folder.name / "2045_scenario" / "postprocessed" / "scalars.csv"
        shutil.copy(source, target)

        # Extract objective and create objective.csv
        scalars = pd.read_csv(source, delimiter=";", encoding="utf-8")
        objective_cost = scalars[scalars["var_name"] == "total_system_cost"].var_value.iloc[0]
        objective_df = pd.DataFrame({"": ["objective"], "0": [objective_cost]})
        objective_df.to_csv(
            TARGET_FOLDER / folder.name / "2045_scenario" / "postprocessed" / "objective.csv",
            sep=";",
            index=False,
        )
