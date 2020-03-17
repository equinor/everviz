import pytest
import numpy as np
from pandas import DataFrame
from everviz.pages.controls import control_data_per_batch, control_data_initial_vs_best


def test_control_data_per_batch(mocker):
    api_mock = mocker.Mock()
    control_values = [
        {"control": "c1", "batch": 0, "value": 0},
        {"control": "c2", "batch": 0, "value": 0},
        {"control": "c1", "batch": 1, "value": 42},
        {"control": "c1", "batch": 1, "value": 24},
    ]
    api_mock.control_values = control_values
    result = control_data_per_batch(api_mock)
    expected = DataFrame(control_values)

    assert expected.equals(result)


@pytest.mark.parametrize(
    "controls, objectives, expected",
    [
        (
            [{"control": "c1", "batch": 0, "value": 12},],
            [
                {
                    "function": "fc",
                    "batch": 0,
                    "realization": "0",
                    "simulation": "0",
                    "value": 1,
                },
            ],
            [{"control": "c1", "batch": "initial", "value": 12},],
        ),
        (
            [
                {"control": "c1", "batch": 0, "value": 12},
                {"control": "c1", "batch": 1, "value": 30},
            ],
            [
                {
                    "function": "fc",
                    "batch": 0,
                    "realization": "0",
                    "simulation": "0",
                    "value": 1,
                },
                {
                    "function": "fc",
                    "batch": 1,
                    "realization": "0",
                    "simulation": "0",
                    "value": 2,
                },
            ],
            [
                {"control": "c1", "batch": "initial", "value": 12},
                {"control": "c1", "batch": "best", "value": 30},
            ],
        ),
        (
            [
                {"control": "c1", "batch": 0, "value": 12},
                {"control": "c2", "batch": 0, "value": 30},
                {"control": "c1", "batch": 1, "value": 20},
                {"control": "c2", "batch": 1, "value": 22},
                {"control": "c1", "batch": 2, "value": 10},  # best
                {"control": "c2", "batch": 2, "value": 32},  # best
                {"control": "c1", "batch": 3, "value": 2},
                {"control": "c2", "batch": 3, "value": 40},
            ],
            [
                {
                    "function": "fc",
                    "batch": 0,
                    "realization": "0",
                    "simulation": "0",
                    "value": 1,
                },
                {
                    "function": "fc",
                    "batch": 1,
                    "realization": "0",
                    "simulation": "0",
                    "value": 2,
                },
                {
                    "function": "fc",
                    "batch": 2,
                    "realization": "0",
                    "simulation": "0",
                    "value": 4,
                },  # best value
                {
                    "function": "fc",
                    "batch": 3,
                    "realization": "0",
                    "simulation": "0",
                    "value": 0,
                },
            ],
            [
                {"control": "c1", "batch": "initial", "value": 12},
                {"control": "c2", "batch": "initial", "value": 30},
                {"control": "c1", "batch": "best", "value": 10},
                {"control": "c2", "batch": "best", "value": 32},
            ],
        ),
    ],
)
def test_control_data_initial_vs_best(controls, objectives, expected, mocker):
    api_mock = mocker.Mock()
    api_mock.control_values = controls
    api_mock.objective_values = objectives
    result = control_data_initial_vs_best(api_mock)
    expected = DataFrame(expected)
    assert np.array_equal(result.values, expected.values)
