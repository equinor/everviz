from datetime import datetime

import pandas

from everviz.plugins.delta_plot.delta_plot import DeltaPlot
from everviz.pages.deltaplot import _get_summary_delta_values

_SUMMARY = {
    "realization": 3 * [1] + 3 * [2] + 3 * [1] + 3 * [2],
    "simulation": 3 * [1] + 3 * [2] + 3 * [1] + 3 * [2],
    "batch": [0] * 6 + [2] * 6,
    "date": 4
    * [
        datetime(2000, 1, 1).date().isoformat(),
        datetime(2000, 2, 1).date().isoformat(),
        datetime(2000, 3, 1).date().isoformat(),
    ],
    "key1": range(1, 13),
    "key2": range(10, 130, 10),
}

_EMPTY_SUMMARY = {"realization": [], "simulation": [], "date": [], "batch": []}


def test_summary_delta_plot_callback(app, dash_duo, mocker, caplog):
    mock_api = mocker.Mock()
    mock_api.summary_values.return_value = pandas.DataFrame(_SUMMARY)

    mocker.patch(
        "everviz.plugins.delta_plot.delta_plot.get_data",
        return_value=_get_summary_delta_values(mock_api, 2),
    )

    plugin = DeltaPlot(app, "values", "none")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    # Select an additional key>
    dash_duo.select_dcc_dropdown("#{}".format(plugin.key_dropdown_id), "key1")
    dash_duo.select_dcc_dropdown("#{}".format(plugin.key_dropdown_id), "key2")

    # Clear the key dropdown, which should not cause an error.
    dash_duo.clear_input("#{}".format(plugin.key_dropdown_id))
    dash_duo.clear_input("#{}".format(plugin.key_dropdown_id))

    # Add back a key.
    dash_duo.select_dcc_dropdown("#{}".format(plugin.key_dropdown_id), "key2")

    # Add a date.
    dash_duo.select_dcc_dropdown(
        "#{}".format(plugin.date_dropdown_id), datetime(2000, 2, 1).date().isoformat()
    )

    # Clear the date dropdown, which should not cause an error.
    dash_duo.clear_input("#{}".format(plugin.date_dropdown_id))
    dash_duo.clear_input("#{}".format(plugin.date_dropdown_id))

    for record in caplog.records:
        assert record.levelname != "ERROR"


def test_summary_delta_plot_empty_callback(app, dash_duo, mocker, caplog):
    mock_api = mocker.Mock()
    mock_api.summary_values.return_value = pandas.DataFrame(_EMPTY_SUMMARY)

    mocker.patch(
        "everviz.plugins.delta_plot.delta_plot.get_data",
        return_value=_get_summary_delta_values(mock_api, 2),
    )

    plugin = DeltaPlot(app, "values", "none")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    for record in caplog.records:
        assert record.levelname != "ERROR"
