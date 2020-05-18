import pandas as pd
from everviz.plugins.controls_plot.controls_plot import ControlsPlot


def test_control_plot_callback(app, dash_duo, mocker, caplog):
    test_data = [
        {"control": "c1", "batch": 0, "value": 0},
        {"control": "c2", "batch": 0, "value": 0},
        {"control": "c1", "batch": 1, "value": 42},
        {"control": "c2", "batch": 1, "value": 24},
    ]

    mocker.patch(
        "everviz.plugins.controls_plot.controls_plot.get_data",
        return_value=pd.DataFrame(test_data),
    )

    plugin = ControlsPlot(app, "dummy")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    # Test adding a control.
    dash_duo.select_dcc_dropdown("#{}".format(plugin.controls_dropdown_id), "c2")

    # Clear the dropdown, which should not cause an error. Call twice to
    # simulate two clear key presses.
    dash_duo.clear_input("#{}".format(plugin.controls_dropdown_id))
    dash_duo.clear_input("#{}".format(plugin.controls_dropdown_id))

    for record in caplog.records:
        assert record.levelname != "ERROR"
