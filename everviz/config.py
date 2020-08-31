import os
import yaml

from everviz.log import get_logger
from everviz.util import get_everviz_folder, DEFAULT_CONFIG
from everviz.pages import (
    controls,
    configuration,
    crossplot,
    summary_values,
    objectives,
    deltaplot,
    wells_values,
)

logger = get_logger()


def webviz_config(api):
    pages = [
        {
            "title": "Everest",
            "content": [],
        },
        objectives.page_layout(api),
        summary_values.page_layout(api),
        wells_values.page_layout(api),
        crossplot.page_layout(api),
        controls.page_layout(api),
        deltaplot.page_layout(api),
        configuration.page_layout(api),
    ]

    # Remove possible empty pages
    pages = list(filter(None, pages))

    return {
        "title": "Everest Optimization Report",
        "pages": pages,
    }


def write_webviz_config(config, file_path):
    with open(file_path, "w") as fh:
        yaml.dump(config, fh, default_flow_style=False, sort_keys=False)
    logger.info("Webviz config file created: {}".format(file_path))


def setup_default_everviz_config(api):
    """
    Creates default everviz config file and all required data sources
    """
    everviz_folder = get_everviz_folder(api)

    config = webviz_config(api)
    config_file_path = os.path.join(everviz_folder, DEFAULT_CONFIG)
    write_webviz_config(config, config_file_path)
    logger.info("Default everviz config created: {}".format(config_file_path))
    return config_file_path
