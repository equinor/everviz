import os
import pkg_resources
from pathlib import Path
import dash_html_components as html
import dash_core_components as dcc

from uuid import uuid4
from dash.dependencies import Input, Output
from webviz_config import WebvizPluginABC

from everviz.plugins.crossplot.layout.crossplot_layout import get_sidebar_layout
from everviz.plugins.crossplot.callback.crossplot_callback import (
    crossplot_update_graph,
    get_graph_line,
)
from everviz.data.load_csv.get_data import get_data
from webviz_config.webviz_assets import WEBVIZ_ASSETS


class Crossplot(WebvizPluginABC):
    def __init__(self, app, data_path, title="Crossplot"):
        super().__init__()
        self.title = title
        self.graph_id = f"graph-{uuid4()}"
        self.keys_x_id = f"dropdown-{uuid4()}"
        self.keys_y_id = f"dropdown-{uuid4()}"
        self.axis_type_x_id = f"radio-{uuid4()}"
        self.axis_type_y_id = f"radio-{uuid4()}"
        self.axis_opt_x_id = f"radio-{uuid4()}"
        self.axis_opt_y_id = f"radio-{uuid4()}"

        self.data_path = data_path
        self.set_callbacks(app)

        ASSETS_DIR = pkg_resources.resource_filename("everviz", os.path.join("assets"))

        WEBVIZ_ASSETS.add(Path(ASSETS_DIR) / "axis_customization.css")

    def add_webvizstore(self):
        return [(get_data, [{"data_path": self.data_path}])]

    @property
    def layout(self):
        axis_type = [(i, i) for i in ["Linear", "Log"]]
        axis_options = ["Normal", "Cumulative"]
        df = get_data(self.data_path)
        plot_keys = df.columns.unique()

        sidebar_configs = [
            (
                "radio",
                {
                    "title": "X-axis",
                    "item_id": self.axis_type_x_id,
                    "options": axis_type,
                },
            ),
            ("radio", {"item_id": self.axis_opt_x_id, "options": axis_options},),
            ("dropdown", {"item_id": self.keys_x_id, "options": plot_keys},),
            (
                "radio",
                {
                    "title": "Y-axis",
                    "item_id": self.axis_type_y_id,
                    "options": axis_type,
                },
            ),
            ("radio", {"item_id": self.axis_opt_y_id, "options": axis_options},),
            ("dropdown", {"item_id": self.keys_y_id, "options": plot_keys},),
        ]

        return html.Div(
            [
                html.H1(children=self.title, style={"textAlign": "center"},),
                html.Div(
                    [
                        html.Div(
                            [get_sidebar_layout(sidebar_configs)],
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
                Input(self.keys_x_id, "value"),
                Input(self.keys_y_id, "value"),
                Input(self.axis_type_x_id, "value"),
                Input(self.axis_type_y_id, "value"),
                Input(self.axis_opt_x_id, "value"),
                Input(self.axis_opt_y_id, "value"),
            ],
        )
        def update_graph(
            xaxis_column_name,
            yaxis_column_name,
            xaxis_type,
            yaxis_type,
            axis_options_x_id,
            axis_options_y_id,
        ):
            df = get_data(self.data_path)
            x_data = df[xaxis_column_name]
            y_data = df[yaxis_column_name]
            data = [
                get_graph_line(x_data, y_data, axis_options_x_id, axis_options_y_id)
            ]
            return crossplot_update_graph(
                data, xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type
            )
