from uuid import uuid4
from pathlib import Path
import pkg_resources

import dash_html_components as html
import dash_core_components as dcc

import plotly.graph_objs as go

from dash.dependencies import Output, Input
from webviz_config import WebvizPluginABC
from webviz_config.webviz_assets import WEBVIZ_ASSETS
from everviz.data.load_csv.get_data import get_data


class SingleObjectivesPlot(WebvizPluginABC):
    """
    This webviz plugin is designed to display the single objective function
    calculated as the weighted sum of the objective functions from a multi
    objective everest optimisation.
    """

    def __init__(self, app, csv_file):
        super().__init__()

        self.graph_id = f"graph-{uuid4()}"
        self.div_id = f"div-{uuid4()}"

        self.csv_file = csv_file
        self.set_callbacks(app)

        ASSETS_DIR = Path(pkg_resources.resource_filename("everviz", "assets"))
        WEBVIZ_ASSETS.add(ASSETS_DIR / "axis_customization.css")

    def add_webvizstore(self):
        return [
            (get_data, [{"csv_file": self.csv_file}]),
        ]

    @property
    def layout(self):
        return html.Div(
            [dcc.Graph(id=self.graph_id)],
            id=self.div_id,
            style={"width": "69%", "display": "inline-block"},
        )

    def set_callbacks(self, app):
        @app.callback(self.plugin_data_output, [self.plugin_data_requested])
        def user_download_data(data_requested):
            if data_requested:
                return WebvizPluginABC.plugin_data_compress(
                    [
                        {
                            "filename": Path(self.csv_file).name,
                            "content": get_data(self.csv_file).to_csv(),
                        }
                    ]
                )
            return ""

        @app.callback(
            Output(self.graph_id, "figure"), [Input(self.div_id, "children")],
        )
        def update_graph(_):
            data = get_data(self.csv_file)
            accepted_data = data[data.accepted == True]  # pylint: disable=C0121
            not_accepted_data = data[data.accepted == False]  # pylint: disable=C0121
            traces = [
                go.Scatter(
                    y=accepted_data.value,
                    x=accepted_data.batch,
                    mode="lines+markers",
                    marker={"color": "blue", "size": 10},
                    name="accepted",
                ),
                go.Scatter(
                    y=not_accepted_data.value,
                    x=not_accepted_data.batch,
                    mode="markers",
                    marker={"color": "red", "size": 9},
                    name="not accepted",
                ),
            ]

            return {
                "data": traces,
                "layout": dict(
                    xaxis={"title": "Batch"},
                    yaxis={"title": "Objection function value"},
                ),
            }
