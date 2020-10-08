from uuid import uuid4
from pathlib import Path

import dash_html_components as html
import dash_core_components as dcc

import plotly.graph_objs as go

from dash.dependencies import Output, Input
from everviz.plugins.plugin_abc import EvervizPluginABC
from everviz.data.load_csv.get_data import get_data
from everviz.util import base64encode


class ControlsPlot(EvervizPluginABC):
    """
    The ControlsPlot class implements a plugin for Webviz, for plotting the
    control values generated during an Everest optimization.
    """

    def __init__(self, app, csv_file):
        super().__init__()

        self.graph_id = f"graph-{uuid4()}"
        self.controls_dropdown_id = f"dropdown-{uuid4()}"

        self.csv_file = csv_file
        self.set_callbacks(app)

    def add_webvizstore(self):
        return [(get_data, [{"csv_file": self.csv_file}])]

    @property
    def layout(self):
        data = get_data(self.csv_file)

        controls = data["control"].unique()
        control_dropdown_options = [{"label": i, "value": i} for i in controls]
        control_elements = [
            html.Label("Controls to plot:"),
            dcc.Dropdown(
                id=self.controls_dropdown_id,
                options=control_dropdown_options,
                multi=True,
                value=[controls[0]],
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
            [Input(self.controls_dropdown_id, "value")],
        )
        def update_graph(control_list):
            # # The key_list arguments is the list of functions to plot.
            if control_list is None:
                return {}

            # # Get the data, setting its index.
            data = get_data(self.csv_file).set_index("control")

            traces = []
            for control in control_list:
                control_data = data.xs(control)
                traces.append(
                    go.Scatter(
                        y=control_data["value"],
                        x=control_data["batch"],
                        mode="lines",
                        name=control,
                        showlegend=True,
                    ),
                )
            return {
                "data": traces,
                "layout": dict(
                    xaxis={"title": "Batch", "tickformat": ",d"},
                    yaxis={"title": "Control Value"},
                ),
            }
