from uuid import uuid4
from pathlib import Path
from itertools import cycle
import pkg_resources

import dash_html_components as html
import dash_core_components as dcc

import plotly.graph_objs as go
from plotly.colors import DEFAULT_PLOTLY_COLORS

from dash.dependencies import Output, Input, State
from webviz_config import WebvizPluginABC
from webviz_config.webviz_assets import WEBVIZ_ASSETS
from everviz.data.load_csv.get_data import get_data

from .util import parse_range, calculate_statistics


class ObjectivesPlot(WebvizPluginABC):
    """
    The ObjectivesPlot class implements a plugin for Webviz, for plotting the
    objective values generated during an Everest optimization.

    Generally there are multiple realizations for the objective function values
    at each batch. Additionally, there may be multiple objective functions that
    are optimized simultaneously. These can be plotted either all individually
    in the plot, or they are summarized by plotting the mean value together with
    a P10-P90 range.
    """

    def __init__(self, app, csv_file):
        super().__init__()

        self.graph_id = f"graph-{uuid4()}"
        self.radio_id = f"dropdown-{uuid4()}"
        self.function_dropdown_id = f"dropdown-{uuid4()}"
        self.realization_filter_check_id = f"check-{uuid4()}"
        self.realization_filter_input_id = f"input-{uuid4()}"

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
        data = get_data(self.csv_file)

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
                value=radio_options[1],
                labelStyle={"display": "inline-block"},
                style={"margin-top": 20},
            )
        ]

        realization_elements = [
            html.Div(
                [
                    dcc.Checklist(
                        id=self.realization_filter_check_id,
                        options=[{"label": "Filter realizations:", "value": "filter"}],
                        style={"display": "inline-block", "margin-right": 8},
                    ),
                    dcc.Input(
                        id=self.realization_filter_input_id,
                        type="text",
                        placeholder="example: 0, 3, 6-10",
                        pattern=r"\s*|([0-9]+(\s*-\s*[0-9]+)?)(\s*,\s*[0-9]+(\s*-\s*[0-9]+)?)*",
                        style={"display": "inline-block"},
                    ),
                ],
                style={"margin-top": 20},
            )
        ]

        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            func_elements + radio_elements + realization_elements,
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
                                        "modeBarButtonsToRemove": ["toImage"],
                                        "displaylogo": False,
                                    },
                                )
                            ],
                            style={"width": "69%", "display": "inline-block"},
                        ),
                    ]
                ),
            ]
        )

    def set_callbacks(self, app):
        @app.callback(
            self.plugin_data_output,
            [self.plugin_data_requested],
            [
                State(self.radio_id, "value"),
                State(self.realization_filter_check_id, "value"),
                State(self.realization_filter_input_id, "value"),
            ],
        )
        def user_download_data(
            data_requested, radio_value, realizations_check, realizations_input,
        ):
            if data_requested:
                content = get_data(self.csv_file)
                if realizations_check:
                    realizations = parse_range(realizations_input)
                    if realizations:
                        content = content[content["realization"].isin(realizations)]
                if radio_value == "Statistics":
                    filename = "objective_statistics.csv"
                    content = calculate_statistics(content)
                else:
                    filename = "objective_values.csv"
                return WebvizPluginABC.plugin_data_compress(
                    [{"filename": filename, "content": content.to_csv(),}]
                )
            return ""

        @app.callback(
            Output(self.realization_filter_input_id, "disabled"),
            [Input(self.realization_filter_check_id, "value")],
        )
        def set_button_enabled_state(filter_realizations):
            return not filter_realizations

        @app.callback(
            Output(self.graph_id, "figure"),
            [
                Input(self.function_dropdown_id, "value"),
                Input(self.radio_id, "value"),
                Input(self.realization_filter_check_id, "value"),
                Input(self.realization_filter_input_id, "value"),
            ],
        )
        def update_graph(
            func_list, radio_value, realizations_check, realizations_input
        ):
            # # The key_list arguments is the list of functions to plot.
            if func_list is None:
                return {}

            # Get the data, filter if requested.
            data = get_data(self.csv_file)
            if realizations_check:
                realizations = parse_range(realizations_input)
                if realizations:
                    data = data[data["realization"].isin(realizations)]
            if len(data) == 0:
                return {}

            if radio_value == "Statistics":
                data = calculate_statistics(data)

            data = data.set_index("function")

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
