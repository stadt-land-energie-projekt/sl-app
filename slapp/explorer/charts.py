import pandas as pd

from . import chart_data


def get_all_base_charts(scenario: str) -> dict:
    """Return data for all base charts."""
    return {
        "electricity_import": electricity_import(scenario)[1],
        "total_electricity_per_technology": total_electricity_per_technology(scenario)[1],
        "optimized_capacities": optimized_capacities(scenario)[1],
        "generation_consumption_per_sector": generation_consumption_per_sector(scenario)[1],
        "self_generation_imports": self_generation_imports(scenario)[1],
        "supplied_hours": supplied_hours(scenario)[1],
    }


def merge_technologies(technology):
    if "wind" in technology:
        return "wind"
    if "import" in technology:
        return "import"
    if "pv" in technology:
        return "electricity-pv"
    if "heatpump" in technology:
        return "electricity-heatpump"
    if "storage" in technology and "electricity" in technology:
        return "electricity-storage"
    if "storage" in technology and "heat" in technology:
        return "heat-storage"
    if "bpchp" in technology and "h2" not in technology:
        return "bpchp"
    if "boiler" in technology and "h2" not in technology:
        return "boiler"
    if "h2-bpchp" in technology:
        return "h2-bpchp"
    return technology


def total_electricity_per_technology(scenario: str):
    template = "total_electricity_per_technology.html"
    scalars = chart_data.get_postprocessed_data(scenario)
    filtered = scalars[(scalars["var_name"] == "flow_out_electricity") & (scalars["var_value"] > 0)][
        ["name", "var_value"]
    ]
    filtered.columns = ["name", "value"]
    filtered["name"] = filtered["name"].apply(lambda x: x.split("-", 1)[1])
    filtered = filtered.groupby("name").sum()
    filtered["value"] = (filtered["value"] / filtered["value"].sum() * 100).round(3)
    return template, filtered.reset_index().to_dict(orient="records")


def electricity_import(scenario: str):
    template = "electricity_import.html"
    scalars = chart_data.get_postprocessed_data(scenario)
    import_df = scalars[
        (scalars["var_name"] == "flow_out_electricity") & (scalars["tech"] == "import") & (scalars["var_value"] > 0)
    ][["name", "var_value"]]
    export_df = scalars[
        (scalars["var_name"] == "flow_in_electricity") & (scalars["tech"] == "export") & (scalars["var_value"] > 0)
    ][["name", "var_value"]]
    result = [import_df["var_value"].sum(), -export_df["var_value"].sum()]
    return template, result


def optimized_capacities(scenario: str):
    template = "optimized_capacities.html"

    file_list = chart_data.get_preprocessed_file_list()
    file_names_list = [file_name[:-4] for file_name in file_list]

    scalars_df = chart_data.get_postprocessed_data(scenario)

    var_value_df = scalars_df[
        (scalars_df["var_name"].str.contains("invest_out|invest_in"))
        & (scalars_df["name"].str.contains("|".join(file_names_list)))
    ]

    capacity_potential_df = chart_data.get_preprocessed_file_df()

    merged_df = pd.merge(var_value_df, capacity_potential_df, on="name", how="outer")
    merged_df = merged_df[["name", "var_value", "capacity_potential", "var_name"]]

    merged_df.loc[
        merged_df["capacity_potential"] == float("inf"),
        "capacity_potential",
    ] = 0
    merged_df.loc[
        merged_df["capacity_potential"] == float("-inf"),
        "capacity_potential",
    ] = 0

    merged_df = merged_df[
        (merged_df["var_value"].notna())
        & (merged_df["capacity_potential"].notna() & merged_df["capacity_potential"] > 0)
    ]
    merged_df["name"] = merged_df["name"].apply(merge_technologies)
    return template, merged_df.to_dict(orient="records")


def generation_consumption_per_sector(scenario: str):
    template = "generation_consumption_per_sector.html"
    scalars = chart_data.get_postprocessed_data(scenario)

    scalars["name"] = scalars["name"].apply(merge_technologies)

    y1 = (
        scalars.loc[
            (scalars["var_name"] == "flow_out_electricity") & (scalars["var_value"] > 0),
            ["name", "var_value"],
        ]
        .groupby("name")
        .sum()
    )
    x1 = (
        int(
            scalars.loc[(scalars["var_name"] == "flow_in_electricity"), "var_value"].sum().sum() / 1000,
        )
        * 1000
    )

    y2 = (
        scalars.loc[
            (scalars["var_name"] == "flow_out_heat_low_decentral") & (scalars["var_value"] > 0),
            ["name", "var_value"],
        ]
        .groupby("name")
        .sum()
    )
    x2 = (
        int(
            scalars.loc[
                (scalars["var_name"] == "flow_in_heat_low_decentral"),
                "var_value",
            ]
            .sum()
            .sum()
            / 1000,
        )
        * 1000
    )

    y3 = (
        scalars.loc[
            (scalars["var_name"] == "flow_out_heat_low_central") & (scalars["var_value"] > 0),
            ["name", "var_value"],
        ]
        .groupby("name")
        .sum()
    )
    x3 = (
        int(
            scalars.loc[
                (scalars["var_name"] == "flow_in_heat_low_central"),
                "var_value",
            ]
            .sum()
            .sum()
            / 1000,
        )
        * 1000
    )

    y4 = (
        scalars.loc[
            (scalars["var_name"] == "flow_out_heat_high") & (scalars["var_value"] > 0),
            ["name", "var_value"],
        ]
        .groupby("name")
        .sum()
    )
    x4 = (
        int(
            scalars.loc[(scalars["var_name"] == "flow_in_heat_high"), "var_value"].sum().sum() / 1000,
        )
        * 1000
    )

    data = {
        "chart1-1": (y1 / y1.sum() * 100).to_dict()["var_value"],
        "chart1-total": x1,
        "chart2-1": y2.to_dict()["var_value"],
        "chart2-total": x2,
        "chart3-1": y3.to_dict()["var_value"],
        "chart3-total": x3,
        "chart4-1": y4.to_dict()["var_value"],
        "chart4-total": x4,
    }
    return template, data


def self_generation_imports(scenario: str):
    template = "self_generation_power.html"
    scalars = chart_data.get_postprocessed_data(scenario)
    y1_df = scalars[(scalars["var_name"] == "flow_out_electricity") & (~scalars["type"].isin(["shortage", "storage"]))]
    y1 = y1_df["var_value"].sum()

    y2_df = scalars[(scalars["var_name"] == "flow_out_electricity") & (scalars["tech"] == "import")]
    y2 = y2_df["var_value"].sum()

    data = {
        "y1": y1,
        "y2": y2,
        "x": round(y1 + y2, 2),
    }
    return template, data


def supplied_hours(scenario: str):
    template = "supplied_hours.html"
    electricity = chart_data.get_electricity_sequences(scenario)
    from_to_columns = [column.split("|") for column in electricity.columns.tolist()]
    supplies = ["chp", "pv", "wind", "storage"]
    supply_columns = [
        "|".join([from_node, to_node])
        for from_node, to_node in from_to_columns
        if "electricity" in to_node and any(supply in from_node for supply in supplies)
    ]
    demand_columns = [
        "|".join([from_node, to_node])
        for from_node, to_node in from_to_columns
        if "electricity" in from_node and "demand" in to_node
    ]
    self_supplied_hours = sum(electricity[supply_columns].sum(axis=1) > electricity[demand_columns].sum(axis=1))

    y1 = self_supplied_hours
    y2 = 8760 - y1
    x = y1 + y2

    y1 = y1 / x * 100
    y2 = y2 / x * 100

    data = {"y1": {"a": round(y1, 2)}, "y2": {"b": round(y2, 2)}}
    return template, data


def interactive_time_series_plot(scenario: str):
    template = "interactive_time_series_plot.html"
    data_df = pd.DataFrame()
    flow_df = chart_data.get_postprocessed_by_variable_flow("flow.csv")
    storage_content_df = chart_data.get_postprocessed_by_variable_flow(
        "storage_content.csv",
    )

    data_df["flow zeit 1"] = flow_df[1]
    data_df["storage content zeit 1"] = storage_content_df[1]

    data_df["flow zeit N"] = flow_df[2]
    data_df["storage content zeit N"] = storage_content_df[3]
    return template, data_df.to_dict()
