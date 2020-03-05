def _lineplot_callback(data, yaxis_column_name):
    return {
        "data": data,
        "layout": dict(
            yaxis={"title": yaxis_column_name,},
            xaxis={"title": "batch"},
            font={"size": 20},
        ),
    }
