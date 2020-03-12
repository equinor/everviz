import sys

import pytest

try:
    from pathlib import Path
    import black
    from click.testing import CliRunner
except ImportError:
    pass


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires Python3")
def test_code_style(capsys):

    runner = CliRunner()
    resp = runner.invoke(
        black.main,
        [
            "--check",
            "tests",
            "everviz",
            "setup.py",
            "--exclude",
            "everviz/version.py",  # File written by setuptools_scm
        ],
    )

    assert (
        resp.exit_code == 0
    ), "Black would still reformat one or more files:\n{}".format(resp.output)
