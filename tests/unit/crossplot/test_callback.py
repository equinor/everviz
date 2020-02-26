import pandas as pd
import pytest
from everviz.plugins.crossplot.callback.crossplot_callback import (
    crossplot_update_graph,
    get_graph_line,
)


@pytest.mark.parametrize("axis", ["xaxis", "yaxis"])
@pytest.mark.parametrize("axis_type, expected", [("Log", "log"), ("Linear", "linear")])
def test_crossplot_callback_axis_type(axis, axis_type, expected):
    if axis == "xaxis":
        inactive_axis = "yaxis"
        test_result = crossplot_update_graph(
            [], "x-column", "y-column", axis_type, "Log"
        )
    else:
        inactive_axis = "xaxis"
        test_result = crossplot_update_graph(
            [], "x-column", "y-column", "Log", axis_type
        )

    assert list(test_result.keys()) == ["data", "layout"]

    assert test_result["layout"][axis]["type"] == expected
    assert test_result["layout"][inactive_axis]["type"] == "log"


@pytest.mark.parametrize("axis", ["x", "y"])
@pytest.mark.parametrize(
    "test_input, expected", [("an-axis-type", [1, 2]), ("Cumulative", [1, 3])]
)
def test_crossplot_get_trace(axis, test_input, expected):
    mock_data = pd.DataFrame(data=[[1, 1], [2, 2]], columns=["a", "b"])
    if axis == "x":
        result = get_graph_line(mock_data["a"], mock_data["b"], test_input, "")
    else:
        result = get_graph_line(mock_data["a"], mock_data["b"], "", test_input)

    assert all(result[axis] == expected)
