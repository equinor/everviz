import os
from everviz.config import (
    create_everviz_folder,
    write_webviz_config,
)


def test_create_everviz_folder(tmpdir):
    everest_folder = "everest_output"
    expected_everviz_path = os.path.join(everest_folder, "everviz")
    with tmpdir.as_cwd():
        assert not os.path.exists(expected_everviz_path)
        everviz_path = create_everviz_folder(everest_folder)
        assert os.path.exists(everviz_path)
        assert expected_everviz_path == everviz_path


def test_write_webviz_config(tmpdir):
    file_name = "everviz_webviz_config.yml"
    config = {}
    with tmpdir.as_cwd():
        assert not os.path.exists(file_name)
        write_webviz_config(config, file_name)
        assert os.path.exists(file_name)
