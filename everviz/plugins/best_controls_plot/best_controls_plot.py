from uuid import uuid4
from pathlib import Path

import dash_html_components as html
import dash_core_components as dcc

import plotly.express as px

from everviz.plugins.plugin_abc import EvervizPluginABC
from everviz.data.load_csv.get_data import get_data
from everviz.util import base64encode


class BestControlsPlot(EvervizPluginABC):
    """
    The BestControlsPlot class implements a plugin for Webviz, for plotting the
    best control values vs the initial values.
    """

    def __init__(self, app, csv_file):
        super().__init__()

        self.graph_id = f"graph-{uuid4()}"

        self.csv_file = csv_file
        self.set_callbacks(app)

    def add_webvizstore(self):
        return [(get_data, [{"csv_file": self.csv_file}])]

    @property
    def layout(self):
        data = get_data(self.csv_file)

        fig = px.scatter(
            data,
            y="value",
            x="control",
            color="batch",
            template="plotly_white",
            labels={"control": "Control", "value": "Control Value"},
        )
        return html.Div(
            [
                dcc.Graph(
                    id=self.graph_id,
                    config={
                        "displaylogo": False,
                        "toImageButtonOptions": {"filename": "best_controls"},
                    },
                    figure=fig,
                )
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
