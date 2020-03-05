import dash
import dash_html_components as html
from everviz.plugins._lineplot_plugin._layout._lineplot_layout import _get_layout


def test_lineplot_layout(dash_duo):
    app = dash.Dash(__name__)
    layout = _get_layout(
        "title", "graph_id", (1, 2, 3), [4, 5, 6], "x-axis-label", "y-axis-label"
    )
    app.layout = html.Div(layout)
    dash_duo.start_server(app)
    figure_text = dash_duo.find_element("#graph_id").text

    assert "1" in figure_text
    assert "6" in figure_text
    assert "x-axis-label" in figure_text
    assert "y-axis-label" in figure_text
