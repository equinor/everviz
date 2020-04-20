import pytest

from everviz.util import identify_indexed_controls


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (["base_name-0", "base_name-1"], {"base_name": [0, 1]}),
        (["base_name-0", "indexed-0"], {"base_name": [0], "indexed": [0]}),
        (["not_indexed"], {}),
        (["not_indexed-a"], {}),
    ],
)
def test_get_indexed_controls(test_input, expected):
    result = identify_indexed_controls(test_input)
    assert result == expected
