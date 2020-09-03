import os

import pandas as pd
import numpy as np

import everviz

from everviz.pages.objectives import (
    _set_up_data_sources,
    _objective_values,
    _total_objective_values,
)

from everviz.plugins.objectives_plot.util import calculate_statistics

OBJECTIVES = [
    {
        "batch": 0,
        "realization": 1,
        "function": "f0",
        "value": 100,
        "simulation": 1,
        "weight": 0.75,
        "norm": 1,
    },
    {
        "batch": 0,
        "realization": 1,
        "function": "f1",
        "value": 200,
        "simulation": 1,
        "weight": 0.25,
        "norm": 1.5,
    },
    {
        "batch": 2,
        "realization": 2,
        "function": "f0",
        "value": 200,
        "simulation": 2,
        "weight": 0.75,
        "norm": 1,
    },
    {
        "batch": 2,
        "realization": 2,
        "function": "f1",
        "value": 400,
        "simulation": 2,
        "weight": 0.25,
        "norm": 1.5,
    },
    {
        "batch": 0,
        "realization": 1,
        "function": "f0",
        "value": 300,
        "simulation": 1,
        "weight": 0.75,
        "norm": 1,
    },
    {
        "batch": 0,
        "realization": 1,
        "function": "f1",
        "value": 600,
        "simulation": 1,
        "weight": 0.25,
        "norm": 1.5,
    },
    {
        "batch": 2,
        "realization": 2,
        "function": "f0",
        "value": 400,
        "simulation": 2,
        "weight": 0.75,
        "norm": 1,
    },
    {
        "batch": 2,
        "realization": 2,
        "function": "f1",
        "value": 800,
        "simulation": 2,
        "weight": 0.25,
        "norm": 1.5,
    },
]


def test_objective_values_data_frame():
    """Test for the correct layout and size of the objective values data frame."""
    objective_values = _objective_values(pd.DataFrame(OBJECTIVES))

    assert set(objective_values.columns) == {
        "batch",
        "function",
        "value",
        "realization",
        "weight",
        "norm",
    }
    assert len(objective_values) == len(OBJECTIVES)
    assert set(objective_values["batch"]) == {obj["batch"] for obj in OBJECTIVES}
    assert set(objective_values["function"]) == {obj["function"] for obj in OBJECTIVES}
    assert set(objective_values["realization"]) == {
        obj["realization"] for obj in OBJECTIVES
    }
    assert set(objective_values["weight"]) == {obj["weight"] for obj in OBJECTIVES}
    assert set(objective_values["norm"]) == {obj["norm"] for obj in OBJECTIVES}


def test_objective_statistics_data_frame():
    """Test for the correct layout and size of the objective statistics data frame"""
    objective_values = _objective_values(pd.DataFrame(OBJECTIVES))
    objective_statistics = calculate_statistics(objective_values)

    assert set(objective_statistics.columns) == {
        "batch",
        "function",
        "mean",
        "P10",
        "P90",
        "min_value",
        "max_value",
        "min_realization",
        "max_realization",
    }
    assert len(objective_statistics) == 2 * 2  # #batches * #functions
    assert set(objective_statistics["batch"]) == {obj["batch"] for obj in OBJECTIVES}
    assert set(objective_statistics["function"]) == {
        obj["function"] for obj in OBJECTIVES
    }


def test_objective_statistics_contenIt():
    """Test for the correct content of the objectives statistics data frame."""
    objective_values = _objective_values(pd.DataFrame(OBJECTIVES))
    objective_statistics = calculate_statistics(objective_values)
    mean = []
    p10 = []
    p90 = []
    min_value = []
    max_value = []
    min_realization = []
    max_realization = []
    for func in ["f0", "f1"]:
        for batch in [0, 2]:
            values = [
                obj["value"]
                for obj in OBJECTIVES
                if obj["batch"] == batch and obj["function"] == func
            ]
            realizations = [
                obj["realization"]
                for obj in OBJECTIVES
                if obj["batch"] == batch and obj["function"] == func
            ]
            mean.append(np.mean(values))
            p10.append(np.quantile(values, q=0.1))
            p90.append(np.quantile(values, q=0.9))
            min_value.append(np.min(values))
            max_value.append(np.max(values))
            min_realization.append(realizations[np.argmin(values)])
            max_realization.append(realizations[np.argmax(values)])
    assert objective_statistics["mean"].to_list() == mean
    assert objective_statistics["P10"].to_list() == p10
    assert objective_statistics["P90"].to_list() == p90
    assert objective_statistics["min_value"].to_list() == min_value
    assert objective_statistics["max_value"].to_list() == max_value
    assert objective_statistics["min_realization"].to_list() == min_realization
    assert objective_statistics["max_realization"].to_list() == max_realization


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
        data_source.total_objective_values
        == tmpdir / "everviz" / "total_objective_values.csv"
    )


def test_total_objective_values_data_frame():
    total_data = pd.DataFrame(OBJECTIVES).drop(
        columns=["realization", "function", "simulation", "weight", "norm"]
    )
    total_objective_values = _total_objective_values(total_data)

    assert set(total_objective_values.columns) == {"batch", "value"}
    assert len(total_objective_values) == len(OBJECTIVES)
