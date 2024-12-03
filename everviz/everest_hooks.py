import os
import shutil
import signal
import subprocess
import sys

from everest.plugins import hookimpl  # pylint: disable=import-error

from everviz.config import setup_default_everviz_config
from everviz.log import setup_logger
from everviz.util import get_everviz_folder


def handle_exit(*args):  # pylint: disable=unused-argument)
    print("\n" + "=" * 32)
    print("Session terminated by the user.\nThank you for using Everviz!")
    print("=" * 32)
    sys.tracebacklimit = 0
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
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
