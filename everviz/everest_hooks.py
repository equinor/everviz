import yaml
import subprocess
import shutil

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
    config = webviz_config()

    fname = "everviz_webviz_config.yml"
    write_webviz_config(config, fname)

    # The entry point of webviz is to call it from command line, and so we do.
    if shutil.which("webviz"):
        subprocess.call("webviz build {} --theme equinor".format(fname))


def write_webviz_config(config, file_path):
    with open(file_path, "w") as fh:
        yaml.dump(config, fh, default_flow_style=False)
    print("Webviz config file created: {}".format(file_path))


def webviz_config():
    return {
        "title": "Everest Optimization Report",
        "pages": [{"title": "", "content": [],},],
    }
