from datetime import datetime

import pandas as pd
import pytest

from everviz.plugins.summary_plot.wells_plot import WellsPlot, _get_target_keys
from everviz.pages.summary_values import _summary_values


def test_well_plot(app, dash_duo, mocker, caplog):
    test_data = {
        "realization": range(12),
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
        "WOPR:OP1": range(1, 13),
        "WOPRT:OP1": range(10, 130, 10),
    }

    mocker.patch(
        "everviz.plugins.summary_plot.wells_plot.get_data",
        return_value=_summary_values(pd.DataFrame(test_data)),
    )

    plugin = WellsPlot(app, "values")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    # Tests warning label not there
    dash_duo.wait_for_contains_text(f"#{plugin.label_id}", "")

    dash_duo.clear_input("#{}".format(plugin.dropdown_key))
    dash_duo.select_dcc_dropdown("#{}".format(plugin.dropdown_key), "WOPR:OP1")
    result = dash_duo.find_element("#{}".format(plugin.dropdown_key)).text.split()[0]
    dash_duo.find_element(
        "#{} label:nth-child({})".format(plugin.radio_statistics, 2)
    ).click()

    # Tests warning label is there
    dash_duo.wait_for_contains_text(f"#{plugin.label_id}", "Statistics are calculated")

    for record in caplog.records:
        assert record.levelname != "ERROR"


@pytest.mark.parametrize(
    "summary_keys, expected",
    (
        (["WOPR:OP1"], ["WOPRT:OP1"]),
        (["WOPR:OP2"], []),
        (["WOPR:OP1", "WOPR:OP2", "WWIR:IN1"], ["WOPRT:OP1", "WWIRT:IN1"]),
    ),
)
def test_get_target_keys(summary_keys, expected):
    df = pd.DataFrame(columns=["WOPRT:OP1", "WWIRT:IN1"])
    assert _get_target_keys(df, summary_keys) == expected
