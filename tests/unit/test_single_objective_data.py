from everviz.pages.objectives import _single_objective_title


def test_single_objective_title(mocker):
    api_mock = mocker.Mock()
    api_mock.objective_function_names = ["npv"]
    result = _single_objective_title(api_mock)
    expected = "Objective"
    assert result == expected

    api_mock.objective_function_names = ["npv", "rf"]
    result = _single_objective_title(api_mock)
    expected = "Objective functions"
    assert result == expected
