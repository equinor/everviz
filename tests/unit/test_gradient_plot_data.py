import os

import pytest
import pandas as pd

from everviz.util import get_everviz_folder
from everviz.pages.gradientplot import (
    _gradient_values,
    DataSources,
    _set_up_data_sources,
)


_DATA = [
    {"batch": 0, "function": "f1", "control": "c1", "value": 1},
    {"batch": 0, "function": "f1", "control": "c2", "value": 2},
    {"batch": 0, "function": "f2", "control": "c1", "value": 3},
    {"batch": 0, "function": "f2", "control": "c2", "value": 4},
    {"batch": 1, "function": "f1", "control": "c1", "value": 5},
    {"batch": 1, "function": "f1", "control": "c2", "value": 6},
    {"batch": 1, "function": "f2", "control": "c1", "value": 7},
    {"batch": 1, "function": "f2", "control": "c2", "value": 8},
]


@pytest.fixture
def mocked_api(mocker):
    api_mock = mocker.Mock()
    api_mock.output_folder = "everest_output"
    api_mock.gradient_values = _DATA
    return api_mock


def test_no_gradient_data(mocker):
    api_mock = mocker.Mock()
    api_mock.gradient_values = {}
    result = _gradient_values(api_mock)
    assert result is None


def test_gradient_data(mocker):
    api_mock = mocker.Mock()
    api_mock.gradient_values = _DATA
    result = _gradient_values(api_mock)
    expected = pd.DataFrame(_DATA)

    assert expected.equals(result)


def test_set_up_gradient_data_sources(tmpdir, mocked_api):
    expected = DataSources(
        gradient_values="everest_output/everviz/gradient_values.csv",
    )

    with tmpdir.as_cwd():
        for field in expected._fields:
            assert not os.path.exists(getattr(expected, field))

        get_everviz_folder(mocked_api)
        result = _set_up_data_sources(mocked_api)
        assert expected == result

        for field in result._fields:
            assert os.path.exists(getattr(result, field))
