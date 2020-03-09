import dash
import dash_html_components as html

from everviz.plugins.crossplot.set_up_assets import set_up_assets


def test_set_up_assets(dash_duo):

    app = dash.Dash(__name__)
    app.layout = html.Div([])
    dash_duo.start_server(app)

    # Trying to set up an asset twice will fail
    # if we don't account for it
    set_up_assets(app, "A_DIR")
    set_up_assets(app, "A_DIR")
