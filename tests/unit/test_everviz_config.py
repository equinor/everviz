import os

from everviz.config import write_webviz_config
from everviz.util import DEFAULT_CONFIG


def test_write_webviz_config(tmpdir):
    file_name = DEFAULT_CONFIG
    config = {}
    with tmpdir.as_cwd():
        assert not os.path.exists(file_name)
        write_webviz_config(config, file_name)
        assert os.path.exists(file_name)
