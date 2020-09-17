from itertools import cycle
from datetime import datetime
from unittest import mock

import pytest
import pandas as pd
from plotly.colors import DEFAULT_PLOTLY_COLORS

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
    plotly_mock.Scatter.assert_called()


@pytest.mark.parametrize(
    "keys, lines, x_filter, x_key",
    [
        ([], [datetime(2000, 1, 1)], "date", "batch"),
        (None, [0], "date", "batch"),
        (["key1"], [datetime(2000, 1, 1)], "date", "batch"),
        (["key1"], [0], "batch", "date"),
        (["key1", "key2"], [datetime(2000, 1, 1)], "date", "batch"),
        (["key1", "key2"], [0], "batch", "date"),
    ],
)
def test_get_lines_callback(monkeypatch, keys, lines, x_filter, x_key):
    plotly_mock = mock.Mock()
    plotly_mock.Scatter.return_value = "scatter"
    monkeypatch.setattr(summary_callback, "go", plotly_mock)
    df = pd.DataFrame(__TEST_DATA)

    try:
        df = calculate_statistics(df, keys).set_index(["summary_key", "batch", "date"])

        traces = summary_callback._get_statistics_lines(
            df, ["key1"], lines, x_filter, x_key
        )

        assert plotly_mock.Scatter.call_count == 5
        assert traces == 5 * ["scatter"]
    except AssertionError as e:
        assert str(e) in "List of summary keys is required"


@pytest.mark.parametrize(
    "keys, x_axis_title",
    [
        ([], "date"),
        (["key1", "key2", "key3"], "batch"),
    ],
)
def test_get_layout(keys, x_axis_title):
    expected = dict(
        xaxis={"title": x_axis_title},
        hovermode="closest",
    )
    colors = cycle(DEFAULT_PLOTLY_COLORS)
    for idx, key in enumerate(keys):
        color = next(colors)
        y_axis = f"yaxis{idx + 1}" if idx > 0 else "yaxis"
        expected.update(
            {
                y_axis: dict(
                    title=key,
                    titlefont=dict(color=color),
                    tickfont=dict(color=color),
                )
            }
        )
        if idx > 0:
            expected[y_axis].update(
                dict(
                    anchor="x",
                    overlaying="y",
                    side="right" if idx % 2 else "left",
                )
            )

    layout = summary_callback.get_layout(keys, x_axis_title)
    assert expected == layout
    if len(keys) > 0:
        assert "yaxis1" not in layout
        assert "yaxis3" in layout
