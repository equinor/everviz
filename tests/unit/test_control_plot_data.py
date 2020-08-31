import os

import pytest
import numpy as np
import pandas as pd

from everviz.util import get_everviz_folder
from everviz.pages.controls import (
    _control_data_per_batch,
    _control_data_initial_vs_best,
    DataSources,
    _set_up_data_sources,
)


controls = [
    [
        {"control": "c1", "batch": 0, "value": 12},
    ],
    [
        {"control": "c1", "batch": 0, "value": 12},
        {"control": "c1", "batch": 1, "value": 30},
    ],
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
]
objectives = [
    [
        {
            "batch": 0,
            "objective": 1,
        },
    ],
    [
        {
            "batch": 0,
            "objective": 1,
        },
        {
            "batch": 1,
            "objective": 2,
        },
    ],
    [
        {
            "batch": 0,
            "objective": 1,
        },
        {
            "batch": 1,
            "objective": 2,
        },
        {
            "batch": 2,
            "objective": 4,
        },  # best value
        {
            "batch": 3,
            "objective": 0,
        },
    ],
]

expected = [
    [
        {"control": "c1", "batch": "initial", "value": 12},
    ],
    [
        {"control": "c1", "batch": "initial", "value": 12},
        {"control": "c1", "batch": "best", "value": 30},
    ],
    [
        {"control": "c1", "batch": "initial", "value": 12},
        {"control": "c2", "batch": "initial", "value": 30},
        {"control": "c1", "batch": "best", "value": 10},
        {"control": "c2", "batch": "best", "value": 32},
    ],
]


@pytest.fixture
def mocked_api(mocker):
    api_mock = mocker.Mock()
    api_mock.output_folder = "everest_output"
    api_mock.control_values = controls[0]
    api_mock.single_objective_values = objectives[0]
    return api_mock


def test_control_data_per_batch(mocker):
    api_mock = mocker.Mock()
    control_values = [
        {"control": "c1", "batch": 0, "value": 0},
        {"control": "c2", "batch": 0, "value": 0},
        {"control": "c1", "batch": 1, "value": 42},
        {"control": "c1", "batch": 1, "value": 24},
    ]
    api_mock.control_values = control_values
    result = _control_data_per_batch(api_mock)
    expected = pd.DataFrame(control_values)

    assert expected.equals(result)


@pytest.mark.parametrize(
    "controls, objectives, expected",
    [
        (controls[0], objectives[0], expected[0]),
        (controls[1], objectives[1], expected[1]),
        (controls[2], objectives[2], expected[2]),
    ],
)
def test_control_data_initial_vs_best(controls, objectives, expected, mocker):
    api_mock = mocker.Mock()
    api_mock.control_values = controls
    api_mock.single_objective_values = objectives
    result = _control_data_initial_vs_best(api_mock)
    expected_result = pd.DataFrame(expected)
    assert np.array_equal(result.values, expected_result.values)


def test_set_up_data_sources(tmpdir, mocked_api):
    expected = DataSources(
        controls_per_batch="everest_output/everviz/controls_per_batch.csv",
        controls_initial_vs_best="everest_output/everviz/controls_initial_vs_best.csv",
    )

    with tmpdir.as_cwd():
        for field in expected._fields:
            assert not os.path.exists(getattr(expected, field))

        get_everviz_folder(mocked_api)
        result = _set_up_data_sources(mocked_api)
        assert expected == result

        for field in result._fields:
            assert os.path.exists(getattr(result, field))
