[![PyPI Latest Release](https://img.shields.io/pypi/v/everviz.svg)](https://pypi.org/project/everviz/)
[![Build Status](https://travis-ci.com/equinor/everviz.svg?branch=master)](https://travis-ci.com/equinor/everviz)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

# everviz: web based visualization for everest

## What is everviz
everviz is a visualization plugin for everest based on [dash](https://github.com/plotly/dash) 
and [webviz-config](https://github.com/equinor/webviz-config).

## Download project
The code is hosted on GitHub:
https://github.com/equinor/everviz

The latest version is available on [pypi](https://pypi.org/project/everviz).

```sh
# Install
pip install everviz
```

## Run tests
[tox](https://tox.readthedocs.io/en/latest/) is used as the test facilitator,
to run the full test suite:

```sh
# Test
pip install tox
tox
```

or to run it for a particular Python version (in this case Python 3.7):

```sh
# Test
pip install tox
tox -e py37
```

[pytest](https://docs.pytest.org/en/latest/) is used as the test runner, so for quicker
iteration it is possible to run:

```sh
# Test
pytest
# or to run the tests headless:
pytest --headless
```

this requires that the test dependencies from `tox.ini` are installed.

The tests requires WebDrivers (default: Chrome), more information can be found [here](https://dash.plotly.com/testing)
