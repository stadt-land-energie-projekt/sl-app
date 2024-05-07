import os
import pathlib
import shutil
from ast import literal_eval

import pandas as pd
import tsam.timeseriesaggregation as tsam
from frictionless import Package

SCENARIO_FOLDER = pathlib.Path(__file__).parent.parent / "data" / "oemof"
SCENARIO_ORIGINAL = "scenario_2045"
SCENARIO_TARGET = "scenario_2045_tsam"

sequences_original_path = SCENARIO_FOLDER / SCENARIO_ORIGINAL / "data" / "sequences"
datapackage_path = SCENARIO_FOLDER / SCENARIO_ORIGINAL

periods_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "periods"
sequences_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "sequences"
tsam_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "tsam"


def crawl_oemof_tabular_datapackage(path=datapackage_path):
    """
    The function crawls the sequences csv-files of an oemof.tabular
    data and merges them into one single DataFrame

    Parameters
    ----------
    path (pathlib.Path object)
        path-object to datapackage.json

    Returns
    -------
    df (pd.DataFrame):
        DataFrame that contains all sequence data specified in the
        oemof-tabular datapackage

    """
    df = pd.DataFrame()
    package = Package(path)
    for resource in package.resources:
        if "profile" in resource.name:
            resource.read()
            df_sequence = pd.read_csv(
                resource.raw_iter(),
                delimiter=";",
                encoding="utf-8",
                index_col="timeindex",
                parse_dates=True,
            )
            df = pd.concat([df, df_sequence], axis=1)

    return df


def crawl_sequences_data(path=sequences_original_path):
    """
    The function crawls the sequences csv-files of oemof.tabular
    data/sequences path and merges them into one single DataFrame

    Parameters
    ----------
    path (pathlib.Path object)
        path-object to oemof squence data "data/sequences"

    Returns
    -------
    df (pd.DataFrame):
        DataFrame that contains all sequence data specified in the
        oemof-tabular datapackage

    """
    df = pd.DataFrame()

    for f in path.iterdir():
        if f.is_file() and f.suffix in ".csv":
            file = pd.read_csv(f, parse_dates=True, encoding="utf8", sep=";", index_col="timeindex")
            df = pd.concat([df, file], axis=1)
    return df


def run_tsam(df, typical_periods=40, hours_per_period=24):
    """
    The function takes the merged oemof-sequences DataFrame,
    runs the tsam TimeSeriesAggregation and returns aggregated data and
    tsa_parameters for a single oemof period. The default Clustermethod is set
    to 'k_means' but can be changed accordingly. See the tsam-Documentation for
    further detail.

    Parameters
    ----------
    df (pd.DataFrame):
        DataFrame that contains all sequence data specified in the
        oemof-tabular datapackage

    typical_periods (int; Default: 40)
        Number of typcial periods used for the aggregation.

    hours_per_period (int; Default: 24)
        Number of hours per period used for aggregation.

    Returns
    -------
    aggregation (tsam.TimeSeriesAggregation object)
        The tsam.TimeSeriesAggregation object contains all relevant parameters
        and values as a result of executing the time series aggregation

    """
    aggregation = tsam.TimeSeriesAggregation(
        df,
        noTypicalPeriods=typical_periods,
        hoursPerPeriod=hours_per_period,
        sortValues=False,
        clusterMethod="k_means",
        rescaleClusterPeriods=False,
        extremePeriodMethod="replace_cluster_center",
        representationMethod="durationRepresentation",
    )

    return aggregation


def prepare_oemof_parameters(aggregation, directory="tsam_parameters"):
    """
    Function takes aggregation object and derives tsa_parameters, tsa_periods,
    tsa_timeindex and saves return values as .csv files in results_path

    Parameters
    ----------
    aggregation (tsam.TimeSeriesAggregation object)

    Returns
    -------
    tsa_periods (pd.DataFrame):
        contains typical periods and data of all oemof.tabular sequences df
    tsa_parameters (pd.DataFrame dict-like):
        contains meta information to solph oemof model using tsam
    tsa_timeindex (dict):
        contains the timeindex of aggregated df and is used as index for
        seqeuences data

    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    tsa_periods = aggregation.createTypicalPeriods()
    tsa_periods.to_csv(
        pathlib.Path(directory, "tsa_periods.csv"),
        encoding="utf-8",
        sep=";",
        index_label=["typ_period", "hpperiod"],
    )

    tsa_parameters = {
        "period": 1,
        "timesteps_per_period": aggregation.hoursPerPeriod,
        "order": [aggregation.clusterOrder.tolist()],
    }

    tsa_parameters = pd.DataFrame(tsa_parameters)
    tsa_parameters.to_csv(pathlib.Path(directory, "tsa_parameters.csv"), index=False, encoding="utf-8", sep=";")

    tsa_date_range = pd.date_range(
        aggregation.timeIndex[0],
        periods=aggregation.noTypicalPeriods * aggregation.hoursPerPeriod,
        freq="h",
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    tsa_timeindex = pd.DataFrame(index=tsa_date_range)
    tsa_timeindex.to_csv(
        pathlib.Path(directory, "tsa_timeindex.csv"),
        index_label="timeindex",
        encoding="utf-8",
        sep=";",
    )

    return tsa_periods, tsa_parameters, tsa_timeindex


def convert_tsa_periods_to_sequences(tsa_parameters_dir="tsam_parameters", path=sequences_path):
    try:
        os.path.exists(tsa_parameters_dir)
    except NameError:
        print("Directory does not exist:", tsa_parameters_dir)

    if not os.path.exists(path):
        os.makedirs(path)

    timeindex = pd.read_csv(
        pathlib.Path(tsa_parameters_dir, "tsa_timeindex.csv"),
        encoding="utf8",
        sep=";",
        parse_dates=True,
    )

    df = pd.read_csv(pathlib.Path(tsa_parameters_dir, "tsa_periods.csv"), encoding="utf8", sep=";")
    df["timeindex"] = timeindex
    df.set_index("timeindex", inplace=True)
    df.drop(["typ_period", "hpperiod"], inplace=True, axis=1)

    for series_name, series in df.items():
        # delete the characters "ABW-" from csv-name
        file_name = series_name[4:]
        csv_name = file_name.removesuffix("-profile") + "_profile.csv"
        series.to_csv(pathlib.Path(path, csv_name), index_label=["timeindex"], encoding="utf-8", sep=";")
    return df


def reconvert_tsa_periods_to_full_periods(
    tsa_parameters_dir="tsam_parameters",
    timeindex=pd.date_range(start="2019-01-01 00:00:00", end="2019-12-31 23:00:00", freq="h"),
    path=sequences_path,
):
    try:
        os.path.exists(tsa_parameters_dir)
    except NameError:
        print("Directory does not exist:", tsa_parameters_dir)

    if not os.path.exists(path):
        os.makedirs(path)

    tsa_periods = pd.read_csv(pathlib.Path(tsa_parameters_dir, "tsa_periods.csv"), encoding="utf8", sep=";")
    tsa_parameters = pd.read_csv(
        pathlib.Path(tsa_parameters_dir, "tsa_parameters.csv"),
        encoding="utf8",
        sep=";",
        usecols=["order"],
        converters={"order": literal_eval},
    )
    tsa_cluster_order = tsa_parameters.iloc[0, 0]

    df = pd.DataFrame()

    for item in tsa_cluster_order:
        periods_new = tsa_periods[item * 24 : (item + 1) * 24]
        df = pd.concat([df, periods_new])

    df["timeindex"] = timeindex
    df.set_index("timeindex", inplace=True)
    df.drop(["typ_period", "hpperiod"], inplace=True, axis=1)

    for series_name, series in df.items():
        # delete the characters "ABW-" from csv-name
        file_name = series_name[4:]
        csv_name = file_name.removesuffix("-profile") + "_profile.csv"
        series.to_csv(pathlib.Path(path, csv_name), index_label=["timeindex"], encoding="utf-8", sep=";")

    return df


def create_oemof_periods_csv(
    tsa_parameters_dir="tsam_parameters",
    no_of_periods=1,
    timeincrement=1,
    path=periods_path,
):
    try:
        os.path.exists(tsa_parameters_dir)
    except NameError:
        print("Directory does not exist:", tsa_parameters_dir)

    if not os.path.exists(path):
        os.makedirs(path)

    df = pd.read_csv(pathlib.Path(tsa_parameters_dir, "tsa_timeindex.csv"), sep=";", encoding="utf-8")

    df["periods"] = no_of_periods - 1
    df["timeincrement"] = timeincrement

    df.to_csv(pathlib.Path(path, "periods.csv"), index=False, encoding="utf-8", sep=";")
    return df


def copy_tsa_parameter(tsa_parameters_dir="tsam_parameters", path=tsam_path):
    if not os.path.exists(path):
        os.makedirs(path)

    try:
        os.path.exists(tsa_parameters_dir)
    except NameError:
        print("Directory does not exist:", tsa_parameters_dir)

    df = pd.read_csv(pathlib.Path(tsa_parameters_dir, "tsa_parameters.csv"), sep=";", encoding="utf-8")

    df.to_csv(pathlib.Path(path, "tsa_parameters.csv"), index=False, encoding="utf-8", sep=";")

    return df


def copy_elements_data(origin=SCENARIO_ORIGINAL, goal=SCENARIO_TARGET):
    try:
        shutil.copytree(pathlib.Path(origin, "data", "elements"), pathlib.Path(goal, "data", "elements"))
    except Exception as e:
        print("Fehler beim Kopieren des Ordners", e)


if __name__ == "__main__":
    sequences = crawl_sequences_data()
    # sequences.drop("ABW-efficiency-profile", axis=1).plot()
    # matplotlib.pyplot.show()
    # sequences.to_csv(scenario_name_origin+"_sequences.csv", encoding="utf-8",
    #          #sep=";")
    df_sum = sequences.sum()
    aggregation = run_tsam(sequences, typical_periods=40)
    oemof_tsa_parameters = prepare_oemof_parameters(aggregation)
    convert_tsa_periods_to_sequences()
    create_oemof_periods_csv()
    copy_tsa_parameter()
    copy_elements_data()
    # copy_data_datapackage_to_scenario_goal()
    # reconvert_tsa_periods_to_full_periods()
    # tsa_periods=pd.read_csv(pathlib.Path(tsam_path,'tsa_parameters.csv'), encoding="utf-8", sep=";")
    # tsa_periods["order"][0]=list(range(0,365))
    # tsa_periods.to_csv(pathlib.Path(tsam_path, 'tsa_parameters.csv'),
    # encoding="utf-8", sep=";", index=False)
    print("done")
