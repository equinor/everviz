import os
from datetime import datetime

import polars as pl
from everviz.pages.deltaplot import (
    _get_objective_delta_values,
    _get_summary_delta_values,
    _set_up_data_sources,
    page_layout,
)

_OBJECTIVES = [
    {"batch": 0, "realization": 1, "function": "f0", "value": 100, "simulation": 1},
    {"batch": 0, "realization": 2, "function": "f0", "value": 200, "simulation": 2},
    {"batch": 0, "realization": 1, "function": "f1", "value": 300, "simulation": 1},
    {"batch": 0, "realization": 2, "function": "f1", "value": 400, "simulation": 2},
    {"batch": 2, "realization": 1, "function": "f0", "value": 500, "simulation": 1},
    {"batch": 2, "realization": 2, "function": "f0", "value": 600, "simulation": 2},
    {"batch": 2, "realization": 1, "function": "f1", "value": 800, "simulation": 1},
    {"batch": 2, "realization": 2, "function": "f1", "value": 900, "simulation": 2},
]

_SUMMARY = {
    "realization": 3 * [1] + 3 * [2] + 3 * [1] + 3 * [2],
    "simulation": 3 * [1] + 3 * [2] + 3 * [1] + 3 * [2],
    "batch": [0] * 6 + [2] * 6,
    "date": 4
    * [
        datetime(2000, 1, 1).date().isoformat(),
        datetime(2000, 2, 1).date().isoformat(),
        datetime(2000, 3, 1).date().isoformat(),
    ],
    "key1": range(1, 13),
    "key2": range(10, 130, 10),
}

_SINGLE_OBJECTIVES = {"batch": [0, 2], "objective": [0.0, 1.0]}


def test_objective_values_data_frame(mocker):
    """Test for the correct layout and size of the objective values data frame."""
    mock_api = mocker.Mock()
    mock_api.objective_values = _OBJECTIVES

    objective_delta_values = _get_objective_delta_values(mock_api, 2)

    assert set(objective_delta_values.columns) == {"realization", "f0", "f1"}
    expected_len = 2
    assert len(objective_delta_values) == expected_len
    assert set(objective_delta_values["realization"]) == {
        obj["realization"] for obj in _OBJECTIVES
    }
    expected_f0_value = 400
    expected_f1_value = 500
    assert (objective_delta_values["f0"] == expected_f0_value).all()
    assert (objective_delta_values["f1"] == expected_f1_value).all()


def test_summary_values_data_frame(mocker):
    """Test for the correct layout and size of the objective values data frame."""
    mock_api = mocker.Mock()
    mock_api.summary_values.return_value = pl.DataFrame(_SUMMARY)

    summary_delta_values = _get_summary_delta_values(mock_api, 2)

    assert set(summary_delta_values.columns) == {"realization", "date", "key1", "key2"}
    expected_len = 6
    assert len(summary_delta_values) == expected_len
    assert set(summary_delta_values["realization"]) == set(_SUMMARY["realization"])
    expected_key1_value = 6
    expected_key2_value = 60
    assert (summary_delta_values["key1"] == expected_key1_value).all()
    assert (summary_delta_values["key2"] == expected_key2_value).all()


def test_set_up_sources(mocker, tmpdir):
    mock_api = mocker.Mock()
    mock_api.objective_values = _OBJECTIVES
    mock_api.single_objective_values = _SINGLE_OBJECTIVES
    mock_api.summary_values.return_value = pl.DataFrame(_SUMMARY)
    mock_api.output_folder = tmpdir

    os.mkdir(os.path.join(tmpdir, "everviz"))
    data_source = _set_up_data_sources(mock_api)
    assert (
        data_source.objective_delta_values
        == tmpdir / "everviz" / "objective_delta_values.csv"
    )
    assert (
        data_source.summary_delta_values
        == tmpdir / "everviz" / "summary_delta_values.csv"
    )


def test_delta_plot_layout_with_empty_summary(mocker, tmpdir):
    mock_api = mocker.Mock()
    mock_api.objective_values = _OBJECTIVES
    mock_api.single_objective_values = _SINGLE_OBJECTIVES
    mock_api.summary_values.return_value = pl.DataFrame(
        {"realization": [], "simulation": [], "date": [], "batch": []}
    )
    mock_api.output_folder = tmpdir

    os.mkdir(os.path.join(tmpdir, "everviz"))
    layout = page_layout(mock_api)

    assert "content" in layout
    content = layout["content"]
    expected_length = 3
    assert len(content) == expected_length
    assert "Objective functions" in content[0]
    assert "DeltaPlot" in content[1]
    assert "Summary keys: No data" in content[2]
