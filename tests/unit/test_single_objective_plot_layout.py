import time
import os
import pytest

import pandas as pd
from PIL import Image

import everviz
from everviz.plugins.objectives_plot.single_objectives_plot import SingleObjectivesPlot


def test_single_objective_plot_layout(
    app, dash_duo, mocker, caplog, tmpdir, assert_equal_images
):
    test_data = [
        {"batch": 0, "value": 100, "accepted": True},
        {"batch": 1, "value": 200, "accepted": True},
        {"batch": 2, "value": 200, "accepted": False},
        {"batch": 3, "value": 400, "accepted": True},
        {"batch": 4, "value": 300, "accepted": False},
        {"batch": 5, "value": 600, "accepted": False},
        {"batch": 6, "value": 400, "accepted": True},
        {"batch": 7, "value": 800, "accepted": True},
    ]

    def mock_get_data(_):
        return pd.DataFrame(test_data)

    mocker.patch(
        "everviz.plugins.objectives_plot.single_objectives_plot.get_data",
        side_effect=mock_get_data,
    )

    plugin = SingleObjectivesPlot(app, "csv_data_file")
    app.layout = plugin.layout
    dash_duo.driver.set_window_size(1024, 768)
    dash_duo.start_server(app)

    reference_image = Image.open(
        os.path.join(
            everviz.__path__[0],
            "..",
            "test-data",
            "objectives",
            "single_objective_layout_headless.png",
        )
    )

    with tmpdir.as_cwd():
        time.sleep(1)
        dash_duo.driver.save_screenshot("example_snapshot.png")
        screen_shot = Image.open("example_snapshot.png")

    if screen_shot.size != reference_image.size:
        pytest.skip("Reference image size does not match {}".format(screen_shot.size))
    assert_equal_images(reference_image, screen_shot, threshold=0.5)

    for record in caplog.records:
        assert record.levelname != "ERROR"
