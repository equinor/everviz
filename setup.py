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
        "pytest",
        'black',
    ],
    classifiers=[
        "Programming language :: Python",
        "Programming language :: Python :: 3.6",
        "Programming language :: Python :: 3.7",
    ],
)
