from functools import partial

import numpy as np
import pandas as pd


def calculate_statistics(data):
    data = data.reset_index()
    index = ["function", "batch"]
    result = pd.pivot_table(
        data,
        values="value",
        index=index,
        aggfunc=[
            "mean",
            partial(np.quantile, q=0.1),
            partial(np.quantile, q=0.9),
            "min",
            "max",
        ],
    )
    min_index = data.groupby(index)["value"].idxmin()
    max_index = data.groupby(index)["value"].idxmax()
    min_realization = data.loc[min_index].set_index(index)["realization"]
    max_realization = data.loc[max_index].set_index(index)["realization"]
    result = pd.concat([result, min_realization, max_realization], axis=1)
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
