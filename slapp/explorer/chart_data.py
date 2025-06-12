import os
import pathlib

import pandas as pd

DATA_DIR = pathlib.Path(__file__).parent.parent / "data" / "zib" / "base"
OEMOF_SCENARIO = "2045_scenario"
OEMOF_SCENARIOS_SINGLE = [
    "r120640428428",
    "r120640472472",
    "r120670124124",
    "r120670201201",
]

NODES = [
    {"name": "Straußberg", "x": 50, "y": -50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
    {"name": "Rüdersdorf", "x": 0, "y": 0, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
    {"name": "Grünheide", "x": 50, "y": 50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
    {"name": "Erkner", "x": -10, "y": 50, "itemStyle": {"color": "#798897"}, "symbolSize": 30},
    {"name": "Netz ", "x": 80, "y": -25, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
    {"name": "Netz   ", "x": 60, "y": 75, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
    {"name": "Netz", "x": -20, "y": -20, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
    {"name": "Netz  ", "x": -20, "y": 75, "itemStyle": {"color": "#000000"}, "symbolSize": 10},
]


def get_postprocessed_data(scenario: str = "all"):
    """
    Get postprocessed data for scenario.

    Scenario can be one of "all" or "single". In case of "single" scenario,
    postprocessed data from scenarios is merged together.
    """
    if scenario == "all":
        return pd.read_csv(
            DATA_DIR / OEMOF_SCENARIO / "postprocessed" / "scalars.csv",
            delimiter=";",
        )
    elif scenario == "single":
        scenario_data = []
        for scenario in OEMOF_SCENARIOS_SINGLE:
            scenario_data.append(
                pd.read_csv(DATA_DIR / scenario / OEMOF_SCENARIO / "postprocessed" / "scalars.csv", delimiter=";")
            )
        merged_df = pd.concat(scenario_data, axis=0)
        return merged_df
    else:
        return pd.read_csv(DATA_DIR / scenario / OEMOF_SCENARIO / "postprocessed" / "scalars.csv", delimiter=";")


def get_preprocessed_file_list():
    path = DATA_DIR / OEMOF_SCENARIO / "preprocessed" / "data" / "elements"
    file_list = [f for f in os.listdir(path) if f.endswith(".csv")]
    filtered_file_list = [
        f
        for f in file_list
        if not any(x in f for x in ["commodity", "demand", "bus", "export", "import", "transmission"])
    ]
    return filtered_file_list


def get_preprocessed_file_df():
    resultDf = pd.DataFrame()
    file_list = get_preprocessed_file_list()

    for file in file_list:
        file_path = DATA_DIR / OEMOF_SCENARIO / "preprocessed" / "data" / "elements" / file
        techDf = pd.read_csv(file_path, delimiter=";")
        resultDf = pd.concat([resultDf, techDf], ignore_index=True)

    return resultDf


def get_electricity_sequences(scenario: str = "all"):
    file_list = []
    if scenario == "all":
        path = DATA_DIR / OEMOF_SCENARIO / "postprocessed" / "sequences" / "bus"
        file_list += [path / f for f in os.listdir(path) if f.endswith(".csv") and "electricity" in f]
    elif scenario == "single":
        for scenario in OEMOF_SCENARIOS_SINGLE:
            path = DATA_DIR / scenario / OEMOF_SCENARIO / "postprocessed" / "sequences" / "bus"
            file_list += [path / f for f in os.listdir(path) if f.endswith(".csv") and "electricity" in f]
    else:
        path = DATA_DIR / scenario / OEMOF_SCENARIO / "postprocessed" / "sequences" / "bus"
        file_list += [path / f for f in os.listdir(path) if f.endswith(".csv") and "electricity" in f]

    data = []

    for file in file_list:
        df = pd.read_csv(file, index_col=0, header=None, sep=";")
        columns = df.iloc[:2].values
        df = df.iloc[3:]
        df.columns = list("|".join(item) for item in zip(columns[0], columns[1]))
        # This gives me strange output ? Look at timeindex around 8700 and you will see artifacts
        data.append(df)

    merged_df = pd.concat(data, axis=1)
    merged_df = merged_df.astype(float)
    return merged_df


def get_postprocessed_by_variable_flow(filename="flow.csv"):
    path = DATA_DIR / OEMOF_SCENARIO / "postprocessed" / "sequences" / "by_variable" / filename
    df = pd.read_csv(path, sep=";", skiprows=3, header=None, index_col=0)
    return df
