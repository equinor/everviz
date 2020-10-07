import pandas as pd
import everviz
from everviz.plugins.crossplot.crossplot_indexed import CrossplotIndexed


def test_crossplot_indexed_callback(app, dash_duo, monkeypatch, mocker, caplog):
    columns_names = ["a", "b", "c"]
    mock_data = pd.DataFrame(
        data=[[1, 2, 3]],
        columns=[f"{name}-{idx}" for idx, name in enumerate(columns_names)],
    )
    monkeypatch.setattr(
        everviz.plugins.crossplot.crossplot_indexed,
        "get_data",
        mocker.Mock(return_value=mock_data),
    )

    plugin = CrossplotIndexed(app, "a_data_file")
    app.layout = plugin.layout
    dash_duo.start_server(app)

    dropdown_x = dash_duo.find_element(f"#{plugin.dropdown_x_id}")
    dropdown_x.click()
    options_x = dropdown_x.find_element_by_css_selector("div.Select-menu-outer")
    assert columns_names == options_x.text.split("\n")
    dash_duo.clear_input("#{}".format(plugin.dropdown_x_id))

    dash_duo.click_at_coord_fractions(
        dash_duo.find_element(f"#{plugin.graph_id}"), 0, 0
    )

    dropdown_y = dash_duo.find_element(f"#{plugin.dropdown_y_id}")
    dropdown_y.click()
    options_y = dropdown_y.find_element_by_css_selector("div.Select-menu-outer")
    assert columns_names == options_y.text.split("\n")
    dash_duo.clear_input("#{}".format(plugin.dropdown_y_id))

    dash_duo.clear_input("#{}".format(plugin.dropdown_realization_id))

    for record in caplog.records:
        assert record.levelname != "ERROR"
