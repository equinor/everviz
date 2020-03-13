import subprocess
import shutil
import os
from everviz.config import write_webviz_config, webviz_config
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
    file_name = "everviz_webviz_config.yml"
    everviz_folder = os.path.join(api.output_folder(), "everviz")
    file_path = os.path.join(everviz_folder, file_name)
    logger = setup_logger(everviz_folder)

    config = webviz_config()
    write_webviz_config(config, file_path)

    # The entry point of webviz is to call it from command line, and so we do.
    if shutil.which("webviz"):
        subprocess.call(
            ["webviz", "build", file_name, "--theme", "equinor"], cwd=everviz_folder
        )
    else:
        logger.error("Failed to find webviz")
