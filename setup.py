#!/usr/bin/env python
from os import path
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="everviz",
    packages=find_packages(exclude=["tests", "test-data"]),
    package_data={"everviz": ["assets/axis_customization.css"]},
    description="Visualization for Everest",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Software Innovation Bergen, Equinor ASA",
    license="AGPL-3.0",
    url="https://github.com/equinor/everviz",
    setup_requires=["setuptools_scm"],
    install_requires=[
        "pyyaml",
        "pandas",
        "numpy",
        "dash",
        "webviz-config>=0.2.0",
        "plotly",
        "flask",
    ],
    test_suite="tests",
    use_scm_version={"write_to": "everviz/version.py"},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={
        "webviz_config_plugins": [
            "Crossplot = everviz.plugins:Crossplot",
            "CrossplotIndexed = everviz.plugins:CrossplotIndexed",
            "SummaryPlot = everviz.plugins:SummaryPlot",
            "ObjectivesPlot = everviz.plugins:ObjectivesPlot",
            "SingleObjectivesPlot = everviz.plugins:SingleObjectivesPlot",
            "ControlsPlot = everviz.plugins:ControlsPlot",
            "BestControlsPlot = everviz.plugins:BestControlsPlot",
            "DeltaPlot = everviz.plugins:DeltaPlot",
            "ConfigEditor = everviz.plugins:ConfigEditor",
            "WellsPlot = everviz.plugins:WellsPlot",
        ],
        "everest": [
            "everviz = everviz.everest_hooks",
        ],
    },
)
