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

sequences_original_path = \
    SCENARIO_FOLDER / SCENARIO_ORIGINAL / "data" / "sequences"
datapackage_path = \
    SCENARIO_FOLDER / SCENARIO_ORIGINAL
elements_original_path = \
    SCENARIO_FOLDER / SCENARIO_ORIGINAL / "data" / "elements"

periods_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "periods"
sequences_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "sequences"
tsam_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "tsam"
elements_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "elements"


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

    # Dictionary to keep track of columns from each file
    file_columns = {}

    # List to store dataframes
    dfs = []

    package = Package(path)

    for resource in package.resources:
        if "profile" in resource.name:
            resource.read()
            file_name = resource.raw_iter()
            df = pd.read_csv(
                file_name,
                delimiter=";",
                encoding="utf-8",
                index_col="timeindex",
                parse_dates=True,
            )
            file_columns[
                file_name] = df.columns.tolist()
            dfs.append(df)

    df = pd.concat(dfs, axis=1)

    return df, file_columns


def crawl_sequences_data(path=sequences_original_path):
    """ The function crawls the sequences csv-files of oemof.tabular
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
    # Dictionary to keep track of columns from each file
    file_columns = {}

    # List to store dataframes
    dfs = []

    for file_name in path.iterdir():
        if file_name.is_file() and file_name.suffix in ".csv":
            df = pd.read_csv(file_name, encoding='utf8',
                             sep=';', parse_dates=True, index_col='timeindex')
            file_columns[file_name.name] = df.columns.tolist()
            dfs.append(df)

    df = pd.concat(dfs, axis=1)

    return df, file_columns


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
    tsa_aggregation = tsam.TimeSeriesAggregation(
        df,
        noTypicalPeriods=typical_periods,
        hoursPerPeriod=hours_per_period,
        sortValues=False,
        clusterMethod="k_means",
        rescaleClusterPeriods=False,
        extremePeriodMethod="replace_cluster_center",
        representationMethod="durationRepresentation",
    )

    return tsa_aggregation


def prepare_oemof_parameters(tsa_aggregation, directory="tsam_parameters"):
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

    tsa_periods = tsa_aggregation.createTypicalPeriods()

    tsa_parameters = {
        "period": 1,
        "timesteps_per_period": tsa_aggregation.hoursPerPeriod,
        "order": [tsa_aggregation.clusterOrder.tolist()],
    }

    tsa_parameters = pd.DataFrame(tsa_parameters)

    tsa_date_range = pd.date_range(
        tsa_aggregation.timeIndex[0],
        periods=tsa_aggregation.noTypicalPeriods
        * tsa_aggregation.hoursPerPeriod,
        freq="h"
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    return tsa_periods, tsa_parameters, tsa_date_range


def convert_tsa_periods_to_sequences(tsa_periods, tsa_date_range,
                                     file_columns,
                                     path=sequences_path):
    if not os.path.exists(path):
        os.makedirs(path)

    df = tsa_periods
    df["timeindex"] = tsa_date_range
    df.set_index("timeindex", inplace=True)

    for file_name, columns in file_columns.items():
        # Subset the DataFrame based on original columns
        df_subset = df[columns]
        # Write to CSV
        df_subset.to_csv(pathlib.Path(path, file_name), encoding="utf-8",
                         sep=";", index=True, index_label="timeindex")

    return df


def resample_tsa_sequences_to_original_sequences(
    origin=sequences_original_path,
    goal=sequences_path,
    tsa_parameters_dir=tsam_path,
    path=sequences_path / "sequences_resampled",
):
    try:
        os.path.exists(tsa_parameters_dir)
    except NameError:
        print("Directory does not exist:", tsa_parameters_dir)

    if not os.path.exists(path):
        os.makedirs(path)

    tsa_parameters = pd.read_csv(
        pathlib.Path(tsa_parameters_dir, "tsa_parameters.csv"),
        encoding="utf8",
        sep=";",
        usecols=["order"],
        converters={"order": literal_eval},
    )

    tsa_cluster_order = tsa_parameters.iloc[0, 0]

    df = pd.DataFrame()

    for file_name in goal.iterdir():
        if file_name.is_file() and file_name.suffix in ".csv":
            dfs = []

            df = pd.read_csv(file_name, encoding='utf-8',
                             sep=';', parse_dates=True,
                             index_col='timeindex')

            timeindex_original = pd.read_csv(
                pathlib.Path(origin, file_name.name),
                encoding="utf8",
                sep=";",
                usecols=[0],
                index_col=[0])

            for item in tsa_cluster_order:
                df_subset = df[item * 24: (item + 1) * 24]
                dfs.append(df_subset)

            df = pd.concat(dfs, axis=0)
            df["timeindex"] = timeindex_original.index
            df.set_index("timeindex", inplace=True)

            df.to_csv(pathlib.Path(path, file_name.name), encoding="utf-8",
                      sep=";", index=True)
    return df


def create_oemof_periods_csv(
    tsa_periods,
    no_of_periods=1,
    timeincrement=1,
    path=periods_path,
):
    if not os.path.exists(path):
        os.makedirs(path)

    df = tsa_periods

    df["periods"] = no_of_periods - 1
    df["timeincrement"] = timeincrement

    df.to_csv(pathlib.Path(path, "periods.csv"), index=False,
              encoding="utf-8", sep=";")
    return df


def copy_tsa_parameter(tsa_parameters, path=tsam_path):
    if not os.path.exists(path):
        os.makedirs(path)

    df = tsa_parameters
    df.to_csv(pathlib.Path(path, "tsa_parameters.csv"), index=False,
              encoding="utf-8", sep=";")

    return df


def copy_elements_data(origin=elements_original_path, goal=elements_path):
    try:
        shutil.copytree(origin, goal)
    except Exception as e:
        print("Fehler beim Kopieren des Ordners", e)


if __name__ == "__main__":
    sequences, sequence_dict = crawl_sequences_data()
    aggregation = run_tsam(sequences, typical_periods=40)
    periods, parameters, timeindex = prepare_oemof_parameters(aggregation)
    convert_tsa_periods_to_sequences(periods, timeindex, sequence_dict)
    create_oemof_periods_csv(periods)
    copy_tsa_parameter(parameters)
    copy_elements_data()
    # resample_tsa_sequences_to_original_sequences()
