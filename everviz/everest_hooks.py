import subprocess
import shutil
import signal
import sys
import os

from everviz.util import get_everviz_folder
from everviz.config import setup_default_everviz_config
from everviz.log import setup_logger


# Mock the hookimpl decorator
# Allow everviz to be installed and have tests run without installing everest
def mock_impl(func):
    return func


try:
    from everest.plugins import hookimpl
except ImportError:
    hookimpl = mock_impl


def handle_exit(*args):  # pylint: disable=unused-argument)
    print("\n" + "=" * 32)
    print("Session terminated by the user.\n" "Thank you for using Everviz!")
    print("=" * 32)
    sys.tracebacklimit = 0
    sys.stdout = open(os.devnull, "w")
    sys.exit()


@hookimpl
def visualize_data(api):
    everviz_folder = get_everviz_folder(api)
    logger = setup_logger(everviz_folder)
    signal.signal(signal.SIGINT, handle_exit)

    config_path = setup_default_everviz_config(api)
    # The entry point of webviz is to call it from command line, and so do we.
    if shutil.which("webviz"):
        subprocess.call(["webviz", "build", config_path, "--theme", "equinor"])
    else:
        logger.error("Failed to find webviz")
