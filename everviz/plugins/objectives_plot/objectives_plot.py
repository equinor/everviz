import os
import pkg_resources

import dash_html_components as html
import dash_core_components as dcc

import plotly.graph_objs as go
import plotly.express as px
from pathlib import Path
from uuid import uuid4
from dash.dependencies import Output, Input
from webviz_config import WebvizPluginABC
from webviz_config.webviz_assets import WEBVIZ_ASSETS
from everviz.data.load_csv.get_data import get_data


class ObjectivesPlot(WebvizPluginABC):
    def __init__(
        self,
        app,
        data_path,
        x_title="batch",
        y_title="value",
        title="Objective function values",
    ):
        super().__init__()
        self.title = title
        self.x_title = x_title
        self.y_title = y_title
        self.graph_id = f"graph-{uuid4()}"
        self.filter_box_id = f"dropdown-{uuid4()}"
        self.radio_id = f"dropdown-{uuid4()}"

        self.data_path = data_path
        self.set_callbacks(app)

        ASSETS_DIR = Path(pkg_resources.resource_filename("everviz", "assets"))

        WEBVIZ_ASSETS.add(ASSETS_DIR / "axis_customization.css")

    def add_webvizstore(self):
        return [(get_data, [{"data_path": self.data_path}])]

    @property
    def layout(self):
        radio_options = ["Statistics", "Data"]
        return html.Div(
            [
                html.H1(children=self.title, style={"textAlign": "center"}),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id=self.graph_id)],
                            style={"width": "99%", "display": "inline-block"},
                        ),
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id=self.radio_id,
                                    options=[
                                        {"label": i, "value": i} for i in radio_options
                                    ],
                                    value=radio_options[0],
                                    labelStyle={"display": "inline-block"},
                                ),
                            ],
                            style={"textAlign": "center"},
                        ),
                    ]
                ),
            ]
        )

    def set_callbacks(self, app):
        @app.callback(
            Output(self.graph_id, "figure"), [Input(self.radio_id, "value"),],
        )
        def update_graph(graph_type):
            df = get_data(self.data_path)
            traces = []
            if graph_type == "Statistics":
                for label in ["P10", "Mean", "P90"]:
                    fill = "tonexty" if label in ["P90", "Mean"] else None
                    traces.append(
                        go.Scatter(
                            y=df[label],
                            x=df[self.x_title],
                            name=label,
                            mode="lines",
                            marker={"size": 10},
                            fill=fill,
                            fillcolor="rgba(0,40,100,0.2)",
                        )
                    )
            else:
                traces.append(
                    go.Scatter(
                        y=df[self.y_title],
                        x=df[self.x_title],
                        mode="markers",
                        marker={"size": 10},
                    )
                )
            return {
                "data": traces,
                "layout": dict(
                    xaxis={"title": self.x_title.capitalize()},
                    yaxis={"title": self.y_title.capitalize()},
                ),
            }
