import pandas as pd
from everviz.plugins.gradient_plot import GradientPlot


_DATA = [
    {"batch": 0, "function": "f1", "control": "c1", "value": 1},
    {"batch": 0, "function": "f1", "control": "c2", "value": 2},
    {"batch": 0, "function": "f2", "control": "c1", "value": 3},
    {"batch": 0, "function": "f2", "control": "c2", "value": 4},
    {"batch": 1, "function": "f1", "control": "c1", "value": 5},
    {"batch": 1, "function": "f1", "control": "c2", "value": 6},
    {"batch": 1, "function": "f2", "control": "c1", "value": 7},
    {"batch": 1, "function": "f2", "control": "c2", "value": 8},
]


def test_gradient_plot_callback(app, dash_duo, mocker, caplog):
    mocker.patch(
        "everviz.plugins.gradient_plot.get_data",
        return_value=pd.DataFrame(_DATA),
    )

    plugin = GradientPlot(app, "dummy")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    # Test adding a function.
    dash_duo.select_dcc_dropdown("#{}".format(plugin.function_dropdown_id), "f2")

    # Clear the dropdown, which should not cause an error. Call twice to
    # simulate two clear key presses.
    dash_duo.clear_input("#{}".format(plugin.function_dropdown_id))
    dash_duo.clear_input("#{}".format(plugin.function_dropdown_id))

    # Test adding a batch
    dash_duo.select_dcc_dropdown("#{}".format(plugin.function_dropdown_id), "f2")
    dash_duo.select_dcc_dropdown("#{}".format(plugin.batch_dropdown_id), "1")

    # Clear the dropdown, which should not cause an error. Call twice to
    # simulate two clear key presses.
    dash_duo.clear_input("#{}".format(plugin.batch_dropdown_id))
    dash_duo.clear_input("#{}".format(plugin.batch_dropdown_id))

    # Test normalization radio.
    dash_duo.select_dcc_dropdown("#{}".format(plugin.batch_dropdown_id), "0")
    dash_duo.find_element(
        "#{} label:nth-child({})".format(plugin.normalization_radio_id, 2)
    ).click()
    dash_duo.find_element(
        "#{} label:nth-child({})".format(plugin.normalization_radio_id, 3)
    ).click()

    # Test abs check.
    dash_duo.find_element(
        "#{} label:nth-child({})".format(plugin.abs_check_id, 1)
    ).click()

    for record in caplog.records:
        assert record.levelname != "ERROR"
