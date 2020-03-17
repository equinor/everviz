import os
import yaml
from collections import namedtuple
from everviz.log import get_logger
from everviz.pages import controls

DataSources = namedtuple("DataSource", "controls_per_batch, controls_initial_vs_best")

logger = get_logger()


def _get_everviz_folder(everest_folder):
    everviz_path = os.path.join(everest_folder, "everviz")
    if not os.path.exists(everviz_path):
        os.makedirs(everviz_path)
    return everviz_path


def _write_to_csv(data, file_path, sep=","):
    data.to_csv(file_path, sep=sep, index=False)
    logger.info("File created: {}".format(file_path))
    return file_path


def _set_up_data_sources(api):
    everviz_path = _get_everviz_folder(api.output_folder())

    logger.info("Generating controls per batch source data file")
    controls_per_batch = os.path.join(everviz_path, "controls_per_batch.csv")
    _write_to_csv(controls.control_data_per_batch(api), controls_per_batch)

    logger.info("Generating initial vs best controls source data file")
    controls_initial_vs_best = os.path.join(
        everviz_path, "controls_initial_vs_best.csv"
    )
    _write_to_csv(controls.control_data_initial_vs_best(api), controls_initial_vs_best)

    return DataSources(
        controls_per_batch=controls_per_batch,
        controls_initial_vs_best=controls_initial_vs_best,
    )


def webviz_config(api):
    sources = _set_up_data_sources(api)
    return {
        "title": "Everest Optimization Report",
        "pages": [
            {"title": "Everest", "content": [],},
            controls.page_layout(
                sources.controls_per_batch, sources.controls_initial_vs_best
            ),
        ],
    }


def write_webviz_config(config, file_path):
    with open(file_path, "w") as fh:
        yaml.dump(config, fh, default_flow_style=False)
    logger.info("Webviz config file created: {}".format(file_path))
