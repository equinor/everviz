from datetime import datetime

import pandas as pd
import numpy as np

from everviz.pages.summary_values import page_layout, _summary_values
from everviz.plugins.summary_plot.util import calculate_statistics

__TEST_DATA = {
    "realization": range(12),
    "simulation": range(12),
    "batch": [0] * 6 + [1] * 6,
    "date": [
        datetime(2000, 1, 1),
        datetime(2000, 2, 1),
        datetime(2000, 3, 1),
        datetime(2000, 1, 1),
        datetime(2000, 2, 1),
        datetime(2000, 3, 1),
        datetime(2000, 1, 1),
        datetime(2000, 2, 1),
        datetime(2000, 3, 1),
        datetime(2000, 1, 1),
        datetime(2000, 2, 1),
        datetime(2000, 3, 1),
    ],
    "key1": range(1, 13),
    "key2": range(10, 130, 10),
}


def test_empty_summary_values(mocker):
    """Test for the case of missing summary values."""
    mock_api = mocker.Mock()
    mock_api.output_folder = "dummy"
    mock_api.summary_values.return_value = pd.DataFrame()
    layout = page_layout(mock_api)
    assert layout == {}


def test_summary_values_data_frame():
    """Test for the correct layout and size of the summary values data frame."""
    summary_values = _summary_values(pd.DataFrame(__TEST_DATA))

    assert list(
        summary_values.columns == ["summary_key", "batch", "date", "key1", "key2"]
    )
    assert len(summary_values) == len(__TEST_DATA["simulation"])
    assert set(summary_values["batch"]) == set(__TEST_DATA["batch"])
    assert set(summary_values["date"]) == {
        pd.Timestamp(date) for date in __TEST_DATA["date"]
    }


def test_summary_statistics_data_frame():
    """Test for the correct layout and size of the summary statistics data frame"""
    summary_values = _summary_values(pd.DataFrame(__TEST_DATA))
    summary_statistics = calculate_statistics(summary_values, ["key1", "key2"])

    assert list(summary_statistics.columns) == [
        "summary_key",
        "batch",
        "date",
        "mean",
        "P10",
        "P90",
        "min_value",
        "max_value",
        "min_realization",
        "max_realization",
    ]
    assert len(summary_statistics) == 2 * 3 * 2  # #batches * #dates * #keys
    assert set(summary_statistics["summary_key"]) == set(["key1", "key2"])
    assert set(summary_statistics["batch"]) == set(__TEST_DATA["batch"])
    assert set(summary_statistics["date"]) == {
        pd.Timestamp(date) for date in __TEST_DATA["date"]
    }


def test_summary_statistics_content():
    """Test for the correct content of the summary statistics data frame."""
    summary_values = _summary_values(pd.DataFrame(__TEST_DATA))
    summary_statistics = calculate_statistics(summary_values, ["key1", "key2"])

    mean = []
    p10 = []
    p90 = []
    min_value = []
    max_value = []
    min_realization = []
    max_realization = []
    for key in ["key1", "key2"]:
        zipped = list(
            zip(
                __TEST_DATA["batch"],
                __TEST_DATA["date"],
                __TEST_DATA[key],
                __TEST_DATA["realization"],
            )
        )
        for batch in [0, 1]:
            for date in [
                datetime(2000, 1, 1),
                datetime(2000, 2, 1),
                datetime(2000, 3, 1),
            ]:
                values = [v for b, d, v, _ in zipped if batch == b and date == d]
                realizations = [r for b, d, _, r in zipped if batch == b and date == d]
                mean.append(np.mean(values))
                p10.append(np.quantile(values, q=0.1))
                p90.append(np.quantile(values, q=0.9))
                min_value.append(np.min(values))
                max_value.append(np.max(values))
                min_realization.append(realizations[np.argmin(values)])
                max_realization.append(realizations[np.argmax(values)])

    assert summary_statistics["mean"].to_list() == mean
    assert summary_statistics["P10"].to_list() == p10
    assert summary_statistics["P90"].to_list() == p90
    assert summary_statistics["min_value"].to_list() == min_value
    assert summary_statistics["max_value"].to_list() == max_value
    assert summary_statistics["min_realization"].to_list() == min_realization
    assert summary_statistics["max_realization"].to_list() == max_realization
