import os
import everviz
from everviz.config import (
    write_webviz_config,
    webviz_config,
    setup_default_everviz_config,
)
from everviz.util import DEFAULT_CONFIG


def test_write_webviz_config(tmpdir):
    file_name = DEFAULT_CONFIG
    config = {}
    with tmpdir.as_cwd():
        assert not os.path.exists(file_name)
        write_webviz_config(config, file_name)
        assert os.path.exists(file_name)


def test_webviz_config(mocker, monkeypatch):
    monkeypatch.setattr(
        everviz.pages.controls,
        "page_layout",
        mocker.Mock(return_value=""),
    )
    monkeypatch.setattr(
        everviz.pages.crossplot,
        "page_layout",
        mocker.Mock(return_value=""),
    )
    monkeypatch.setattr(
        everviz.pages.configuration,
        "page_layout",
        mocker.Mock(return_value=""),
    )
    monkeypatch.setattr(
        everviz.pages.objectives,
        "page_layout",
        mocker.Mock(return_value=""),
    )
    monkeypatch.setattr(
        everviz.pages.deltaplot,
        "page_layout",
        mocker.Mock(return_value=""),
    )
    monkeypatch.setattr(
        everviz.pages.summary_values,
        "page_layout",
        mocker.Mock(return_value={"title": "Summary", "content": []}),
    )
    monkeypatch.setattr(
        everviz.pages.wells_values,
        "page_layout",
        mocker.Mock(return_value={}),
    )

    expected_config = {
        "title": "Everest Optimization Report",
        "pages": [
            {
                "title": "Everest",
                "content": [],
            },
            {
                "title": "Summary",
                "content": [],
            },
        ],
    }

    config = webviz_config(mocker.Mock())

    assert expected_config == config


def test_setup_default_everviz_config(mocker, monkeypatch, tmpdir):
    monkeypatch.setattr(
        everviz.config,
        "webviz_config",
        mocker.Mock(
            return_value={
                "title": "Everest Optimization Report",
                "pages": [],
            }
        ),
    )

    api_mock = mocker.Mock()
    api_mock.output_folder = "everest_output"
    expected_result = os.path.join(api_mock.output_folder, "everviz", DEFAULT_CONFIG)

    with tmpdir.as_cwd():
        assert not os.path.exists(expected_result)
        result = setup_default_everviz_config(api_mock)
        assert os.path.exists(expected_result)
        assert expected_result == result
