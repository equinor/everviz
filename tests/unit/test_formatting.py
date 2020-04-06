import black
from click.testing import CliRunner


def test_code_style():

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
