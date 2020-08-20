import os
import pytest
from everviz.util import get_everviz_folder, parse_range, get_placeholder_text


@pytest.fixture
def mocked_api(mocker):
    api_mock = mocker.Mock()
    api_mock.output_folder = "everest_output"
    return api_mock


def test_get_everviz_folder(tmpdir, mocked_api):
    everest_folder = "everest_output"
    expected_everviz_path = os.path.join(everest_folder, "everviz")
    with tmpdir.as_cwd():
        assert not os.path.exists(expected_everviz_path)
        everviz_path = get_everviz_folder(mocked_api)
        assert os.path.exists(everviz_path)
        assert expected_everviz_path == everviz_path


@pytest.mark.parametrize(
    "input_string, expected",
    [
        ("", set()),
        (" ", set()),
        ("1,2,3", {1, 2, 3}),
        ("1, 2 ,3", {1, 2, 3}),
        ("3,1,2", {1, 2, 3}),
        ("3,1,3", {1, 3}),
        ("1-3", {1, 2, 3}),
        ("1, 2-3", {1, 2, 3}),
        ("1, 1-3, 2", {1, 2, 3}),
        ("x", set()),
        ("1,2,x,3", {1, 2, 3}),
    ],
)
def test_object_parse_range(input_string, expected):
    assert parse_range(input_string) == expected


@pytest.mark.parametrize(
    "realizations, expected",
    [
        ([], "No realizations found"),
        ([1, 2, 3, 5], "example: 1, 5, 1-5"),
        ([0], "example: 0"),
    ],
)
def test_get_placeholder_text(realizations, expected):
    assert get_placeholder_text(realizations) == expected
