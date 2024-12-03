![Publish Python 🐍 distributions 📦 to PyPI](https://github.com/equinor/everviz/workflows/Publish%20Python%20%F0%9F%90%8D%20distributions%20%F0%9F%93%A6%20to%20PyPI/badge.svg)
![Python package](https://github.com/equinor/everviz/workflows/Python%20package/badge.svg)
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

```sh
# Test
wget https://chromedriver.storage.googleapis.com/$(wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE -q -O -)/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
export PATH=$PATH:$PWD
python -m pip install ".[test]"
pytest --headless
```
