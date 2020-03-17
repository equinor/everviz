import os
import numpy as np
import pandas as pd
import pytest
from everviz.config import (
    write_webviz_config,
    _get_everviz_folder,
    _write_to_csv,
    _set_up_data_sources,
    webviz_config,
    DataSources,
)


@pytest.fixture
def mocked_api(mocker):
    api_mock = mocker.Mock()
    api_mock.output_folder.return_value = "everest_output"
    api_mock.control_values = [
        {"control": "c1", "batch": 0, "value": 12},
        {"control": "c1", "batch": 1, "value": 30},
    ]
    api_mock.objective_values = [
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
    ]
    return api_mock


def test_create_everviz_folder(tmpdir):
    everest_folder = "everest_output"
    expected_everviz_path = os.path.join(everest_folder, "everviz")
    with tmpdir.as_cwd():
        assert not os.path.exists(expected_everviz_path)
        everviz_path = _get_everviz_folder(everest_folder)
        assert os.path.exists(everviz_path)
        assert expected_everviz_path == everviz_path


def test_write_to_csv(tmpdir):
    expected_df = pd.DataFrame(np.random.randint(0, 10, (4, 4)), columns=list("ABCD"))
    with tmpdir.as_cwd():
        file_name = "test_data.csv"
        assert not os.path.exists(file_name)
        returned_file_name = _write_to_csv(expected_df, file_name)
        assert os.path.exists(returned_file_name)
        assert returned_file_name == file_name
        df = pd.read_csv(returned_file_name)
        assert expected_df.equals(df)


def test_write_webviz_config(tmpdir):
    file_name = "everviz_webviz_config.yml"
    config = {}
    with tmpdir.as_cwd():
        assert not os.path.exists(file_name)
        write_webviz_config(config, file_name)
        assert os.path.exists(file_name)


def test_set_up_data_sources(tmpdir, mocked_api):
    expected = DataSources(
        controls_per_batch="everest_output/everviz/controls_per_batch.csv",
        controls_initial_vs_best="everest_output/everviz/controls_initial_vs_best.csv",
    )

    with tmpdir.as_cwd():
        for field in expected._fields:
            assert not os.path.exists(getattr(expected, field))

        result = _set_up_data_sources(mocked_api)
        assert expected == result

        for field in result._fields:
            assert os.path.exists(getattr(result, field))


def test_webviz_config(tmpdir, mocked_api):
    expected = {
        "title": "Everest Optimization Report",
        "pages": [
            {"title": "Everest", "content": []},
            {
                "title": "Controls",
                "content": [
                    "## Control value per batch",
                    {
                        "TablePlotter": {
                            "lock": True,
                            "csv_file": "everest_output/everviz/controls_per_batch.csv",
                            "filter_cols": ["control"],
                            "plot_options": {
                                "x": "batch",
                                "y": "value",
                                "type": "line",
                                "color": "control",
                            },
                        }
                    },
                    "## Initial controls versus best controls",
                    {
                        "TablePlotter": {
                            "lock": True,
                            "csv_file": "everest_output/everviz/controls_initial_vs_best.csv",
                            "plot_options": {
                                "x": "control",
                                "y": "value",
                                "type": "scatter",
                                "color": "batch",
                            },
                        }
                    },
                ],
            },
        ],
    }
    with tmpdir.as_cwd():
        assert expected == webviz_config(mocked_api)
