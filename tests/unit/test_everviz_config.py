import os
import pytest

from everviz.config import webviz_config, write_webviz_config


def test_write_webviz_config(tmpdir):
    file_name = "everviz_webviz_config.yml"
    file_path = os.path.join("everviz", file_name)
    config = webviz_config()
    with tmpdir.as_cwd():
        assert not os.path.exists(file_path)
        write_webviz_config(config, file_path)
        assert os.path.exists(file_path)
