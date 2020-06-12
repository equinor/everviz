from itertools import cycle
import plotly.graph_objs as go

from plotly.colors import DEFAULT_PLOTLY_COLORS


def _get_statistics_lines(
    data, summary_key_list, line_list, x_filter, x_key, mode="lines"
):
    """
    :param data: Dataframe
    :param summary_key_list: List of summary keys to plot
    :param line_list: List of batches or dates to plot
    :param x_filter: One of date|batch
    :param x_key: Opposite of x_filter
    """
    colors = cycle(DEFAULT_PLOTLY_COLORS)
    traces = []
    for color, key in zip(colors, summary_key_list):
        # Select all data belonging to the current key.
        key_data = data.xs(key, level="summary_key", drop_level=True)

        for line in line_list:
            # Select all rows belonging the current batch or date.
            line_data = key_data.xs(line, level=x_filter, drop_level=True).reset_index()

            # Set the name of the plotted line.
            name = key
            if len(line_list) > 1:
                name += f", {x_filter}:{line}"

            # Make the traces, with mean, P10 and P90, shading in between.
            traces.extend(
                [
                    go.Scatter(
                        y=line_data["P90"],
                        x=line_data[x_key],
                        mode=mode,
                        marker={"size": 10},
                        line={"color": color},
                        name=name + "(P90)",
                        showlegend=False,
                    ),
                    go.Scatter(
                        y=line_data["P10"],
                        x=line_data[x_key],
                        mode=mode,
                        line={"color": color},
                        marker={"size": 10},
                        fill="tonexty",
                        name=name + "(P10)",
                        showlegend=False,
                    ),
                    go.Scatter(
                        y=line_data["mean"],
                        x=line_data[x_key],
                        mode=mode,
                        marker={"size": 10},
                        line={"color": color},
                        name=name,
                        showlegend=True,
                    ),
                ]
            )
    return traces


def _get_data_lines(data, summary_key_list, line_list, x_filter, x_key, mode="markers"):
    """
    :param data: Dataframe
    :param summary_key_list: List of summary keys to plot
    :param line_list: List of batches or dates to plot
    :param x_filter: One of date|batch
    :param x_key: Opposite of x_filter
    """
    colors = cycle(DEFAULT_PLOTLY_COLORS)
    traces = []
    for color, key in zip(colors, summary_key_list):
        # Select all data belonging to the current key.
        key_data = data[key]

        for line in line_list:
            # Select all rows belonging the current batch or date.
            line_data = key_data.xs(line, level=x_filter, drop_level=True).reset_index()

            # Set the name of the plotted line.
            name = key
            if len(line_list) > 1:
                name += f", {x_filter}:{line}"

            traces.append(
                go.Scatter(
                    y=line_data[key],
                    x=line_data[x_key],
                    mode=mode,
                    marker={"size": 10},
                    name=name,
                    showlegend=True,
                )
            )

    return traces


def get_callback_func(statistics):
    if statistics == "Statistics":
        return _get_statistics_lines
    return _get_data_lines
