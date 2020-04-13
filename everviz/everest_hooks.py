import subprocess
import shutil
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


@hookimpl
def visualize_data(api):
    everviz_folder = get_everviz_folder(api)
    logger = setup_logger(everviz_folder)

    config_path = setup_default_everviz_config(api)
    # The entry point of webviz is to call it from command line, and so do we.
    if shutil.which("webviz"):
        subprocess.call(["webviz", "build", config_path, "--theme", "equinor"])
    else:
        logger.error("Failed to find webviz")
