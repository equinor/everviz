import os
from collections import namedtuple
import pandas as pd
from everviz.log import get_logger


DataSources = namedtuple("DataSource", "gradient_values")

logger = get_logger()


def _gradient_values(api):
    gradient_values = api.gradient_values
    if gradient_values:
        return pd.DataFrame(api.gradient_values)
    return None


def _set_up_data_sources(api):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")

    logger.info("Generating controls per batch source data file")
    gradient_values = os.path.join(everviz_path, "gradient_values.csv")
    data = _gradient_values(api)
    if data is None:
        logger.info("No gradient data availabe, skipping")
        return None
    data.to_csv(gradient_values, index=False)
    logger.info(f"File created: {gradient_values}")  # pylint: disable=W1203
    return DataSources(gradient_values=gradient_values)


def page_layout(api):
    sources = _set_up_data_sources(api)
    if sources is None:
        return {}
    return {
        "title": "Gradients",
        "content": [
            "## Gradient values",
            {"GradientPlot": {"csv_file": sources.gradient_values}},
        ],
    }
