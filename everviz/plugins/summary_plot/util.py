from functools import partial

import pandas
import numpy


def calculate_statistics(summary_values, keys):
    if keys is None or len(keys) == 0:
        raise AssertionError("List of summary keys is required")
    # Make rows out of the keys for statistics.
    reshaped_summary_values = pandas.melt(
        summary_values,
        id_vars=["batch", "date", "realization"],
        value_vars=keys,
        var_name="summary_key",
        value_name="value",
    ).dropna()

    # Aggregate the values over the realizations, using pivot_table, keeping the
    # key, batch and date as the multi-index, calculating statistics of the
    # values over the realizations.
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
