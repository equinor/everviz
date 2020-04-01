import os
from collections import namedtuple
from functools import partial

import pandas
import numpy

from everviz.log import get_logger


DataSources = namedtuple("DataSource", ["summary_values", "summary_statistics"])

logger = get_logger()

_SUMMARY_INDEX_COLUMNS = ["batch", "date", "simulation"]


def _summary_values(summary_values):
    # Sort by the index columns.
    sorted_values = (
        summary_values.set_index(_SUMMARY_INDEX_COLUMNS).sort_index().reset_index()
    )
    return sorted_values


def _summary_statistics(summary_values):
    # Find the key names.
    value_vars = [
        column
        for column in summary_values.columns
        if column not in _SUMMARY_INDEX_COLUMNS
    ]

    # Make rows out of the keys for statistics.
    reshaped_summary_values = pandas.melt(
        summary_values,
        id_vars=_SUMMARY_INDEX_COLUMNS,
        value_vars=value_vars,
        var_name="summary_key",
        value_name="value",
    )

    # Aggregate the values over the simulations, using pivot_table, keeping the
    # key, batch and date as the multi-index, calculating statistics of the
    # values over the simulations.
    summary_statistics = pandas.pivot_table(
        reshaped_summary_values,
        values="value",
        index=["summary_key", "batch", "date"],
        aggfunc=[
            numpy.mean,
            partial(numpy.quantile, q=0.1),
            partial(numpy.quantile, q=0.9),
        ],
    ).droplevel(1, axis="columns")
    summary_statistics.columns = ["mean", "P10", "P90"]

    # Sort the multi index, and reset them to columns.
    sorted_statistics = summary_statistics.sort_index().reset_index()

    return sorted_statistics


def _set_up_data_sources(api, keys=None):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")

    # Make a table which statistics over the simulations.
    summary_values = api.summary_values(keys=keys)

    if summary_values.empty:
        return None

    logger.info("Generating summary values plot")

    summary_values_file = os.path.join(everviz_path, "summary_values.csv")
    values = _summary_values(summary_values)
    values.to_csv(summary_values_file, index=False)
    logger.info(f"File created: {summary_values_file}")

    summary_statistics_file = os.path.join(everviz_path, "summary_statistics.csv")
    statistics = _summary_statistics(summary_values)
    statistics.to_csv(summary_statistics_file, index=False)
    logger.info(f"File created: {summary_statistics_file}")

    return DataSources(
        summary_values=summary_values_file, summary_statistics=summary_statistics_file,
    )


def page_layout(api):
    sources = _set_up_data_sources(api)

    if sources is None:
        return {}

    return {
        "title": "Summary Values",
        "content": [
            "## Summary values as a function of date",
            {
                "SummaryPlot": {
                    "values_file": sources.summary_values,
                    "statistics_file": sources.summary_statistics,
                    "xaxis": "date",
                },
            },
            "## Summary values as a function of batch",
            {
                "SummaryPlot": {
                    "values_file": sources.summary_values,
                    "statistics_file": sources.summary_statistics,
                    "xaxis": "batch",
                },
            },
        ],
    }
