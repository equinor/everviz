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
        {"batch": 0, "objective": 100, "accepted": 1, "npv": 110, "rf": 130},
        {"batch": 1, "objective": 200, "accepted": 1, "npv": 210, "rf": 230},
        {"batch": 2, "objective": 200, "accepted": 0, "npv": 210, "rf": 230},
        {"batch": 3, "objective": 400, "accepted": 1, "npv": 410, "rf": 430},
        {"batch": 4, "objective": 300, "accepted": 0, "npv": 310, "rf": 330},
        {"batch": 5, "objective": 600, "accepted": 1, "npv": 610, "rf": 630},
        {"batch": 6, "objective": 400, "accepted": 0, "npv": 410, "rf": 430},
        {"batch": 7, "objective": 800, "accepted": 1, "npv": 810, "rf": 830},
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

    dash_duo.select_dcc_dropdown("#{}".format(plugin.function_dropdown_id), "npv")
    dash_duo.select_dcc_dropdown("#{}".format(plugin.function_dropdown_id), "rf")

    ref_image_path = os.path.join(
        everviz.__path__[0],
        "..",
        "test-data",
        "objectives",
        "single_objective_layout_headless.png",
    )
    ref_image = Image.open(ref_image_path)

    with tmpdir.as_cwd():
        time.sleep(10)
        dash_duo.driver.save_screenshot("example_snapshot.png")
        screen_shot = Image.open("example_snapshot.png")

    if screen_shot.size != ref_image.size:
        pytest.skip("Reference image size does not match {}".format(screen_shot.size))
    assert_equal_images(ref_image, screen_shot, threshold=1.0)

    dash_duo.clear_input("#{}".format(plugin.function_dropdown_id))

    for record in caplog.records:
        assert record.levelname != "ERROR"
