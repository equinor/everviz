import os
import pkg_resources

import dash_html_components as html
import dash_core_components as dcc

import plotly.graph_objs as go

from uuid import uuid4
from dash.dependencies import Output, Input
from webviz_config import WebvizPluginABC
from webviz_config.webviz_assets import WEBVIZ_ASSETS
from everviz.data.load_csv.get_data import get_data
from everviz.plugins.lineplot.callback.lineplot_dropdown import (
    dropdown_callback,
)
from everviz.plugins.crossplot.set_up_assets import set_up_assets


class Lineplot(WebvizPluginABC):
    def __init__(self, app, data_path, title="Lineplot"):
        super().__init__()
        self.title = title
        self.graph_id = f"graph-{uuid4()}"
        self.filter_box_id = f"dropdown-{uuid4()}"
        self.dropdown_id = f"dropdown-{uuid4()}"

        self.data_path = data_path
        self.set_callbacks(app)

        ASSETS_DIR = pkg_resources.resource_filename("everviz", os.path.join("assets"))

        WEBVIZ_ASSETS.add(os.path.join(ASSETS_DIR, "axis_customization.css"))

        # We do this because webwiz currently doesn't give a way to serve
        # css when running in non portable mode.
        set_up_assets(app, ASSETS_DIR)

    def add_webvizstore(self):
        return [(get_data, [{"data_path": self.data_path}])]

    @property
    def layout(self):
        df = get_data(self.data_path)
        dropdown_options = [{"label": i, "value": i} for i in list(df.columns.unique())]
        return html.Div(
            [
                html.H1(children=self.title, style={"textAlign": "center"}),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Input(
                                    id=self.filter_box_id,
                                    placeholder="Enter a filter",
                                    type="text",
                                    value="",
                                ),
                                dcc.Dropdown(
                                    id=self.dropdown_id,
                                    options=dropdown_options,
                                    multi=True,
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
            Output(self.dropdown_id, "options"), [Input(self.filter_box_id, "value"),],
        )
        def update_dropwdown(selected_control):
            df = get_data(self.data_path)
            controls = df.columns.unique()
            return dropdown_callback(selected_control, controls)

        @app.callback(
            Output(self.graph_id, "figure"), [Input(self.dropdown_id, "value"),],
        )
        def update_graph(plot_items,):
            if plot_items is None:
                return {}
            if isinstance(plot_items, int):
                plot_items = [plot_items]
            df = get_data(self.data_path)
            x_data = df.iloc[:,0]
            traces = []
            for plot_item in plot_items:
                y_data = df[plot_item]
                traces.append(
                    go.Scatter(y=y_data, x=x_data, mode="lines", marker={"size": 10})
                )
            return {"data": traces}
