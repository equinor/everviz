import sys
import os

import pytest

try:
    from pathlib import Path
    import black
    from click.testing import CliRunner
except ImportError:
    pass


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires Python3")
def test_code_style():

    root = str(Path(__file__).parent.parent.parent)

    runner = CliRunner()
    resp = runner.invoke(
        black.main,
        [
            "--check",
            os.path.join(root, "tests"),
            os.path.join(root, "everviz"),
            os.path.join(root, "setup.py"),
            "--exclude",
            "everviz/version.py",  # File written by setuptools_scm
        ],
    )

    assert (
        resp.exit_code == 0
    ), "Black would still reformat one or more files:\n{}".format(resp.output)
