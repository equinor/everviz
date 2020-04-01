import os
import pandas
import numpy
from collections import namedtuple
from functools import partial
from everviz.log import get_logger


DataSources = namedtuple("DataSource", "summary_values")

logger = get_logger()


def _summary_values(summary_values):
    # Rename the batch, simulation, and date columsn.
    summary_values.rename(
        columns={"batch": "Batch", "simulation": "Simulation", "date": "Date"},
        inplace=True,
    )

    # Find the key names.
    id_vars = ["Batch", "Date", "Simulation"]
    value_vars = [column for column in summary_values.columns if column not in id_vars]

    # Make rows out of the keys.
    summary_values = pandas.melt(
        summary_values,
        id_vars=id_vars,
        value_vars=value_vars,
        var_name="Summary Key",
        value_name="Value",
    )

    # Aggregate the values over the simulations, using pivot_table, keeping the
    # key, batch and date as the multi-index, calculating statistics of the
    # values over the simulations.
    summary_values = pandas.pivot_table(
        summary_values,
        values="Value",
        index=["Summary Key", "Batch", "Date"],
        aggfunc=[
            numpy.mean,
            partial(numpy.quantile, q=0.1),
            partial(numpy.quantile, q=0.9),
        ],
    )

    # Rename the statistics columns.
    summary_values = summary_values.droplevel(1, axis="columns")
    summary_values.columns = ["Mean", "P10", "P90"]

    # Sort the multi index, and reset them to columns.
    return summary_values.sort_index().reset_index()


def _set_up_data_sources(api, keys=None):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")

    # Make a table which statistics over the simulations.
    summary_values = api.summary_values(keys=keys)

    if summary_values.empty:
        return None

    logger.info("Generating summary values plot")
    summary_values_file = os.path.join(everviz_path, "summary_values.csv")
    data = _summary_values(summary_values)
    data.to_csv(summary_values_file, index=False, sep=";")
    logger.info(f"File created: {summary_values_file}")

    return DataSources(summary_values=summary_values_file,)


def page_layout(api):
    sources = _set_up_data_sources(api)
    if sources is None:
        return ""
    else:
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
