from uuid import uuid4
from pathlib import Path
from itertools import cycle
import pkg_resources

import dash_html_components as html
import dash_core_components as dcc

import plotly.graph_objs as go
from plotly.colors import DEFAULT_PLOTLY_COLORS

from dash.dependencies import Output, Input
from webviz_config import WebvizPluginABC
from webviz_config.webviz_assets import WEBVIZ_ASSETS
from everviz.data.load_csv.get_data import get_data


class ObjectivesPlot(WebvizPluginABC):
    def __init__(self, app, values_file, statistics_file):
        super().__init__()

        self.graph_id = f"graph-{uuid4()}"
        self.radio_id = f"dropdown-{uuid4()}"
        self.function_dropdown_id = f"dropdown-{uuid4()}"

        self.values_file = values_file
        self.statistics_file = statistics_file
        self.set_callbacks(app)

        ASSETS_DIR = Path(pkg_resources.resource_filename("everviz", "assets"))
        WEBVIZ_ASSETS.add(ASSETS_DIR / "axis_customization.css")

    def add_webvizstore(self):
        return [
            (get_data, [{"values_file": self.values_file}]),
            (get_data, [{"statistics_file": self.statistics_file}]),
        ]

    @property
    def layout(self):
        data = get_data(self.statistics_file)

        functions = data["function"].unique()
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

        radio_options = ["Statistics", "Data"]
        radio_elements = [
            dcc.RadioItems(
                id=self.radio_id,
                options=[{"label": i, "value": i} for i in radio_options],
                value=radio_options[0],
                labelStyle={"display": "inline-block"},
                style={"margin-top": 20},
            )
        ]

        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            func_elements + radio_elements,
                            style={
                                "width": "29%",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                        html.Div(
                            [dcc.Graph(id=self.graph_id)],
                            style={"width": "69%", "display": "inline-block"},
                        ),
                    ]
                ),
            ]
        )

    def set_callbacks(self, app):
        @app.callback(
            Output(self.graph_id, "figure"),
            [Input(self.function_dropdown_id, "value"), Input(self.radio_id, "value"),],
        )
        def update_graph(func_list, radio_value):
            # # The key_list arguments is the list of functions to plot.
            if func_list is None:
                return {}

            # # Get the data, setting its index.
            if radio_value == "Statistics":
                data = get_data(self.statistics_file).set_index("function")
            else:
                data = get_data(self.values_file).set_index("function")

            # Make a cycle iterator over the plotly colors.
            colors = cycle(DEFAULT_PLOTLY_COLORS)

            traces = []
            for color, key in zip(colors, func_list):
                # Select all data belonging to the current key.
                func_data = data.xs(key)

                # Make the traces, with mean, P10 and P90, shading in between.
                if radio_value == "Statistics":
                    traces.extend(
                        [
                            go.Scatter(
                                y=func_data["P90"],
                                x=func_data["batch"],
                                mode="lines",
                                marker={"size": 10},
                                line={"color": color},
                                name=key + "(P90)",
                                showlegend=False,
                            ),
                            go.Scatter(
                                y=func_data["P10"],
                                x=func_data["batch"],
                                mode="lines",
                                line={"color": color},
                                marker={"size": 10},
                                fill="tonexty",
                                name=key + "(P10)",
                                showlegend=False,
                            ),
                            go.Scatter(
                                y=func_data["Mean"],
                                x=func_data["batch"],
                                mode="lines",
                                marker={"size": 10},
                                line={"color": color},
                                name=key,
                                showlegend=True,
                            ),
                        ]
                    )
                else:
                    traces.append(
                        go.Scatter(
                            y=func_data["value"],
                            x=func_data["batch"],
                            mode="markers",
                            marker={"size": 10},
                            name=key,
                            showlegend=True,
                        )
                    )

            return {
                "data": traces,
                "layout": dict(
                    xaxis={"title": "Batch"}, yaxis={"title": "Function Key Value"},
                ),
            }
