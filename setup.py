#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="everviz",
    packages=find_packages(include=["everviz"]),
    description="",
    author="Equinor ASA",
    url="https://github.com/equinor/everviz",
    setup_requires=["pytest-runner", "setuptools_scm"],
    test_suite="tests",
    use_scm_version={"write_to": "everviz/version.py"},
    tests_require=[
        "pytest==4.6.4; python_version<='2.7'",
        "pytest; python_version>='3.5'",
        'black; python_version>="3.6"',
    ],
    classifiers=[
        "Programming language :: Python",
        "Programming language :: Python :: 2.7",
        "Programming language :: Python :: 3.6",
        "Programming language :: Python :: 3.7",
    ],
)
