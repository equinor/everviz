import numpy as np
import plotly.graph_objs as go


def crossplot_update_graph(
    data, xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type
):
    return {
        "data": data,
        "layout": dict(
            xaxis={
                "title": xaxis_column_name,
                "type": xaxis_type.lower(),
            },
            yaxis={
                "title": yaxis_column_name,
                "type": yaxis_type.lower(),
            },
        ),
    }


def get_graph_line(
    x_data,
    y_data,
    xaxis_option,
    yaxis_option,
    mode="markers",
    line_shape=None,
    name=None,
):
    return go.Scatter(
        y=y_data if yaxis_option != "Cumulative" else np.cumsum(y_data),
        x=x_data if xaxis_option != "Cumulative" else np.cumsum(x_data),
        mode=mode,
        marker={"size": 10},
        line_shape=line_shape,
        name=name,
    )
