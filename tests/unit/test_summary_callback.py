from datetime import datetime
from unittest import mock

import pytest
import pandas as pd

from everviz.plugins.summary_plot import summary_callback
from everviz.plugins.summary_plot.util import calculate_statistics

__TEST_DATA = {
    "realization": range(12),
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


@pytest.mark.parametrize(
    "lines, x_filter, x_key",
    [([datetime(2000, 1, 1)], "date", "batch"), ([0], "batch", "date")],
)
def test_get_data_callback(monkeypatch, lines, x_filter, x_key):
    plotly_mock = mock.Mock()
    plotly_mock.Scatter.return_value = "called_scatter"
    monkeypatch.setattr(summary_callback, "go", plotly_mock)
    df = pd.DataFrame(__TEST_DATA)
    df = df.set_index(["batch", "date"])
    summary_callback._get_data_lines(df, ["key1"], lines, x_filter, x_key)
    plotly_mock.Scatter.assert_called_once()


@pytest.mark.parametrize(
    "lines, x_filter, x_key",
    [([datetime(2000, 1, 1)], "date", "batch"), ([0], "batch", "date")],
)
def test_get_lines_callback(monkeypatch, lines, x_filter, x_key):
    plotly_mock = mock.Mock()
    plotly_mock.Scatter.return_value = "scatter"
    monkeypatch.setattr(summary_callback, "go", plotly_mock)
    df = pd.DataFrame(__TEST_DATA)

    df = calculate_statistics(df).set_index(["summary_key", "batch", "date"])

    traces = summary_callback._get_statistics_lines(
        df, ["key1"], lines, x_filter, x_key
    )

    assert plotly_mock.Scatter.call_count == 3
    assert traces == ["scatter", "scatter", "scatter"]
