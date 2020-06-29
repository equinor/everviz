import os
from collections import namedtuple
import pandas as pd
from everviz.log import get_logger


DataSources = namedtuple(
    "DataSource", ["objective_delta_values", "summary_delta_values"]
)

logger = get_logger()


def _get_objective_delta_values(api, best_batch):
    data = pd.DataFrame(api.objective_values).drop(columns=["simulation"])
    initial = data[(data.batch == 0)].drop(columns=["batch"])
    best = data[data.batch == best_batch].drop(columns=["batch"])
    initial = initial.pivot(index="realization", values="value", columns="function")
    best = best.pivot(index="realization", values="value", columns="function")
    return (best - initial).reset_index()


def _get_summary_delta_values(api, best_batch):
    data = (
        api.summary_values()
        .drop(columns="simulation")
        .set_index(["realization", "date"])
        .dropna(axis=1, how="all")
    )
    if not data.empty:
        initial = data[(data.batch == 0)].drop(columns=["batch"])
        best = data[data.batch == best_batch].drop(columns=["batch"])
        return (best - initial).reset_index()
    return data


def _set_up_data_sources(api):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")

    objectives_df = pd.DataFrame(api.single_objective_values)
    best_batch = objectives_df.batch[objectives_df.objective.idxmax()]

    logger.info("Generating objective delta plot source data file")
    objective_csv_path = os.path.join(everviz_path, "objective_delta_values.csv")
    data = _get_objective_delta_values(api, best_batch)
    data.to_csv(objective_csv_path, index=False)
    logger.info(f"File created: {objective_csv_path}")  # pylint: disable=W1203

    logger.info("Generating summary delta plot source data file")
    summary_csv_path = os.path.join(everviz_path, "summary_delta_values.csv")
    data = _get_summary_delta_values(api, best_batch)
    if not data.empty:
        data.to_csv(summary_csv_path, index=False)
        logger.info(f"File created: {summary_csv_path}")  # pylint: disable=W1203
    else:
        logger.info("No summary data, not creating summary_delta_values.csv")
        summary_csv_path = None

    return DataSources(
        objective_delta_values=objective_csv_path, summary_delta_values=summary_csv_path
    )


def page_layout(api):
    sources = _set_up_data_sources(api)
    has_summary = sources.summary_delta_values is not None
    return {
        "title": "Objectives Delta Values",
        "content": [
            "## Objective functions: Difference between best and initial batch",
            {
                "DeltaPlot": {
                    "csv_file": sources.objective_delta_values,
                    "pre_select": "all",
                }
            },
        ]
        + (
            [
                "## Summary keys: Difference between best and initial batch",
                {
                    "DeltaPlot": {
                        "csv_file": sources.summary_delta_values,
                        "pre_select": "none",
                    },
                },
            ]
            if has_summary
            else ["## Summary keys: No data"]
        ),
    }
