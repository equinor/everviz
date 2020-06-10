from functools import partial

import pandas as pd
import numpy as np


def calculate_statistics(data):
    data = pd.pivot_table(
        data,
        values="value",
        index=["function", "batch"],
        aggfunc=[np.mean, partial(np.quantile, q=0.1), partial(np.quantile, q=0.9),],
    )
    data.columns = ["Mean", "P10", "P90"]
    return data.sort_index().reset_index()
