import os
import pandas as pd
from collections import namedtuple


DataSources = namedtuple("DataSource", "objective_values")


def _objective_values(api):
    return pd.DataFrame(api.objective_values)


def _calc_p10_p90(df):
    percentiles = [("P10", 0.1), ("P90", 0.9)]
    for batch in df["batch"].unique():
        for label, quantile in percentiles:
            df.loc[df["batch"] == batch, label] = df[df["batch"] == batch][
                "value"
            ].quantile(quantile)
    return df


def _calc_mean(df):
    for batch in df["batch"].unique():
        df.loc[df["batch"] == batch, "Mean"] = df[df["batch"] == batch]["value"].mean()
    return df


def _set_up_data_sources(api):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")

    objective_values = os.path.join(everviz_path, "objective_values.csv")
    data = _objective_values(api)
    data = _calc_p10_p90(data)
    data = _calc_mean(data)
    data.to_csv(objective_values, index=False)

    return DataSources(objective_values=objective_values,)


def page_layout(api):
    sources = _set_up_data_sources(api)
    return {
        "title": "Objectives",
        "content": [
            "## Objective function values",
            {"ObjectivesPlot": {"data_path": sources.objective_values,},},
        ],
    }
