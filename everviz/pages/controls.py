from pandas import DataFrame


def control_data_per_batch(api):
    return DataFrame(api.control_values)


def control_data_initial_vs_best(api):
    objectives_df = DataFrame(api.objective_values)
    best_batch = objectives_df.batch[objectives_df.value.idxmax()]
    data = DataFrame(api.control_values)

    # Keep only controls associated with initial and best batches
    data = data[(data.batch == 0) | (data.batch == best_batch)]
    return data.replace({"batch": 0}, "initial").replace({"batch": best_batch}, "best")


def page_layout(controls_per_batch, controls_initial_vs_best):
    return {
        "title": "Controls",
        "content": [
            "## Control value per batch",
            {
                "TablePlotter": {
                    "lock": True,
                    "csv_file": controls_per_batch,
                    "filter_cols": ["control"],
                    "plot_options": {
                        "x": "batch",
                        "y": "value",
                        "type": "line",
                        "color": "control",
                    },
                }
            },
            "## Initial controls versus best controls",
            {
                "TablePlotter": {
                    "lock": True,
                    "csv_file": controls_initial_vs_best,
                    "plot_options": {
                        "x": "control",
                        "y": "value",
                        "type": "scatter",
                        "color": "batch",
                    },
                }
            },
        ],
    }
