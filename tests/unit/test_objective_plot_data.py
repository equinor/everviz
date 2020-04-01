import everviz
import operator
import os
import pandas as pd
import pytest

from everviz.pages.objectives import _calc_p10_p90, _set_up_data_sources, _calc_mean

OBJECTIVES = [
    {"batch": 0, "realization": 1, "function": "f0", "value": 100, "simulation": None},
    {"batch": 0, "realization": 1, "function": "f1", "value": 200, "simulation": None},
    {"batch": 2, "realization": 2, "function": "f0", "value": 200, "simulation": None},
    {"batch": 2, "realization": 2, "function": "f1", "value": 400, "simulation": None},
    {"batch": 0, "realization": 3, "function": "f0", "value": 300, "simulation": None},
    {"batch": 0, "realization": 3, "function": "f1", "value": 600, "simulation": None},
    {"batch": 2, "realization": 4, "function": "f0", "value": 400, "simulation": None},
    {"batch": 2, "realization": 4, "function": "f1", "value": 800, "simulation": None},
]


def test_insert_p10_p90():
    df = pd.DataFrame(OBJECTIVES)
    result = _calc_p10_p90(df)
    for header in ["P10", "P90"]:
        assert header in result


def test_mean():
    df = pd.DataFrame(OBJECTIVES)
    result = _calc_mean(df)
    assert all(
        result["Mean"].values
        == [300.0, 300.0, 450.0, 450.0, 300.0, 300.0, 450.0, 450.0]
    )


@pytest.mark.parametrize(
    "header_1, header_2", [("P10", "P90")],
)
def test_p10_p90(header_1, header_2):
    df = pd.DataFrame(OBJECTIVES)
    result = _calc_p10_p90(df)
    for val_1, val_2 in zip(result[header_1], result[header_2]):
        assert val_1 < val_2


def test_set_up_sources(mocker, monkeypatch, tmpdir):
    mock_api = mocker.Mock()
    mock_api.output_folder = tmpdir
    os.mkdir(os.path.join(tmpdir, "everviz"))
    monkeypatch.setattr(
        everviz.pages.objectives,
        "_objective_values",
        mocker.Mock(return_value=pd.DataFrame(OBJECTIVES)),
    )
    data_source = _set_up_data_sources(mock_api)
    assert data_source.objective_values == tmpdir / "everviz" / "objective_values.csv"
