# slapp/utils/time_series_aggregation.py

"""
Perform time series aggregation using tsam with oemof-tabular data packages.

This module contains functions that simplify the process of aggregating time
series data, making it easier to handle large datasets efficiently.
"""

from __future__ import annotations

import shutil
from ast import literal_eval
from pathlib import Path

import pandas as pd
import tsam.timeseriesaggregation as tsam
from frictionless import Package

SCENARIO_FOLDER = Path(__file__).parent.parent / "data" / "oemof"
SCENARIO_ORIGINAL = "scenario_2045"
SCENARIO_TARGET = "scenario_2045_tsam"

sequences_original_path = SCENARIO_FOLDER / SCENARIO_ORIGINAL / "data" / "sequences"
datapackage_path = SCENARIO_FOLDER / SCENARIO_ORIGINAL
elements_original_path = SCENARIO_FOLDER / SCENARIO_ORIGINAL / "data" / "elements"

periods_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "periods"
sequences_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "sequences"
tsam_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "tsam"
elements_path = SCENARIO_FOLDER / SCENARIO_TARGET / "data" / "elements"


def crawl_oemof_tabular_datapackage(path: Path = datapackage_path) -> tuple[pd.DataFrame, dict[str, list]]:
    """
    Crawl the oemof-tabular sequences and merge into single dataframe.

    This is necessary to perform tsam with all time series data.

    Parameters
    ----------
    path : Path
        The path object pointing to the datapackage JSON-file.

    Returns
    -------
    profiles : pd.DataFrame
        DataFrame that contains all sequence data specified in the
        oemof-tabular datapackage.

    file_columns : dict
        Dictionary containing the file paths of the csv-files in the sequences
        path as keys and the column names of each csv-file as values.

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
            profiles = pd.read_csv(
                file_name,
                delimiter=";",
                encoding="utf-8",
                index_col="timeindex",
                parse_dates=True,
            )
            file_columns[file_name] = profiles.columns.tolist()
            dfs.append(profiles)

    profiles = pd.concat(dfs, axis=1)

    return profiles, file_columns


def crawl_sequences_data(path: Path = sequences_original_path) -> tuple[pd.DataFrame, dict[str, list]]:
    """
    Crawl the sequences csv-files of oemof-tabular data/sequences path and merges them into one single DataFrame.

    This is necessary to perform tsam with all time series data.

    Parameters
    ----------
    path : Path
        The path object pointing to the datapackage JSON-file.

    Returns
    -------
    profiles : pd.DataFrame
        DataFrame that contains all sequence data specified in the
        oemof-tabular datapackage.

    file_columns : dict
        Dictionary containing the file paths of the csv-files in the sequences
        path as keys and the column names of each csv-file as values.

    """
    # Dictionary to keep track of columns from each file
    file_columns = {}

    # List to store dataframes
    dfs = []

    for file_name in path.iterdir():
        if file_name.is_file() and file_name.suffix in ".csv":
            profiles = pd.read_csv(file_name, encoding="utf8", sep=";", parse_dates=True, index_col="timeindex")
            file_columns[file_name.name] = profiles.columns.tolist()
            dfs.append(profiles)

    profiles = pd.concat(dfs, axis=1)

    return profiles, file_columns


def run_tsam(
    profiles: pd.DataFrame,
    typical_periods: int = 40,
    hours_per_period: int = 24,
) -> tsam.TimeSeriesAggregation:
    """
    Run tsam time series aggregation on merged oemof sequences.

    The default Clustermethod is set to 'k_means' but can be changed
    accordingly (see the tsam documentation for further detail).


    Parameters
    ----------
    profiles: pd.DataFrame
        DataFrame that contains all sequence data specified in the
        oemof-tabular datapackage

    typical_periods: int; Default: 40
        Number of typcial periods used for the aggregation.

    hours_per_period: int; Default: 24
        Number of hours per period used for aggregation.

    Returns
    -------
    aggregation: tsam.TimeSeriesAggregation
        The tsam.TimeSeriesAggregation object contains all relevant parameters
        and values as a result of executing the time series aggregation

    """
    tsa_aggregation = tsam.TimeSeriesAggregation(
        profiles,
        noTypicalPeriods=typical_periods,
        hoursPerPeriod=hours_per_period,
        sortValues=False,
        clusterMethod="k_means",
        rescaleClusterPeriods=False,
        extremePeriodMethod="replace_cluster_center",
        representationMethod="durationRepresentation",
    )

    return tsa_aggregation


def prepare_oemof_parameters(
    tsa_aggregation: tsam.TimeSeriesAggregation,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Index]:
    """
    Take tsa_aggregation object and derive tsa_parameters, tsa_sequences, tsa_timeindex.

    Parameters
    ----------
    tsa_aggregation: tsam.TimeSeriesAggregation
        contains all relevant parameters and values as a result of executing
        the time series aggregation

    Returns
    -------
    tsa_sequences: pd.DataFrame
        contains typical periods and data of all oemof-tabular sequences
    tsa_parameters: pd.DataFrame
        contains meta information to solph oemof model using tsam
    tsa_timeindex: pd.Index
        contains the timeindex of aggregated and is used as index for
        seqeuences data

    """
    tsa_sequences = tsa_aggregation.createTypicalPeriods()
    tsa_sequences = pd.DataFrame(tsa_sequences)

    tsa_parameters = {
        "period": 1,
        "timesteps_per_period": tsa_aggregation.hoursPerPeriod,
        "order": [tsa_aggregation.clusterOrder.tolist()],
    }

    tsa_parameters = pd.DataFrame(tsa_parameters)

    tsa_timeindex = pd.date_range(
        tsa_aggregation.timeIndex[0],
        periods=tsa_aggregation.noTypicalPeriods * tsa_aggregation.hoursPerPeriod,
        freq="h",
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    tsa_timeindex.name = "timeindex"

    return tsa_sequences, tsa_parameters, tsa_timeindex


def convert_tsa_sequences_to_oemof_sequences(
    tsa_sequences: pd.DataFrame,
    tsa_timeindex: pd.Index,
    file_columns: dict,
    path: Path = sequences_path,
) -> None:
    """
    Convert and save aggregated time series dataframe into oemof-tabular sequence files.

    Parameters
    ----------
    tsa_sequences: pd.DataFrame
        contains typical periods and data of all oemof-tabular sequences

    tsa_timeindex: pd.Index
        contains the timeindex of aggregated and is used as index for
        seqeuences data.

    file_columns : dict
        Dictionary containing the file paths of the csv-files in the sequences
        path as keys and the column names of each csv-file as values.

    path : Path
        The Path object pointing to the oemof-tabular sequqnces directory
        (data/sequqnces) in which the tsa_profiles will be stored.

    Returns
    -------
    None

    """
    if not Path.exists(path):
        Path.mkdir(path, parents=True)

    tsa_sequences["timeindex"] = tsa_timeindex
    tsa_sequences = tsa_sequences.set_index("timeindex")

    for file_name, columns in file_columns.items():
        # Subset the DataFrame based on original columns
        df_subset = tsa_sequences[columns]
        # Write to CSV
        df_subset.to_csv(Path(path, file_name), encoding="utf-8", sep=";", index=True, index_label="timeindex")


def resample_tsa_sequences_to_original_sequences(
    origin: Path = sequences_original_path,
    goal: Path = sequences_path,
    tsa_parameters_dir: Path = tsam_path,
    path: Path = sequences_path / "sequences_resampled",
) -> None:
    """
    Convert and save aggregated time series dataframe into oemof-tabular sequence files.

    Parameters
    ----------
    origin : Path
        The Path object pointing to the oemof-tabular sequences directory
        (data/sequences) in which the original sequences are stored.

    goal : Path
        The Path object pointing to the oemof-tabular sequences directory
        (data/sequences) in which the tsam aggregated sequences are stored.

    tsa_parameters_dir : Path
        The Path object pointing to the oemof-tabular tsam directory
        (data/tsam) in which the tsam parameters are stored.

    path : Path, Default: sequences_path / sequences_resampled
        The Path object pointing to the  directory
        in which the tsa_profiles will be stored.

    Returns
    -------
    None

    """
    if not tsa_parameters_dir.exists():
        raise FileNotFoundError(f"Directory does not exist: {tsa_parameters_dir}")

    if not origin.exists():
        raise FileNotFoundError(f"Directory does not exist: {origin}")

    if not goal.exists():
        raise FileNotFoundError(f"Directory does not exist: {goal}")

    if not path.exists():
        Path.mkdir(path)

    tsa_parameters = pd.read_csv(
        Path(tsa_parameters_dir, "tsa_parameters.csv"),
        encoding="utf8",
        sep=";",
        usecols=["order"],
        converters={"order": literal_eval},
    )

    tsa_cluster_order = tsa_parameters.iloc[0, 0]

    for file_name in goal.iterdir():
        if file_name.is_file() and file_name.suffix in ".csv":
            dfs = []

            tsa_profiles = pd.read_csv(file_name, encoding="utf-8", sep=";", parse_dates=True, index_col="timeindex")

            timeindex_original = pd.read_csv(
                Path(origin, file_name.name),
                encoding="utf8",
                sep=";",
                usecols=[0],
                index_col=[0],
            )

            for item in tsa_cluster_order:
                df_subset = tsa_profiles[item * 24 : (item + 1) * 24]
                tsa_profiles.append(df_subset)

            tsa_profiles = pd.concat(dfs, axis=0)
            tsa_profiles["timeindex"] = timeindex_original.index
            tsa_profiles = tsa_profiles.set_index("timeindex")

            tsa_profiles.to_csv(Path(path, file_name.name), encoding="utf-8", sep=";", index=True)


def create_oemof_periods_csv(
    tsa_timeindex: pd.Index,
    no_of_periods: int = 1,
    timeincrement: int = 1,
    path: Path = periods_path,
) -> pd.DataFrame:
    """
    Create and store periods into oemof-tabular datapackage.

    This necessary for multi-period optimization in oemof, if
    no_of_periods=0 function passes None.

    Parameters
    ----------
    tsa_timeindex: pd.Index
        Contains the timeindex of aggregated and is used as index for
        seqeuences data.

    no_of_periods : int
        Number of periods used in oemof NOT in time series aggregation.

    timeincrement : int
        Timeincrement for each period and timestep to allow for
        segmentation.

    path : Path, Default: sequences_path / sequences_resampled
        The Path object pointing to the oemof-tabular datapackage directory
        in which the periods will be stored.

    Returns
    -------
    periods: pd.DataFrame
        Dataframe that maps timeindex, periods and timeincrement for
        each period.

    """
    periods = pd.DataFrame()
    if no_of_periods != 1:
        if not path.exists():
            Path.mkdir(path)

        periods = pd.DataFrame(index=tsa_timeindex)
        periods["periods"] = no_of_periods - 1
        periods["timeincrement"] = timeincrement

        periods.to_csv(Path(path, "periods.csv"), index=True, encoding="utf-8", sep=";")
    return periods


def store_tsa_parameter(tsa_parameters: pd.DataFrame, path: Path = tsam_path) -> None:
    """
    Store tsa_parameters to path.

    Parameters
    ----------
    tsa_parameters : pd.DataFrame
        The path to the origin directory to copy from. Defaults to elements_original_path.
    path : Path
        The path to the oemof-tabular datapackage data/tsam.

    Returns
    -------
    None

    """
    if not path.exists():
        Path.mkdir(path)

    tsa_parameters.to_csv(Path(path, "tsa_parameters.csv"), index=False, encoding="utf-8", sep=";")


def copy_elements_data(origin_path: Path = elements_original_path, goal_path: Path = elements_path) -> None:
    """
    Copy data from the origin directory to the goal directory if the goal directory does not exist.

    Parameters
    ----------
    origin_path : Union[str, Path]
        The path to the origin directory to copy from. Defaults to elements_original_path.
    goal_path : Union[str, Path]
        The path to the goal directory to copy to. Defaults to elements_path.

    Returns
    -------
    None

    """
    if not goal_path.exists():
        shutil.copytree(origin_path, goal_path)


if __name__ == "__main__":
    sequences, sequence_dict = crawl_sequences_data()
    aggregation = run_tsam(sequences, typical_periods=40)
    aggregated_sequences, parameters, timeindex = prepare_oemof_parameters(aggregation)
    convert_tsa_sequences_to_oemof_sequences(aggregated_sequences, timeindex, sequence_dict)
    create_oemof_periods_csv(timeindex)
    store_tsa_parameter(parameters)
    copy_elements_data()
