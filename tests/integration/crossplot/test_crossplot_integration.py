import pandas as pd
import everviz
from everviz.plugins.crossplot.crossplot import Crossplot


def test_crossplot_callback(app, dash_duo, monkeypatch, mocker, caplog):
    mock_data = pd.DataFrame(data=[[1, 2, 3]], columns=["a", "b", "c"])
    monkeypatch.setattr(
        everviz.plugins.crossplot.crossplot,
        "get_data",
        mocker.Mock(return_value=mock_data),
    )

    plugin = Crossplot(app, "a_data_file")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    dash_duo.clear_input("#{}".format(plugin.keys_x_id))
    for record in caplog.records:
        assert record.levelname != "ERROR"
