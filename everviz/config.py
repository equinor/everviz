import os
import yaml

from everviz.log import get_logger
from everviz.pages import controls, crossplot, summary_values


logger = get_logger()


def create_everviz_folder(everest_folder):
    everviz_path = os.path.join(everest_folder, "everviz")
    if not os.path.exists(everviz_path):
        os.makedirs(everviz_path)
    return everviz_path


def webviz_config(api):
    create_everviz_folder(api.output_folder)
    return {
        "title": "Everest Optimization Report",
        "pages": [
            {"title": "Everest", "content": [],},
            controls.page_layout(api),
            summary_values.page_layout(api),
            crossplot.page_layout(api),
        ],
    }


def write_webviz_config(config, file_path):
    with open(file_path, "w") as fh:
        yaml.dump(config, fh, default_flow_style=False, sort_keys=False)
    logger.info("Webviz config file created: {}".format(file_path))
