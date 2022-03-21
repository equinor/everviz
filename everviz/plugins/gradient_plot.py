from uuid import uuid4
from pathlib import Path

from pandas import IndexSlice

import plotly.graph_objs as go

from dash import html, dcc
from dash.dependencies import Output, Input

from everviz.plugins.plugin_abc import EvervizPluginABC
from everviz.data.load_csv.get_data import get_data
from everviz.util import base64encode
from everviz.components import list_select


class GradientPlot(EvervizPluginABC):
    """
    The GradientPlot class implements a plugin for Webviz, for plotting the
    gradient values generated during an Everest optimization.
    """

    def __init__(self, app, csv_file):
        super().__init__()

        self.graph_id = f"graph-{uuid4()}"
        self.function_dropdown_id = f"dropdown-{uuid4()}"
        self.batch_dropdown_id = f"dropdown-{uuid4()}"
        self.control_dropdown_id = f"dropdown-{uuid4()}"
        self.normalization_radio_id = f"dropdown-{uuid4()}"
        self.abs_check_id = f"dropdown-{uuid4()}"
        self.list_select_id = str(uuid4())

        self.csv_file = csv_file
        self.set_callbacks(app)

    def add_webvizstore(self):
        return [(get_data, [{"csv_file": self.csv_file}])]

    @staticmethod
    def get_options(str_list):
        return [{"label": str_elem, "value": str_elem} for str_elem in str_list]

    @property
    def layout(self):
        data = get_data(self.csv_file)

        functions = data["function"].unique()
        batches = data["batch"].unique()
        controls = data["control"].unique()
        radio_buttons = ["None", "By Function", "All"]

        function_dropdown_options = self.get_options(functions)
        batch_dropdown_options = self.get_options(batches)
        controls_dropdown_options = self.get_options(controls)
        radio_options = self.get_options(radio_buttons)

        control_elements = [
            html.Label("Functions to plot:"),
            dcc.Dropdown(
                id=self.function_dropdown_id,
                options=function_dropdown_options,
                multi=True,
                value=[functions[0]],
            ),
            html.Label("Batches to plot:"),
            dcc.Dropdown(
                id=self.batch_dropdown_id,
                options=batch_dropdown_options,
                multi=True,
                value=[batches[0]],
            ),
            html.Label("Controls to plot:"),
            list_select.layout(self.list_select_id, controls_dropdown_options),
            html.Label("Normalization:"),
            dcc.RadioItems(
                id=self.normalization_radio_id,
                options=radio_options,
                value=radio_buttons[0],
                labelStyle={"display": "inline-block"},
            ),
            dcc.Checklist(
                id=self.abs_check_id,
                options=[{"label": "Plot absolute values:", "value": "abs"}],
                style={
                    "display": "inline-block",
                    "margin-right": 8,
                    "margin-top": 20,
                },
            ),
        ]

        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            control_elements,
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
                                            "filename": "controls"
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
        list_select_id = list_select.controller_callback(self.list_select_id, app)

        @app.callback(self.plugin_data_output, [self.plugin_data_requested])
        def user_download_data(data_requested):
            if data_requested:
                return {
                    "filename": Path(self.csv_file).name,
                    "content": base64encode(get_data(self.csv_file).to_csv()),
                    "mime_type": "text/csv",
                }
            return None

        @app.callback(
            Output(self.graph_id, "figure"),
            [
                Input(self.function_dropdown_id, "value"),
                Input(self.batch_dropdown_id, "value"),
                Input(list_select_id, "value"),
                Input(self.normalization_radio_id, "value"),
                Input(self.abs_check_id, "value"),
            ],
        )
        def update_graph(
            function_list, batch_list, control_list, normalization, absolute_values
        ):
            if function_list is None or batch_list is None or not control_list:
                return {}

            data = (
                get_data(self.csv_file)
                .set_index(["batch", "function", "control"])
                .loc[IndexSlice[batch_list, function_list, control_list], :]
            )

            if absolute_values:
                data["value"] = data["value"].abs()
            if normalization == "All":
                data["value"] /= data["value"].abs().max()
            elif normalization == "By Function":
                for function in function_list:
                    data.loc[IndexSlice[:, function], "value"] /= (
                        data.loc[IndexSlice[:, function], "value"].abs().max()
                    )
            traces = []
            for function in function_list:
                for batch in batch_list:
                    batch_data = data.xs((batch, function))
                    traces.append(
                        go.Bar(
                            y=batch_data["value"],
                            x=batch_data.index,
                            name=f"{function}: batch:{batch}",
                            showlegend=True,
                        ),
                    )
            return {
                "data": traces,
                "layout": dict(
                    xaxis={"title": "Controls", "tickformat": ",d", "automargin": True},
                    yaxis={"title": "Gradient Value"},
                ),
            }
