import dash_core_components as dcc
import dash_html_components as html


def _get_layout(title, graph_id, x_data, y_data, x_label, y_label):
    return [
        html.H1(children=title, style={"textAlign": "center"}),
        dcc.Graph(
            id=graph_id,
            figure={
                "data": [dict(x=x_data, y=y_data, mode="line", line={"width": 5})],
                "layout": dict(
                    font=dict(size=20),
                    xaxis={"title": x_label},
                    yaxis={"title": y_label},
                ),
            },
        ),
    ]
