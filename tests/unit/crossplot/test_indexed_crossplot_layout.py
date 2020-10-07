import os
import time
import dash
import pytest

import pandas as pd
from PIL import Image
import everviz
from everviz.plugins import CrossplotIndexed


def test_crossplot_layout(dash_duo, monkeypatch, mocker, tmpdir, assert_equal_images):
    app = dash.Dash(__name__)
    mock_data = pd.DataFrame(data=[[1, 2, 3], [1, 2, 3]], columns=["a", "b", "c"])
    monkeypatch.setattr(
        everviz.plugins.crossplot.crossplot_indexed,
        "get_data",
        mocker.Mock(return_value=mock_data),
    )
    monkeypatch.setattr(
        everviz.plugins.crossplot.crossplot_indexed.CrossplotIndexed,
        "set_callbacks",
        mocker.Mock(),
    )
    plugin = CrossplotIndexed(mocker.Mock(), "data_path")
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)

    _REFERENCE_IMAGES = {
        (1024, 768): "crossplot_indexed_layout_headless.png",
    }

    dash_duo.driver.set_window_size(1024, 768)
    with tmpdir.as_cwd():
        # Graph can be slow to load, so we need to ensure it has loaded.
        time.sleep(10)
        dash_duo.driver.save_screenshot("example_snapshot.png")
        snapshot = Image.open("example_snapshot.png")

    if not snapshot.size in _REFERENCE_IMAGES:
        pytest.skip("No reference image for layout size: {}".format(snapshot.size))

    reference_image = Image.open(
        os.path.join(
            everviz.__path__[0],
            "..",
            "test-data",
            "crossplot",
            _REFERENCE_IMAGES[snapshot.size],
        )
    )

    assert_equal_images(reference_image, snapshot, threshold=1.0)
