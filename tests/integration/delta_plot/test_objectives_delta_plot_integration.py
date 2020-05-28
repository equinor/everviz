from everviz.plugins.delta_plot.delta_plot import DeltaPlot
from everviz.pages.deltaplot import _get_objective_delta_values

_OBJECTIVES = [
    {"batch": 0, "realization": 1, "function": "f0", "value": 100, "simulation": 1},
    {"batch": 0, "realization": 2, "function": "f0", "value": 200, "simulation": 2},
    {"batch": 0, "realization": 1, "function": "f1", "value": 300, "simulation": 1},
    {"batch": 0, "realization": 2, "function": "f1", "value": 400, "simulation": 2},
    {"batch": 2, "realization": 1, "function": "f0", "value": 500, "simulation": 1},
    {"batch": 2, "realization": 2, "function": "f0", "value": 600, "simulation": 2},
    {"batch": 2, "realization": 1, "function": "f1", "value": 800, "simulation": 1},
    {"batch": 2, "realization": 2, "function": "f1", "value": 900, "simulation": 2},
]


def test_objective_delta_plot_callback(app, dash_duo, mocker, caplog):
    mock_api = mocker.Mock()
    mock_api.objective_values = _OBJECTIVES
    mocker.patch(
        "everviz.plugins.delta_plot.delta_plot.get_data",
        return_value=_get_objective_delta_values(mock_api, 2),
    )

    plugin = DeltaPlot(app, "values", "first")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    # Select an additional key>
    dash_duo.select_dcc_dropdown("#{}".format(plugin.key_dropdown_id), "f1")

    # Clear the dropdown, which should not cause an error.
    dash_duo.clear_input("#{}".format(plugin.key_dropdown_id))
    dash_duo.clear_input("#{}".format(plugin.key_dropdown_id))

    for record in caplog.records:
        assert record.levelname != "ERROR"
