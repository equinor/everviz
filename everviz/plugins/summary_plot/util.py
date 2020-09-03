from functools import partial

import pandas
import numpy


def calculate_statistics(data, keys):
    if keys is None or len(keys) == 0:
        raise AssertionError("List of summary keys is required")
    # Make rows out of the keys for statistics.
    data = pandas.melt(
        data,
        id_vars=["batch", "date", "realization"],
        value_vars=keys,
        var_name="summary_key",
        value_name="value",
    ).dropna()
    # Aggregate the values over the realizations, using pivot_table, keeping the
    # key, batch and date as the multi-index, calculating statistics of the
    # values over the realizations.
    index = ["summary_key", "batch", "date"]
    statistics = pandas.pivot_table(
        data,
        values="value",
        index=index,
        aggfunc=[
            numpy.mean,
            partial(numpy.quantile, q=0.1),
            partial(numpy.quantile, q=0.9),
            numpy.min,
            numpy.max,
        ],
    ).droplevel(1, axis="columns")
    min_index = data.groupby(index)["value"].idxmin()
    max_index = data.groupby(index)["value"].idxmax()
    min_realization = data.loc[min_index].set_index(index)["realization"]
    max_realization = data.loc[max_index].set_index(index)["realization"]
    result = pandas.concat([statistics, min_realization, max_realization], axis=1)
    result.columns = [
        "mean",
        "P10",
        "P90",
        "min_value",
        "max_value",
        "min_realization",
        "max_realization",
    ]
    return result.sort_index().reset_index()
