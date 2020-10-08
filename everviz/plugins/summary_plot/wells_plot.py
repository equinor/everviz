from pathlib import Path
from uuid import uuid4

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input

from everviz.plugins.plugin_abc import EvervizPluginABC
from everviz.data.load_csv.get_data import get_data


from everviz.plugins.summary_plot.util import calculate_statistics
from everviz.plugins.utils.layout.sidebar_layout import get_sidebar_layout
from everviz.plugins.summary_plot import summary_callback
from everviz.util import base64encode

_WELL_RATE_KEYS = ["WOPR", "WWIR", "WGPR", "WGIR"]


class WellsPlot(EvervizPluginABC):
    """
    WellsPlot is made to visualize well rates and well target
    rates.
    """

    def __init__(self, app, csv_file, title="Well Rates"):
        super().__init__()
        self.title = title
        self.graph_id = f"graph-{uuid4()}"
        self.dropdown_key = f"dropdown-{uuid4()}"
        self.dropdown_batch = f"dropdown-{uuid4()}"
        self.radio_target = f"radio-{uuid4()}"
        self.radio_statistics = f"radio-{uuid4()}"
        self.label_id = f"label-{uuid4()}"

        self.csv_file = csv_file
        self.set_callbacks(app)

    def add_webvizstore(self):
        return [
            (get_data, [{"csv_file": self.csv_file}]),
        ]

    @property
    def layout(self):
        data = get_data(self.csv_file).set_index(["batch", "date", "realization"])
        well_summary_keys = [
            i for i in list(data.columns.unique()) if i.split(":")[0] in _WELL_RATE_KEYS
        ]
        data = data.reset_index()
        realizations = data["realization"].unique()
        batches = list(data["batch"].unique())
        statistics_toggle = ["Data", "Statistics"]
        target_rate_toggle = ["Off", "On"]

        side_bar_config = [
            (
                "dropdown",
                {
                    "item_id": self.dropdown_key,
                    "options": well_summary_keys,
                    "multi": True,
                },
            ),
            (
                "dropdown",
                {"item_id": self.dropdown_batch, "options": batches, "multi": True},
            ),
            (
                "label",
                {
                    "item_id": self.label_id,
                    "text": f"Statistics are calculated based on {len(realizations)} realizations",
                    "style": {},
                },
            ),
            (
                "radio",
                {"item_id": self.radio_statistics, "options": statistics_toggle},
            ),
            (
                "radio",
                {
                    "title": "Target rate",
                    "item_id": self.radio_target,
                    "options": target_rate_toggle,
                },
            ),
        ]

        return html.Div(
            [
                html.H1(children=self.title, style={"textAlign": "center"}),
                html.Div(
                    [
                        html.Div(
                            [get_sidebar_layout(side_bar_config)],
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
                                        "toImageButtonOptions": {"filename": "wells"},
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
            Output(self.label_id, "style"),
            [Input(self.radio_statistics, "value")],
        )
        def radio_group_click(option):
            if option == "Statistics":
                return {}
            return {"display": "none"}

        @app.callback(
            Output(self.graph_id, "figure"),
            [
                Input(self.dropdown_key, "value"),
                Input(self.dropdown_batch, "value"),
                Input(self.radio_statistics, "value"),
                Input(self.radio_target, "value"),
            ],
        )
        def update_graph(well_keys, batch_list, statistics, target_rate):
            if well_keys is None or batch_list is None:
                return {}
            if well_keys is not None and len(well_keys) == 0:
                return {}
            if batch_list is not None and len(batch_list) == 0:
                return {}

            df = get_data(self.csv_file)

            if statistics == "Statistics":
                df = calculate_statistics(df, well_keys).set_index(
                    ["summary_key", "batch", "date"]
                )
            else:
                df = df.set_index(["batch", "date"])

            callback = summary_callback.get_callback_func(statistics)

            traces = callback(df, well_keys, batch_list, "batch", "date")
            if target_rate == "On":
                target_keys = _get_target_keys(df, well_keys)
                traces.extend(
                    callback(df, target_keys, batch_list, "batch", "date", mode="lines")
                )

            return {
                "data": traces,
                "layout": dict(
                    xaxis={"title": "Date"},
                    yaxis={"title": "Well rates"},
                    hovermode="closest",
                ),
            }


def _get_target_keys(df, summary_keys):
    target_keys = []
    for summary_key in summary_keys:
        well_key, well_name = summary_key.split(":")
        target_key = "{}T:{}".format(well_key, well_name)
        if target_key in df:
            target_keys.append(target_key)
    return target_keys
