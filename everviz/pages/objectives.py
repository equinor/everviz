import os
from collections import namedtuple
import pandas as pd

from everviz.log import get_logger

DataSources = namedtuple("DataSource", ["objective_values", "total_objective_values"])

logger = get_logger()


def _objective_values_from_api(api):
    return pd.DataFrame(api.objective_values)


def _total_objective_values_from_api(api):
    return pd.DataFrame(api.single_objective_values)


def _objective_values(data):
    # Sort by the index columns.
    data = data.drop(columns=["simulation"])
    sorted_values = (
        data.set_index(["function", "batch", "realization"]).sort_index().reset_index()
    )
    return sorted_values


def _total_objective_values(data):
    # Sort by the index columns.
    sorted_values = data.set_index("batch").sort_index().reset_index()
    return sorted_values


def _set_up_data_sources(api):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")

    logger.info("Generating objective values plot")
    data = _objective_values_from_api(api)

    objective_values_file = os.path.join(everviz_path, "objective_values.csv")
    values = _objective_values(data)
    values.to_csv(objective_values_file, index=False)
    logger.info(f"File created: {objective_values_file}")  # pylint: disable=W1203

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
        total_objective_values=total_objective_values_file,
    )


def _single_objective_title(api):
    nr_function = len(api.objective_function_names)
    if nr_function > 1:
        return "Objective functions"
    return "Objective"


def page_layout(api):
    sources = _set_up_data_sources(api)
    return {
        "title": "Objectives",
        "content": [
            "## Objective function values",
            {
                "ObjectivesPlot": {
                    "csv_file": sources.objective_values,
                },
            },
            f"## {_single_objective_title(api)}",
            {
                "SingleObjectivesPlot": {
                    "csv_file": sources.total_objective_values,
                },
            },
        ],
    }
