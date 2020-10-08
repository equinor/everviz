from uuid import uuid4
from pathlib import Path
from itertools import cycle

import dash_html_components as html
import dash_core_components as dcc

import plotly.graph_objs as go
from plotly.colors import DEFAULT_PLOTLY_COLORS

from dash.dependencies import Output, Input
from everviz.data.load_csv.get_data import get_data
from everviz.plugins.plugin_abc import EvervizPluginABC
from everviz.util import base64encode


class SingleObjectivesPlot(EvervizPluginABC):
    """
    This webviz plugin is designed to display the single objective function
    calculated as the weighted sum of the objective functions from a multi
    objective everest optimisation.
    """

    def __init__(self, app, csv_file):
        super().__init__()

        self.graph_id = f"graph-{uuid4()}"
        self.div_id = f"div-{uuid4()}"
        self.function_dropdown_id = f"dropdown-{uuid4()}"
        self.csv_file = csv_file
        self.set_callbacks(app)

    def add_webvizstore(self):
        return [
            (get_data, [{"csv_file": self.csv_file}]),
        ]

    @property
    def layout(self):
        data = get_data(self.csv_file)
        exclude = ["batch", "accepted"]
        functions = [name for name in data.columns if name not in exclude]
        function_dropdown_options = [{"label": i, "value": i} for i in functions]
        func_elements = [
            html.Label("Functions to plot:"),
            dcc.Dropdown(
                id=self.function_dropdown_id,
                options=function_dropdown_options,
                multi=True,
                value=[functions[0]],
            ),
        ]
        return html.Div(
            [
                html.Div(
                    func_elements,
                    style={
                        "width": "29%",
                        "display": "inline-block",
                        "vertical-align": "top",
                    },
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id=self.graph_id,
                            config={
                                "displaylogo": False,
                                "toImageButtonOptions": {
                                    "filename": "single_objectives"
                                },
                            },
                        )
                    ],
                    id=self.div_id,
                    style={"width": "69%", "display": "inline-block"},
                ),
            ]
        )

    def set_callbacks(self, app):
        @app.callback(self.plugin_data_output, [self.plugin_data_requested])
        def user_download_data(data_requested):
            if data_requested:
                return {
                    "filename": Path(self.csv_file).name,
                    "content": base64encode(csv=get_data(self.csv_file).to_csv()),
                    "mime_type": "text/csv",
                }
            return None

        @app.callback(
            Output(self.graph_id, "figure"),
            [Input(self.function_dropdown_id, "value"), Input(self.div_id, "children")],
        )
        def update_graph(function_list, _):
            if function_list is None:
                return {}

            data = get_data(self.csv_file)
            accepted_data = data[data.accepted == 1]
            not_accepted_data = data[data.accepted == 0]

            colors = cycle(DEFAULT_PLOTLY_COLORS)
            traces = []
            for name, color in zip(function_list, colors):
                if name != "objective":
                    traces.append(
                        go.Scatter(
                            y=data[name],
                            x=data.batch,
                            mode="lines+markers",
                            marker={"color": color, "size": 10},
                            name=name,
                        ),
                    )
                else:
                    traces.extend(
                        [
                            go.Scatter(
                                y=accepted_data[name],
                                x=accepted_data.batch,
                                mode="lines+markers",
                                marker={"color": "blue", "size": 10},
                                name="accepted",
                            ),
                            go.Scatter(
                                y=not_accepted_data[name],
                                x=not_accepted_data.batch,
                                mode="markers",
                                marker={"color": "red", "size": 9},
                                name="rejected",
                            ),
                        ]
                    )

            return {
                "data": traces,
                "layout": dict(
                    xaxis={"title": "Batch", "tickformat": ",d"},
                    yaxis={"title": "Objective function value"},
                ),
            }
