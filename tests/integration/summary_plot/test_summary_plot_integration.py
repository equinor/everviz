from datetime import datetime
import pandas as pd
from everviz.plugins.summary_plot.summary_plot import SummaryPlot
from everviz.pages.summary_values import _summary_values, _summary_statistics


def test_summary_plot_callback(app, dash_duo, mocker, caplog):
    test_data = {
        "simulation": range(12),
        "batch": [0] * 6 + [1] * 6,
        "date": [
            datetime(2000, 1, 1),
            datetime(2000, 2, 1),
            datetime(2000, 3, 1),
            datetime(2000, 1, 1),
            datetime(2000, 2, 1),
            datetime(2000, 3, 1),
            datetime(2000, 1, 1),
            datetime(2000, 2, 1),
            datetime(2000, 3, 1),
            datetime(2000, 1, 1),
            datetime(2000, 2, 1),
            datetime(2000, 3, 1),
        ],
        "key1": range(1, 13),
        "key2": range(10, 130, 10),
    }

    def mock_get_data(data_type):
        if data_type == "values":
            result = _summary_values(pd.DataFrame(test_data))
        else:
            result = _summary_statistics(pd.DataFrame(test_data))
        return result

    mocker.patch(
        "everviz.plugins.summary_plot.summary_plot.get_data", side_effect=mock_get_data,
    )

    plugin = SummaryPlot(app, "values", "statistics")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    # Test statistics plot.
    dash_duo.select_dcc_dropdown("#{}".format(plugin.key_dropdown_id), "key1")

    # Test data plot.
    dash_duo.find_element("#{} label:nth-child({})".format(plugin.radio_id, 2)).click()

    # Clear the axes dropdowns, which should not cause an error.
    #
    # NOTE: if you try to do this before the previous click action on a radio
    # button, you get an error, because the the dropdown stays open and overlaps
    # with the radio buttons.
    dash_duo.clear_input("#{}".format(plugin.xaxis_dropdown_id))
    dash_duo.clear_input("#{}".format(plugin.key_dropdown_id))

    for record in caplog.records:
        assert record.levelname != "ERROR"
