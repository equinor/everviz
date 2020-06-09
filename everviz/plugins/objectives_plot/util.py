from functools import partial

import pandas as pd
import numpy as np


def parse_range(numbers):
    result = set()
    if numbers is not None:
        for number in numbers.split(","):
            number = number.strip()
            if number.isdigit():
                result.add(int(number))
            elif "-" in number:
                number_range = number.split("-")
                start = number_range[0]
                stop = number_range[1]
                if start.isdigit() and stop.isdigit():
                    result |= set(range(int(start), int(stop) + 1))
    return result


def calculate_statistics(data):
    data = pd.pivot_table(
        data,
        values="value",
        index=["function", "batch"],
        aggfunc=[np.mean, partial(np.quantile, q=0.1), partial(np.quantile, q=0.9),],
    )
    data.columns = ["Mean", "P10", "P90"]
    return data.sort_index().reset_index()
