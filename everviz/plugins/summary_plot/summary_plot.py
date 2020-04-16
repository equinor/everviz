from pathlib import Path
from uuid import uuid4
from itertools import cycle
import pkg_resources

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input

import plotly.graph_objs as go
from plotly.colors import DEFAULT_PLOTLY_COLORS

from webviz_config import WebvizPluginABC
from webviz_config.webviz_assets import WEBVIZ_ASSETS
from everviz.data.load_csv.get_data import get_data


class SummaryPlot(WebvizPluginABC):
    def __init__(self, app, values_file, statistics_file, xaxis="date"):
        super().__init__()

        self.graph_id = f"graph-{uuid4()}"
        self.key_dropdown_id = f"dropdown-{uuid4()}"
        self.xaxis_dropdown_id = f"dropdown-{uuid4()}"
        self.radio_id = f"radio-{uuid4()}"

        self.values_file = values_file
        self.statistics_file = statistics_file
        self.xaxis = xaxis

        self.set_callbacks(app)

        ASSETS_DIR = pkg_resources.resource_filename("everviz", "assets")
        WEBVIZ_ASSETS.add(Path(ASSETS_DIR) / "axis_customization.css")

    def add_webvizstore(self):
        return [
            (get_data, [{"values_file": self.values_file}]),
            (get_data, [{"statistics_file": self.statistics_file}]),
        ]

    @property
    def layout(self):
        radio_options = ["Statistics", "Data"]
        data = get_data(self.statistics_file)
        key_dropdown_options = [
            {"label": i, "value": i} for i in list(data["summary_key"].unique())
        ]
        xaxis_dropdown_options = [
            {"label": i, "value": i}
            for i in list(data["batch" if self.xaxis == "date" else "date"].unique())
        ]
        xaxis_dropdown_title = (
            "Batches to plot" if self.xaxis == "date" else "Dates to plot"
        )

        # Keywords dropdown.
        keyword_elements = [
            html.Label("Keywords to plot:"),
            dcc.Dropdown(
                id=self.key_dropdown_id, options=key_dropdown_options, multi=True,
            ),
        ]

        # X-axis dropdown.
        xaxis_elements = [
            html.Label(xaxis_dropdown_title, style={"margin-top": 24}),
            dcc.Dropdown(
                id=self.xaxis_dropdown_id,
                options=xaxis_dropdown_options,
                multi=True,
                value=[xaxis_dropdown_options[0]["value"]],
            ),
        ]

        # Radio for switching between data and statistics.
        radio_elements = [
            dcc.RadioItems(
                id=self.radio_id,
                options=[{"label": i, "value": i} for i in radio_options],
                value=radio_options[0],
                labelStyle={"display": "inline-block"},
                style={"margin-top": 20},
            ),
        ]
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            keyword_elements + xaxis_elements + radio_elements,
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
                Input(self.radio_id, "value"),
            ],
        )
        def update_graph(key_list, line_list, radio_value):
            # The key_list arguments is the list of keys to plot. The line_list
            # argument is a list of batches, or a list of dates to plot for
            # those keys.
            if key_list is None or line_list is None:
                return {}

            # Get the data, setting its index.
            if radio_value == "Statistics":
                data = get_data(self.statistics_file).set_index(
                    ["summary_key", "batch", "date"]
                )
            else:
                data = get_data(self.values_file).set_index(["batch", "date"])

            # Make a cycle iterator over the plotly colors.
            colors = cycle(DEFAULT_PLOTLY_COLORS)

            # Choose between dates or batches for different lines.
            line_key = "batch" if self.xaxis == "date" else "date"

            traces = []
            for color, key in zip(colors, key_list):
                # Select all data belonging to the current key.
                if radio_value == "Statistics":
                    key_data = data.xs(key, level="summary_key", drop_level=True)
                else:
                    key_data = data[key]

                for line in line_list:
                    # Select all rows belonging the current batch or date.
                    line_data = key_data.xs(
                        line, level=line_key, drop_level=True
                    ).reset_index()

                    # Set the name of the plotted line.
                    name = key
                    if len(line_list) > 1:
                        name += f", {line_key}:{line}"

                    # Make the traces, with mean, P10 and P90, shading in between.
                    if radio_value == "Statistics":
                        traces.extend(
                            [
                                go.Scatter(
                                    y=line_data["P90"],
                                    x=line_data[self.xaxis],
                                    mode="lines",
                                    marker={"size": 10},
                                    line={"color": color},
                                    name=name + "(P90)",
                                    showlegend=False,
                                ),
                                go.Scatter(
                                    y=line_data["P10"],
                                    x=line_data[self.xaxis],
                                    mode="lines",
                                    line={"color": color},
                                    marker={"size": 10},
                                    fill="tonexty",
                                    name=name + "(P10)",
                                    showlegend=False,
                                ),
                                go.Scatter(
                                    y=line_data["mean"],
                                    x=line_data[self.xaxis],
                                    mode="lines",
                                    marker={"size": 10},
                                    line={"color": color},
                                    name=name,
                                    showlegend=True,
                                ),
                            ]
                        )
                    else:
                        traces.append(
                            go.Scatter(
                                y=line_data[key],
                                x=line_data[self.xaxis],
                                mode="markers",
                                marker={"size": 10},
                                name=name,
                                showlegend=True,
                            )
                        )

            return {
                "data": traces,
                "layout": dict(
                    xaxis={"title": self.xaxis.capitalize()},
                    yaxis={"title": "Summary Key Value"},
                ),
            }
