import os
import yaml
from everviz.log import get_logger
from pandas import DataFrame
from collections import namedtuple

DataSources = namedtuple("DataSource", "controls_per_batch, controls_initial_vs_best")


def _create_folders(file_path):
    folder_path = os.path.realpath(os.path.dirname(file_path))
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)


def _set_up_data_sources(api):
    everviz_path = os.path.join(api.output_folder(), "everviz")
    if not os.path.exists(everviz_path):
        os.makedirs(everviz_path)

    controls_per_batch_source = _control_data_per_batch(api)
    controls_initial_vs_best = _control_data_initial_vs_best(api)
    return DataSources(
        controls_per_batch=controls_per_batch_source,
        controls_initial_vs_best=controls_initial_vs_best,
    )


def _control_data_per_batch(api):
    logger = get_logger()
    logger.info("Generating controls per batch source data file")
    data = DataFrame(api.control_values)
    everviz_path = os.path.join(api.output_folder(), "everviz")
    file_path = os.path.join(everviz_path, "controls.csv")
    data.to_csv(file_path, sep=",")
    logger.info("File created: {}".format(file_path))
    return file_path


def _control_data_initial_vs_best(api):
    logger = get_logger()
    logger.info("Generating initial vs best controls source data file")
    best_batch = DataFrame(api.objective_values).max().batch
    data = DataFrame(api.control_values)
    # Keep only controls associated with initial and best batches
    data = data[(data.batch == 0) | (data.batch == best_batch)]
    data = data.replace({"batch": 0}, "initial").replace({"batch": best_batch}, "best")

    everviz_path = os.path.join(api.output_folder(), "everviz")
    file_path = os.path.join(everviz_path, "controls_vs_best.csv")
    data.to_csv(file_path, sep=",")
    logger.info("File created: {}".format(file_path))
    return file_path


def webviz_config(api):
    sources = _set_up_data_sources(api)
    export_csv = os.path.join(api.output_folder(), "config_minimal.csv")
    return {
        "title": "Everest Optimization Report",
        "pages": [
            {
                "title": "Everest",
                "content": [{"Crossplot": {"data_path": export_csv,}}],
            },
            {
                "title": "Controls",
                "content": [
                    {
                        "TablePlotter": {
                            "lock": True,
                            "csv_file": sources.controls_per_batch,
                            "filter_cols": ["control"],
                            "plot_options": {"x": "batch", "y": "value",},
                        }
                    },
                    {
                        "TablePlotter": {
                            "lock": True,
                            "csv_file": sources.controls_initial_vs_best,
                            "filter_cols": ["batch"],
                            "plot_options": {"x": "control", "y": "value",},
                        }
                    },
                ],
            },
        ],
    }


def write_webviz_config(config, file_path):
    logger = get_logger()
    _create_folders(file_path)
    with open(file_path, "w") as fh:
        yaml.dump(config, fh, default_flow_style=False)
    logger.info("Webviz config file created: {}".format(file_path))
