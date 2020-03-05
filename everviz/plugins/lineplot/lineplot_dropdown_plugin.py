import dash_html_components as html
from uuid import uuid4

from webviz_config import WebvizPluginABC

from everviz.data.load_csv._get_data import get_data
from everviz.plugins._lineplot_plugin._callback._lineplot_callback import (
    _lineplot_callback,
)
from everviz.plugins._lineplot_plugin._layout._lineplot_layout import _get_layout
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash_core_components as dcc


class LineplotDropdownPlugin(WebvizPluginABC):
    def __init__(self, app, data_path, title="Lineplot"):
        super().__init__()
        self.title = title
        self.graph_id = f"graph-{uuid4()}"
        self.dropdown_id = f"dropdown-{uuid4()}"
        self.data_path = data_path

        self.labels = [
            "point_0_x-0",
            "point_0_x-1",
            "point_0_x-2",
            "point_1_x-0",
            "point_1_x-1",
            "point_1_x-2",
            "duration-0",
        ]
        self.intital_y_data = self.labels[0]
        self.set_callbacks(app)

    def add_webvizstore(self):
        return [(get_data, [{"data_path": self.data_path}])]

    @property
    def layout(self):
        df = get_data(self.data_path)

        layout = _get_layout(
            self.title,
            self.graph_id,
            df["batch"],
            df[self.intital_y_data],
            "Batch",
            self.intital_y_data,
        )

        dropdown_layout = [
            html.Div(
                [
                    dcc.Dropdown(
                        id=self.dropdown_id,
                        options=[{"label": i, "value": i} for i in self.labels],
                        placeholder="Select a label",
                        value=self.labels[:1] if len(self.labels) > 0 else [],
                        multi=True,
                    )
                ]
            )
        ]
        return html.Div(layout + dropdown_layout)

    def set_callbacks(self, app):
        @app.callback(
            Output(self.graph_id, "figure"), [Input(self.dropdown_id, "value")]
        )
        def update_graph(y_axis_name):
            df = get_data(self.data_path)
            traces = [add_trace(df, axis_name) for axis_name in y_axis_name]
            return _lineplot_callback(traces, y_axis_name)


def add_trace(df, y_axis_name):
    return go.Scatter(
        y=df[y_axis_name],
        x=df["batch"],
        mode="lines",
        name=y_axis_name,
        line={"width": 5},
    )
