from uuid import uuid4
from pathlib import Path

import dash_html_components as html
import dash_core_components as dcc

import plotly.graph_objs as go

from dash.dependencies import Output, Input
from everviz.plugins.plugin_abc import EvervizPluginABC
from everviz.data.load_csv.get_data import get_data
from everviz.util import base64encode


class DeltaPlot(EvervizPluginABC):
    """
    The DeltaPlot class implements a plugin for Webviz, for plotting the
    difference in values generated during an Everest optimization.
    """

    def __init__(self, app, csv_file, pre_select):
        super().__init__()

        self.graph_id = f"graph-{uuid4()}"
        self.key_dropdown_id = f"dropdown-{uuid4()}"
        self.date_dropdown_id = f"dropdown-{uuid4()}"

        self.csv_file = csv_file
        self.pre_select = pre_select

        self.set_callbacks(app)

    def add_webvizstore(self):
        return [
            (get_data, [{"csv_file": self.csv_file}]),
        ]

    @property
    def layout(self):
        data = get_data(self.csv_file)

        key_dropdown_options = [
            {"label": i, "value": i}
            for i in data.columns
            if i not in ["realization", "date"]
        ]

        if self.pre_select == "first":
            key_dropdown_value = [key_dropdown_options[0]["label"]]
        elif self.pre_select == "all":
            key_dropdown_value = [option["label"] for option in key_dropdown_options]
        elif self.pre_select == "none":
            key_dropdown_value = []
        else:
            raise RuntimeError(f"Invalid argument: 'pre_select={self.pre_select}")

        dropdown_elements = [
            html.Label("Values to plot:"),
            dcc.Dropdown(
                id=self.key_dropdown_id,
                options=key_dropdown_options,
                multi=True,
                value=key_dropdown_value,
            ),
        ]

        if "date" in data.columns:
            date_dropdown_options = [
                {"label": i, "value": i} for i in data["date"].unique()
            ]
            date_dropdown_value = (
                [date_dropdown_options[-1]["label"]] if date_dropdown_options else None
            )
            dropdown_elements.extend(
                [
                    html.Label("Dates to plot:"),
                    dcc.Dropdown(
                        id=self.date_dropdown_id,
                        options=date_dropdown_options,
                        multi=True,
                        value=date_dropdown_value,
                    ),
                ]
            )

        if "objective" in self.csv_file:
            plot_filename = "delta_objectives"
        elif "summary" in self.csv_file:
            plot_filename = "delta_summary"
        else:
            plot_filename = "delta"

        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            dropdown_elements,
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
                                            "filename": plot_filename
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
        @app.callback(self.plugin_data_output, [self.plugin_data_requested])
        def user_download_data(data_requested):
            if data_requested:
                return {
                    "filename": Path(self.csv_file).name,
                    "content": base64encode(csv=get_data(self.csv_file).to_csv()),
                    "mime_type": "text/csv",
                }
            return None

        inputs = [Input(self.key_dropdown_id, "value")]
        data = get_data(self.csv_file)
        if "date" in data.columns:
            inputs.append(Input(self.date_dropdown_id, "value"))

        @app.callback(
            Output(self.graph_id, "figure"),
            inputs,
        )
        def update_graph(key_list, *args):
            if key_list is None:
                return {}

            data = get_data(self.csv_file)

            traces = []
            if "date" in data.columns:
                for key in key_list:
                    for date in args[0]:
                        selected_data = data[data["date"] == date].drop(
                            columns=["date"]
                        )
                        traces.append(
                            go.Bar(
                                y=selected_data[key],
                                x=selected_data["realization"],
                                name=f"{key}:{date}",
                                showlegend=True,
                            ),
                        )
            else:
                for key in key_list:
                    traces.append(
                        go.Bar(
                            y=data[key],
                            x=data["realization"],
                            name=key,
                            showlegend=True,
                        ),
                    )

            return {
                "data": traces,
                "layout": dict(
                    xaxis={"title": "Realization", "tickformat": ",d"},
                    yaxis={"title": "(best realization) - (initial realization)"},
                ),
            }
