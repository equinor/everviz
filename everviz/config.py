import os
import yaml
from everviz.log import get_logger


def _create_folders(file_path):
    folder_path = os.path.realpath(os.path.dirname(file_path))
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)


def webviz_config():
    return {
        "title": "Everest Optimization Report",
        "pages": [{"title": "Everest", "content": [],},],
    }


def write_webviz_config(config, file_path):
    logger = get_logger()
    _create_folders(file_path)
    with open(file_path, "w") as fh:
        yaml.dump(config, fh, default_flow_style=False)
    logger.info("Webviz config file created: {}".format(file_path))
