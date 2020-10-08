import os
from collections import namedtuple
import pandas as pd
from everviz.log import get_logger


DataSources = namedtuple("DataSource", "controls_per_batch, controls_initial_vs_best")

logger = get_logger()


def _control_data_per_batch(api):
    return pd.DataFrame(api.control_values)


def _control_data_initial_vs_best(api):
    objectives_df = pd.DataFrame(api.single_objective_values)
    best_batch = objectives_df.batch[objectives_df.objective.idxmax()]
    data = pd.DataFrame(api.control_values)

    # Keep only controls associated with initial and best batches
    data = data[(data.batch == 0) | (data.batch == best_batch)]
    data = data.replace({"batch": 0}, "initial").replace({"batch": best_batch}, "best")
    return data


def _set_up_data_sources(api):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")

    logger.info("Generating controls per batch source data file")
    controls_per_batch = os.path.join(everviz_path, "controls_per_batch.csv")
    data = _control_data_per_batch(api)
    data.to_csv(controls_per_batch, index=False)
    logger.info(f"File created: {controls_per_batch}")  # pylint: disable=W1203

    logger.info("Generating initial vs best controls source data file")
    controls_initial_vs_best = os.path.join(
        everviz_path, "controls_initial_vs_best.csv"
    )
    data = _control_data_initial_vs_best(api)
    data.to_csv(controls_initial_vs_best, index=False)

    return DataSources(
        controls_per_batch=controls_per_batch,
        controls_initial_vs_best=controls_initial_vs_best,
    )


def page_layout(api):
    sources = _set_up_data_sources(api)
    return {
        "title": "Controls",
        "content": [
            "## Control value per batch",
            {"ControlsPlot": {"csv_file": sources.controls_per_batch}},
            "## Initial controls versus best controls",
            {
                "BestControlsPlot": {
                    "csv_file": sources.controls_initial_vs_best,
                }
            },
        ],
    }
