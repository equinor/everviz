import pandas as pd
import everviz
from everviz.plugins.crossplot.crossplot_indexed import CrossplotIndexed


def test_crossplot_indexed_callback(app, dash_duo, monkeypatch, mocker, caplog):
    mock_data = pd.DataFrame(data=[[1, 2, 3]], columns=["a", "b", "c"])
    monkeypatch.setattr(
        everviz.plugins.crossplot.crossplot_indexed,
        "get_data",
        mocker.Mock(return_value=mock_data),
    )

    plugin = CrossplotIndexed(app, "a_data_file")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    dash_duo.clear_input("#{}".format(plugin.dropdown_x_id))

    for record in caplog.records:
        assert record.levelname != "ERROR"
