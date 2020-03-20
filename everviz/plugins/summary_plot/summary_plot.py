from pathlib import Path
import pkg_resources
from uuid import uuid4
from collections import deque

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input

import plotly.graph_objs as go
from plotly.colors import DEFAULT_PLOTLY_COLORS

from webviz_config import WebvizPluginABC
from everviz.data.load_csv.get_data import get_data
from webviz_config.webviz_assets import WEBVIZ_ASSETS


class SummaryPlot(WebvizPluginABC):
    def __init__(self, app, csv_file, xaxis="date"):
        super().__init__()
        self.xaxis = xaxis
        self.graph_id = f"graph-{uuid4()}"
        self.key_dropdown_id = f"dropdown-{uuid4()}"
        self.xaxis_dropdown_id = f"dropdown-{uuid4()}"
        self.csv_file = csv_file
        self.set_callbacks(app)

        ASSETS_DIR = pkg_resources.resource_filename("everviz", "assets")
        WEBVIZ_ASSETS.add(Path(ASSETS_DIR) / "axis_customization.css")

    def add_webvizstore(self):
        return [(get_data, [{"csv_file": self.csv_file}])]

    @property
    def layout(self):
        data = get_data(self.csv_file)
        key_dropdown_options = [
            {"label": i, "value": i} for i in list(data["Summary Key"].unique())
        ]
        xaxis_dropdown_options = [
            {"label": i, "value": i}
            for i in list(data["Batch" if self.xaxis == "date" else "Date"].unique())
        ]
        xaxis_dropdown_title = (
            "Batches to plot" if self.xaxis == "date" else "Dates to plot"
        )
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Keywords to plot:"),
                                dcc.Dropdown(
                                    id=self.key_dropdown_id,
                                    options=key_dropdown_options,
                                    multi=True,
                                ),
                                html.Label(
                                    xaxis_dropdown_title, style={"margin-top": 24}
                                ),
                                dcc.Dropdown(
                                    id=self.xaxis_dropdown_id,
                                    options=xaxis_dropdown_options,
                                    multi=True,
                                    value=[xaxis_dropdown_options[0]["value"]],
                                ),
                            ],
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
            [
                Input(self.key_dropdown_id, "value"),
                Input(self.xaxis_dropdown_id, "value"),
            ],
        )
        def update_graph(key_list, line_list):
            # The key_list arguments is the list of keys to plot. The line_list
            # argument is a list of batches, or a list of dates to plot for
            # those keys.
            if key_list is None or line_list is None:
                return {}

            # Get the data, setting its index.
            data = get_data(self.csv_file).set_index(["Summary Key", "Batch", "Date"])

            # Put the the standard colors in a deque that we will rotate.
            colors = deque(DEFAULT_PLOTLY_COLORS)

            # Choose between dates or batches on the xaxis.
            line_key = "Batch" if self.xaxis == "date" else "Date"
            xaxis_key = "Date" if self.xaxis == "date" else "Batch"

            traces = []
            for key in key_list:
                # Select all rows belonging to the current key.
                key_data = data.xs(key, level="Summary Key", drop_level=True)

                for line in line_list:
                    # Select all rows belonging the current batch or date.
                    line_data = key_data.xs(
                        line, level=line_key, drop_level=True
                    ).reset_index()

                    # Set the name of the plotted line.
                    name = f"{key}"
                    if len(line_list) > 1:
                        name += f", {line_key}:{line}"

                    # Make the traces, with mean, P10 and P90, shading in between.
                    traces.extend(
                        [
                            go.Scatter(
                                y=line_data["P90"],
                                x=line_data[xaxis_key],
                                mode="lines",
                                marker={"size": 10},
                                line={"color": colors[0]},
                                name=name + "(P90)",
                                showlegend=False,
                            ),
                            go.Scatter(
                                y=line_data["P10"],
                                x=line_data[xaxis_key],
                                mode="lines",
                                line={"color": colors[0]},
                                marker={"size": 10},
                                fill="tonexty",
                                name=name + "(P10)",
                                showlegend=False,
                            ),
                            go.Scatter(
                                y=line_data["Mean"],
                                x=line_data[xaxis_key],
                                mode="lines",
                                marker={"size": 10},
                                line={"color": colors[0]},
                                name=name,
                                showlegend=True,
                            ),
                        ]
                    )

                    # Cycle trough the default colors.
                    colors.rotate(-1)
            return {"data": traces}
