import pandas as pd
from everviz.plugins.objectives_plot.objectives_plot import ObjectivesPlot
from everviz.pages.objectives import _objective_values, _objective_statistics


def test_objective_plot_callback(app, dash_duo, mocker, caplog):
    test_data = [
        {"batch": 0, "realization": 1, "function": "f0", "value": 100, "simulation": 0},
        {"batch": 0, "realization": 1, "function": "f1", "value": 200, "simulation": 1},
        {"batch": 2, "realization": 2, "function": "f0", "value": 200, "simulation": 2},
        {"batch": 2, "realization": 2, "function": "f1", "value": 400, "simulation": 3},
        {"batch": 0, "realization": 3, "function": "f0", "value": 300, "simulation": 4},
        {"batch": 0, "realization": 3, "function": "f1", "value": 600, "simulation": 5},
        {"batch": 2, "realization": 4, "function": "f0", "value": 400, "simulation": 6},
        {"batch": 2, "realization": 4, "function": "f1", "value": 800, "simulation": 7},
    ]

    def mock_get_data(data_type):
        if data_type == "values":
            result = _objective_values(pd.DataFrame(test_data))
        else:
            result = _objective_statistics(pd.DataFrame(test_data))
        return result

    mocker.patch(
        "everviz.plugins.objectives_plot.objectives_plot.get_data",
        side_effect=mock_get_data,
    )

    plugin = ObjectivesPlot(app, "values", "statistics")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    # Test statistics plot.
    dash_duo.select_dcc_dropdown("#{}".format(plugin.function_dropdown_id), "f1")

    # Test data plot.
    dash_duo.find_element("#{} label:nth-child({})".format(plugin.radio_id, 2)).click()

    # Clear the dropdown, which should not cause an error.
    dash_duo.clear_input("#{}".format(plugin.function_dropdown_id))

    for record in caplog.records:
        assert record.levelname != "ERROR"
