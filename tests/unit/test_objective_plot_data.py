import os
import pandas as pd
import numpy as np

import everviz

from everviz.pages.objectives import (
    _set_up_data_sources,
    _objective_values,
    _objective_statistics,
    _total_objective_values,
)

OBJECTIVES = [
    {"batch": 0, "realization": 1, "function": "f0", "value": 100, "simulation": 0},
    {"batch": 0, "realization": 1, "function": "f1", "value": 200, "simulation": 1},
    {"batch": 2, "realization": 2, "function": "f0", "value": 200, "simulation": 2},
    {"batch": 2, "realization": 2, "function": "f1", "value": 400, "simulation": 3},
    {"batch": 0, "realization": 3, "function": "f0", "value": 300, "simulation": 4},
    {"batch": 0, "realization": 3, "function": "f1", "value": 600, "simulation": 5},
    {"batch": 2, "realization": 4, "function": "f0", "value": 400, "simulation": 6},
    {"batch": 2, "realization": 4, "function": "f1", "value": 800, "simulation": 7},
]


def test_objective_values_data_frame():
    """Test for the correct layout and size of the objective values data frame."""
    objective_values = _objective_values(pd.DataFrame(OBJECTIVES))

    assert set(objective_values.columns) == {
        "batch",
        "function",
        "value",
        "simulation",
    }
    assert len(objective_values) == len(OBJECTIVES)
    assert set(objective_values["batch"]) == {obj["batch"] for obj in OBJECTIVES}
    assert set(objective_values["function"]) == {obj["function"] for obj in OBJECTIVES}
    assert set(objective_values["simulation"]) == {
        obj["simulation"] for obj in OBJECTIVES
    }


def test_objective_statistics_data_frame():
    """Test for the correct layout and size of the objective statistics data frame"""
    objective_statistics = _objective_statistics(pd.DataFrame(OBJECTIVES))

    assert set(objective_statistics.columns) == {
        "batch",
        "function",
        "Mean",
        "P10",
        "P90",
    }
    assert len(objective_statistics) == 2 * 2  # #batches * #functions
    assert set(objective_statistics["batch"]) == {obj["batch"] for obj in OBJECTIVES}
    assert set(objective_statistics["function"]) == {
        obj["function"] for obj in OBJECTIVES
    }


def test_objective_statistics_content():
    """Test for the correct content of the objectives statistics data frame."""
    objective_statistics = _objective_statistics(pd.DataFrame(OBJECTIVES))

    mean = []
    p10 = []
    p90 = []
    for func in ["f0", "f1"]:
        for batch in [0, 2]:
            values = [
                obj["value"]
                for obj in OBJECTIVES
                if obj["batch"] == batch and obj["function"] == func
            ]
            mean.append(np.mean(values))
            p10.append(np.quantile(values, q=0.1))
            p90.append(np.quantile(values, q=0.9))

    assert objective_statistics["Mean"].to_list() == mean
    assert objective_statistics["P10"].to_list() == p10
    assert objective_statistics["P90"].to_list() == p90


def test_set_up_sources(mocker, monkeypatch, tmpdir):
    mock_api = mocker.Mock()
    mock_api.output_folder = tmpdir
    os.mkdir(os.path.join(tmpdir, "everviz"))
    monkeypatch.setattr(
        everviz.pages.objectives,
        "_objective_values_from_api",
        mocker.Mock(return_value=pd.DataFrame(OBJECTIVES)),
    )
    total_data = pd.DataFrame(OBJECTIVES).drop(
        columns=["realization", "function", "simulation"]
    )
    monkeypatch.setattr(
        everviz.pages.objectives,
        "_total_objective_values_from_api",
        mocker.Mock(return_value=total_data),
    )
    data_source = _set_up_data_sources(mock_api)
    assert data_source.objective_values == tmpdir / "everviz" / "objective_values.csv"
    assert (
        data_source.objective_statistics
        == tmpdir / "everviz" / "objective_statistics.csv"
    )
    assert (
        data_source.total_objective_values
        == tmpdir / "everviz" / "total_objective_values.csv"
    )


def test_total_objective_values_data_frame():
    total_data = pd.DataFrame(OBJECTIVES).drop(
        columns=["realization", "function", "simulation"]
    )
    total_objective_values = _total_objective_values(total_data)

    assert set(total_objective_values.columns) == {"batch", "value"}
    assert len(total_objective_values) == len(OBJECTIVES)
