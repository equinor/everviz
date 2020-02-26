import dash_core_components as dcc
import dash_html_components as html


def get_sidebar_layout(configurations):
    _FUNCTION_MAP = {"radio": _get_radio, "dropdown": _get_dropdown}

    divs = []
    for comp_name, args in configurations:
        divs += _FUNCTION_MAP[comp_name](**args)
    return html.Div(divs)


def _get_radio(item_id, title=None, options=None):
    if not options:
        options = []
    try:
        options = [{"label": i, "value": j} for i, j in options]
    except ValueError:
        options = [{"label": i, "value": i} for i in options]
    return [
        title,
        dcc.RadioItems(
            id=item_id,
            options=options,
            value=options[0]["value"] if len(options) > 0 else None,
            labelStyle={"display": "inline-block"},
        ),
    ]


def _get_dropdown(item_id, title=None, options=None, multi=False):
    if options is None:
        options = []
    return [
        title,
        dcc.Dropdown(
            id=item_id,
            options=[{"label": i, "value": i} for i in options],
            placeholder="Select a label",
            value=options[0] if len(options) > 0 else [],
            multi=multi,
        ),
    ]
