import os
from collections import namedtuple

from everviz.log import get_logger


DataSources = namedtuple("DataSource", ["summary_values"])

logger = get_logger()


def _summary_values(summary_values):
    # Sort by the index columns.
    sorted_values = (
        summary_values.drop(columns="simulation")
        .set_index(["batch", "date", "realization"])
        .dropna(axis=1, how="all")
        .sort_index()
        .reset_index()
    )
    return sorted_values


def _set_up_data_sources(api, keys=None):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")

    # Make a table which statistics over the realizations.
    summary_values = api.summary_values(keys=keys)

    if summary_values.empty:
        return None

    logger.info("Generating summary values plot")

    summary_values_file = os.path.join(everviz_path, "summary_values.csv")
    values = _summary_values(summary_values)
    values.to_csv(summary_values_file, index=False)
    logger.info(f"File created: {summary_values_file}")  # pylint: disable=W1203

    return DataSources(summary_values=summary_values_file)


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
                    "csv_file": sources.summary_values,
                    "xaxis": "date",
                },
            },
            "## Summary values as a function of batch",
            {
                "SummaryPlot": {
                    "csv_file": sources.summary_values,
                    "xaxis": "batch",
                },
            },
        ],
    }
