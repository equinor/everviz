import os
import everviz
from everviz.config import write_webviz_config, webviz_config
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
        everviz.pages.controls, "page_layout", mocker.Mock(return_value=""),
    )
    monkeypatch.setattr(
        everviz.pages.crossplot, "page_layout", mocker.Mock(return_value=""),
    )
    monkeypatch.setattr(
        everviz.pages.configuration, "page_layout", mocker.Mock(return_value=""),
    )
    monkeypatch.setattr(
        everviz.pages.objectives, "page_layout", mocker.Mock(return_value=""),
    )
    monkeypatch.setattr(
        everviz.pages.summary_values,
        "page_layout",
        mocker.Mock(return_value={"title": "Summary", "content": []}),
    )

    expected_config = {
        "title": "Everest Optimization Report",
        "pages": [
            {"title": "Everest", "content": [],},
            {"title": "Summary", "content": [],},
        ],
    }

    config = webviz_config(mocker.Mock())

    assert expected_config == config
