import os
import pytest
from everviz.util import get_everviz_folder


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
