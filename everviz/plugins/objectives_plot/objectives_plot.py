from uuid import uuid4
from itertools import cycle

import dash_html_components as html
import dash_core_components as dcc

import plotly.graph_objs as go
from plotly.colors import DEFAULT_PLOTLY_COLORS

from dash.dependencies import Output, Input, State
from everviz.plugins.plugin_abc import EvervizPluginABC
from everviz.data.load_csv.get_data import get_data
from everviz.util import parse_range, get_placeholder_text, base64encode

from .util import calculate_statistics


class ObjectivesPlot(EvervizPluginABC):
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
        self.radio_id_mode = f"dropdown-{uuid4()}"
        self.function_dropdown_id = f"dropdown-{uuid4()}"
        self.realization_filter_check_id = f"check-{uuid4()}"
        self.realization_filter_input_id = f"input-{uuid4()}"
        self.label_id = f"label-{uuid4()}"
        self.csv_file = csv_file
        self.set_callbacks(app)

    def add_webvizstore(self):
        return [
            (get_data, [{"csv_file": self.csv_file}]),
        ]

    @property
    def layout(self):
        data = get_data(self.csv_file)

        functions = data["function"].unique()
        function_dropdown_options = [{"label": i, "value": i} for i in functions]
        realizations = data["realization"].unique()
        placeholder_text = get_placeholder_text(realizations)
        func_elements = [
            html.Label("Functions to plot:"),
            dcc.Dropdown(
                id=self.function_dropdown_id,
                options=function_dropdown_options,
                multi=True,
                value=[functions[0]],
            ),
        ]

        radio_options = ["Statistics", "Values", "Normalized", "Weighted + Normalized"]
        radio_elements = [
            html.Label(
                f"Statistics are calculated based on {len(realizations)} realizations",
                id=self.label_id,
                style={"display": "none"},
            ),
            dcc.RadioItems(
                id=self.radio_id,
                options=[{"label": i, "value": i} for i in radio_options],
                value=radio_options[1],
                labelStyle={"display": "inline-block"},
                style={"margin-top": 20},
            ),
            html.Label("Style:"),
            dcc.RadioItems(
                id=self.radio_id_mode,
                options=[
                    {"label": "line", "value": "lines"},
                    {"label": "scatter", "value": "markers"},
                ],
                value="lines",
                labelStyle={"display": "inline-block"},
            ),
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
                        placeholder=placeholder_text,
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
                                        "displaylogo": False,
                                        "toImageButtonOptions": {
                                            "filename": "objectives"
                                        },
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
            data_requested,
            radio_value,
            realizations_check,
            realizations_input,
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
                return {
                    "filename": filename,
                    "content": base64encode(content.to_csv()),
                    "mime_type": "text/csv",
                }
            return None

        @app.callback(
            Output(self.realization_filter_input_id, "disabled"),
            [Input(self.realization_filter_check_id, "value")],
        )
        def set_button_enabled_state(filter_realizations):
            return not filter_realizations

        @app.callback(
            Output(self.label_id, "style"),
            [Input(self.radio_id, "value")],
        )
        def radio_group_click(option):
            if option == "Statistics":
                return {}
            return {"display": "none"}

        @app.callback(
            Output(self.graph_id, "figure"),
            [
                Input(self.function_dropdown_id, "value"),
                Input(self.radio_id, "value"),
                Input(self.radio_id_mode, "value"),
                Input(self.realization_filter_check_id, "value"),
                Input(self.realization_filter_input_id, "value"),
                Input(self.graph_id, "clickData"),
            ],
        )
        def update_graph(
            func_list,
            radio_value,
            plot_mode,
            realizations_check,
            realizations_input,
            click_data,
        ):
            # The key_list arguments is the list of functions to plot.
            if func_list is None or len(func_list) == 0:
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
                    traces.extend(statistics_traces(color, func_data, key, plot_mode))
                else:
                    traces.extend(
                        function_traces(
                            func_list,
                            click_data,
                            color,
                            func_data,
                            key,
                            plot_mode,
                            radio_value,
                        )
                    )

            return {
                "data": traces,
                "layout": dict(
                    xaxis={"title": "Batch", "tickformat": ",d"},
                    yaxis={"title": "Function Key Value"},
                    hovermode="closest",
                ),
            }


def statistics_traces(color, func_data, key, plot_mode):
    return [
        go.Scatter(
            y=func_data["P90"],
            x=func_data["batch"],
            mode=plot_mode,
            marker={"size": 10},
            line={"color": color},
            name=key + "(P90)",
            showlegend=False,
        ),
        go.Scatter(
            y=func_data["P10"],
            x=func_data["batch"],
            mode=plot_mode,
            line={"color": color},
            marker={"size": 10},
            fill="tonexty",
            name=key + "(P10)",
            showlegend=False,
        ),
        go.Scatter(
            y=func_data["mean"],
            x=func_data["batch"],
            mode=plot_mode,
            marker={"size": 10},
            line={"color": color},
            name=key,
            showlegend=True,
        ),
        go.Scatter(
            y=func_data["min_value"],
            x=func_data["batch"],
            mode="markers",
            marker={"size": 10, "symbol": "square"},
            line={"color": color},
            name=key,
            showlegend=False,
            hovertext=[f"realization: {r}" for r in func_data["min_realization"]],
        ),
        go.Scatter(
            y=func_data["max_value"],
            x=func_data["batch"],
            mode="markers",
            marker={"size": 10, "symbol": "square"},
            line={"color": color},
            name=key,
            showlegend=False,
            hovertext=[f"realization: {r}" for r in func_data["max_realization"]],
        ),
    ]


def function_traces(
    func_list, click_data, color, func_data, key, plot_mode, radio_value
):
    realizations = func_data["realization"].unique()
    for real in realizations:
        line = func_data[func_data["realization"].isin([real])]
        y_values = line["value"]
        if radio_value == "Normalized":
            y_values = y_values * line["norm"]
        elif radio_value == "Weighted + Normalized":
            y_values = y_values * line["norm"] * line["weight"]
        line_style = {"dash": "dash"}
        if len(func_list) > 1:
            line_style["color"] = color

        if click_data is not None:
            clicked_realization = click_data["points"][0].get("customdata", None)
            if clicked_realization == real:
                line_style["width"] = 4
                del line_style["dash"]

        mode = plot_mode
        if mode == "lines":
            mode = "lines+markers"

        yield go.Scatter(
            y=y_values,
            x=line["batch"],
            mode=mode,
            marker={"size": 10},
            name=f"{key}, r={real}",
            customdata=[real] * len(line["value"]),
            showlegend=True,
            line=line_style,
        )
