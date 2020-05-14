import os
from collections import namedtuple
from functools import partial
import pandas as pd
import numpy as np

from everviz.log import get_logger

DataSources = namedtuple(
    "DataSource", ["objective_values", "objective_statistics", "total_objective_values"]
)

logger = get_logger()


def _objective_values_from_api(api):
    return pd.DataFrame(api.objective_values)


def _total_objective_values_from_api(api):
    single_objectives = api.single_objective_values
    accepted_batches = api.accepted_batches
    for objective in single_objectives:
        objective.update({"accepted": objective["batch"] in accepted_batches})
    return pd.DataFrame(single_objectives)


def _objective_values(data):
    # Sort by the index columns.
    data = data.drop(columns=["realization"])
    sorted_values = (
        data.set_index(["function", "batch", "simulation"]).sort_index().reset_index()
    )
    return sorted_values


def _total_objective_values(data):
    # Sort by the index columns.
    sorted_values = data.set_index("batch").sort_index().reset_index()
    return sorted_values


def _objective_statistics(data):
    # Aggregate the values over the simulations, using pivot_table, keeping the
    # batch and function as the multi-index, calculating statistics of the
    # values over the simulations.
    statistics = pd.pivot_table(
        data,
        values="value",
        index=["function", "batch"],
        aggfunc=[np.mean, partial(np.quantile, q=0.1), partial(np.quantile, q=0.9),],
    )
    statistics.columns = ["Mean", "P10", "P90"]

    # Sort the multi index, and reset them to columns.
    sorted_statistics = statistics.sort_index().reset_index()

    return sorted_statistics


def _set_up_data_sources(api):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")

    logger.info("Generating objective values plot")
    data = _objective_values_from_api(api)

    objective_values_file = os.path.join(everviz_path, "objective_values.csv")
    values = _objective_values(data)
    values.to_csv(objective_values_file, index=False)
    logger.info(f"File created: {objective_values_file}")  # pylint: disable=W1203

    objective_statistics_file = os.path.join(everviz_path, "objective_statistics.csv")
    statistics = _objective_statistics(data)
    statistics.to_csv(objective_statistics_file, index=False)
    logger.info(f"File created: {objective_statistics_file}")  # pylint: disable=W1203

    logger.info("Generating total objective values plot")
    data = _total_objective_values_from_api(api)

    total_objective_values_file = os.path.join(
        everviz_path, "total_objective_values.csv"
    )
    values = _total_objective_values(data)
    values.to_csv(total_objective_values_file, index=False)
    logger.info(f"File created: {total_objective_values_file}")  # pylint: disable=W1203

    return DataSources(
        objective_values=objective_values_file,
        objective_statistics=objective_statistics_file,
        total_objective_values=total_objective_values_file,
    )


def _single_objective_title(api):
    nr_function = len(api.objective_function_names)
    if nr_function > 1:
        return "Weighted objective function"
    return "Objective function"


def page_layout(api):
    sources = _set_up_data_sources(api)
    return {
        "title": "Objectives",
        "content": [
            "## Objective function values",
            {
                "ObjectivesPlot": {
                    "values_file": sources.objective_values,
                    "statistics_file": sources.objective_statistics,
                },
            },
            f"## {_single_objective_title(api)}",
            {"SingleObjectivesPlot": {"csv_file": sources.total_objective_values,},},
        ],
    }
