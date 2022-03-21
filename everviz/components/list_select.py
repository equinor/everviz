from typing import List
import dash

from dash.development.base_component import Component
from dash.dependencies import Output, Input, State
from dash import html, dcc

import webviz_core_components as wcc


def layout(uuid: str, default_options: List[str] = None) -> Component:
    return html.Div(
        [
            wcc.Select(
                id=f"multi-selector_id_{uuid}",
                multi=True,
                size=10,
                persistence=True,
                options=default_options if default_options is not None else [],
            ),
            dcc.Dropdown(
                id=f"selected_dropdown_id_{uuid}",
                value=[],
                multi=True,
                options=[],
                persistence=True,
                style={"margin-bottom": 20},
            ),
            dcc.Store(id=f"selection-store_id_{uuid}", storage_type="session"),
        ]
    )


def controller_callback(uuid: str, app: dash.Dash) -> str:
    @app.callback(
        [
            Output(f"selected_dropdown_id_{uuid}", "options"),
            Output(f"selected_dropdown_id_{uuid}", "value"),
            Output(f"multi-selector_id_{uuid}", "options"),
            Output(f"multi-selector_id_{uuid}", "value"),
            Output(f"selection-store_id_{uuid}", "data"),
        ],
        [
            Input(f"multi-selector_id_{uuid}", "value"),
            Input(f"selected_dropdown_id_{uuid}", "value"),
        ],
        [
            State(f"selected_dropdown_id_{uuid}", "options"),
            State(f"selected_dropdown_id_{uuid}", "value"),
            State(f"multi-selector_id_{uuid}", "options"),
            State(f"selection-store_id_{uuid}", "data"),
        ],
    )
    def callback_selection_list(
        list_values, _, dropdown_options, dropdown_value, list_options, selection_store
    ):
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if not triggered_id and not selection_store:
            selection_store = {"options": list_options, "selected": []}

        if triggered_id == f"multi-selector_id_{uuid}":
            for option in list_options:
                if option["value"] in list_values:
                    selection_store["selected"].append(option)

        if triggered_id == f"selected_dropdown_id_{uuid}":
            for option in dropdown_options:
                if option["value"] not in dropdown_value:
                    selection_store["selected"].remove(option)

        list_options = [
            option
            for option in selection_store["options"]
            if option not in selection_store["selected"]
        ]
        list_value = []  # No element should be highlited as selected
        dropdown_options = selection_store["selected"]
        dropdown_value = [elem["value"] for elem in dropdown_options]
        return [
            dropdown_options,
            dropdown_value,
            list_options,
            list_value,
            selection_store,
        ]

    return f"selected_dropdown_id_{uuid}"
