import pandas as pd

import pytest
from everviz.pages.objectives import (
    _total_objective_values_from_api,
    _single_objective_title,
)

TEST_DATA = [
    {"batch": 0, "value": 100, "accepted": True},
    {"batch": 1, "value": 200, "accepted": True},
    {"batch": 2, "value": 200, "accepted": False},
    {"batch": 3, "value": 400, "accepted": True},
    {"batch": 4, "value": 300, "accepted": False},
    {"batch": 5, "value": 600, "accepted": False},
    {"batch": 6, "value": 400, "accepted": True},
    {"batch": 7, "value": 800, "accepted": True},
]


@pytest.fixture
def api_mock(mocker):
    api = mocker.Mock()
    single_objectives = [
        {"batch": data["batch"], "value": data["value"]} for data in TEST_DATA
    ]
    api.single_objective_values = single_objectives
    accepted_batches = [data["batch"] for data in TEST_DATA if data["accepted"]]
    api.accepted_batches = accepted_batches
    return api


def test_total_objective_values_from_api(api_mock):
    result = _total_objective_values_from_api(api_mock)
    expected = pd.DataFrame(TEST_DATA)
    assert expected.equals(result)


def test_single_objective_title(api_mock):
    api_mock.objective_function_names = ["npv"]
    result = _single_objective_title(api_mock)
    expected = "Objective function"
    assert result == expected

    api_mock.objective_function_names = ["npv", "rf"]
    result = _single_objective_title(api_mock)
    expected = "Weighted objective function"
    assert result == expected
