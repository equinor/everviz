import dash_html_components as html
from uuid import uuid4

from webviz_config import WebvizPluginABC

from everviz.data.load_csv._get_data import get_data
from everviz.plugins._lineplot_plugin._layout._lineplot_layout import _get_layout


class LineplotPlugin(WebvizPluginABC):
    def __init__(self, app, data_path, title="Lineplot"):
        super().__init__()
        self.title = title
        self.graph_id = f"graph-{uuid4()}"
        self.data_path = data_path
        self.intital_y_data = "real_avg_obj"

    def add_webvizstore(self):
        return [(get_data, [{"data_path": self.data_path}])]

    @property
    def layout(self):
        df = get_data(self.data_path)

        layout = html.Div(
            _get_layout(
                self.title,
                self.graph_id,
                df["batch"],
                df[self.intital_y_data],
                "Batch",
                "Objective function",
            )
        )
        return layout
