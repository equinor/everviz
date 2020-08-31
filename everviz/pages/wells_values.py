import os
from collections import namedtuple

from everviz.log import get_logger

WELLS_EXPLANATION = """
The well plot requires well summary data to be loaded from the forward model.
Make sure the wells are specified in the Everest config file and exported from
Eclipse/Flow to *.UNSMRY. To visualize target rates they also need to be added 
to the simulator summary data section.
"""

DataSources = namedtuple("DataSource", ["summary_values"])

logger = get_logger()


def _set_up_data_sources(api):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")

    summary_values_file = os.path.join(everviz_path, "summary_values.csv")

    if not os.path.exists(summary_values_file):
        return None

    return DataSources(summary_values=summary_values_file)


def page_layout(api):
    sources = _set_up_data_sources(api)

    if sources is None:
        return {
            "title": "Well rates",
            "content": [
                WELLS_EXPLANATION,
            ],
        }

    return {
        "title": "Well rates",
        "content": [
            "## Well rate values as a function of date",
            {
                "WellsPlot": {
                    "csv_file": sources.summary_values,
                },
            },
        ],
    }
