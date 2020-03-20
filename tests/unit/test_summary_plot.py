import pytest
import pandas
import numpy
from datetime import datetime
from pathlib import Path
from everviz.pages.summary_values import _summary_values

test_data = {
    "simulation": [0, 1, 2, 3, 4, 5],
    "batch": [0, 1, 2, 0, 1, 2],
    "date": [
        datetime(2000, 1, 1),
        datetime(2000, 2, 1),
        datetime(2000, 3, 1),
        datetime(2000, 1, 1),
        datetime(2000, 2, 1),
        datetime(2000, 3, 1),
    ],
    "key1": [1, 2, 3, 4, 5, 6],
    "key2": [10, 20, 30, 40, 50, 60],
}


def test_summary_values(request, mocker):
    summary_values = _summary_values(pandas.DataFrame(test_data))

    assert list(summary_values.columns) == [
        "Summary Key",
        "Batch",
        "Date",
        "Mean",
        "P10",
        "P90",
    ]
    assert len(summary_values) == len(test_data["simulation"])
    assert set(summary_values["Summary Key"]) == set(["key1", "key2"])
    assert set(summary_values["Batch"]) == set(test_data["batch"])
    assert set(summary_values["Date"]) == set(
        [pandas.Timestamp(date) for date in test_data["date"]]
    )

    mean = []
    p10 = []
    p90 = []
    for key in ["key1", "key2"]:
        for batch in [0, 1, 2]:
            simulations = [i for i, b in enumerate(test_data["batch"]) if b == batch]
            data = numpy.array(test_data[key])[simulations]
            mean.append(numpy.mean(data))
            p10.append(numpy.quantile(data, q=0.1))
            p90.append(numpy.quantile(data, q=0.9))

    assert summary_values["Mean"].to_list() == mean
    assert summary_values["P10"].to_list() == p10
    assert summary_values["P90"].to_list() == p90
