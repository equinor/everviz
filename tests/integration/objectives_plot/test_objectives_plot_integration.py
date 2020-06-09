import pandas as pd
from everviz.plugins.objectives_plot.objectives_plot import ObjectivesPlot
from everviz.pages.objectives import _objective_values
from everviz.plugins.objectives_plot.util import calculate_statistics


def test_objective_plot_callback(app, dash_duo, mocker, caplog):
    test_data = [
        {"batch": 0, "realization": 1, "function": "f0", "value": 100, "simulation": 1},
        {"batch": 0, "realization": 1, "function": "f1", "value": 200, "simulation": 1},
        {"batch": 2, "realization": 1, "function": "f0", "value": 300, "simulation": 1},
        {"batch": 2, "realization": 1, "function": "f1", "value": 400, "simulation": 1},
        {"batch": 0, "realization": 2, "function": "f0", "value": 500, "simulation": 2},
        {"batch": 0, "realization": 2, "function": "f1", "value": 600, "simulation": 2},
        {"batch": 2, "realization": 2, "function": "f0", "value": 700, "simulation": 2},
        {"batch": 2, "realization": 2, "function": "f1", "value": 800, "simulation": 2},
    ]

    def mock_get_data(data_type):
        result = _objective_values(pd.DataFrame(test_data))
        if data_type == "Statistics":
            result = calculate_statistics(result)
        return result

    mocker.patch(
        "everviz.plugins.objectives_plot.objectives_plot.get_data",
        side_effect=mock_get_data,
    )

    plugin = ObjectivesPlot(app, "values")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    # Test statistics plot.
    dash_duo.find_element("#{} label:nth-child({})".format(plugin.radio_id, 1)).click()
    dash_duo.select_dcc_dropdown("#{}".format(plugin.function_dropdown_id), "f1")

    # Test data plot.
    dash_duo.find_element("#{} label:nth-child({})".format(plugin.radio_id, 2)).click()

    # Test filtering realizations.
    dash_duo.find_element(
        "#{} label:nth-child({})".format(plugin.realization_filter_check_id, 1)
    ).click()
    dash_duo.find_element("#{}".format(plugin.realization_filter_input_id)).send_keys(
        "1, 3"
    )

    # Clear the dropdown, which should not cause an error.
    dash_duo.clear_input("#{}".format(plugin.function_dropdown_id))

    for record in caplog.records:
        assert record.levelname != "ERROR"
