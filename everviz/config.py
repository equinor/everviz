import yaml

from everviz.pages import controls, objectives
from everviz.log import get_logger
from everviz.pages import controls, configuration, crossplot, summary_values


logger = get_logger()


def webviz_config(api):
    pages = [
        {"title": "Everest", "content": [],},
        controls.page_layout(api),
        summary_values.page_layout(api),
        crossplot.page_layout(api),
        objectives.page_layout(api),
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
