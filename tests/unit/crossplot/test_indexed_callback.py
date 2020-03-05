import pytest
from everviz.plugins.crossplot.callback.crossplot_indexed_dropdown import (
    dropdown_callback,
)


@pytest.mark.parametrize(
    "test_control, expected",
    [
        (
            None,
            [
                {"label": "a", "value": "a"},
                {"label": "b", "value": "b"},
                {"label": "c", "value": "c"},
            ],
        ),
        ("a", [{"label": "a", "value": "a"}, {"label": "b", "value": "b"}]),
        ("c", [{"label": "c", "value": "c"}]),
    ],
)
def test_crossplot_dropdown_callback(test_control, expected):
    indexed_control = {"a": [1, 2, 3], "b": [1, 2, 3], "c": [1]}
    result = dropdown_callback(test_control, indexed_control)
    assert result == expected
