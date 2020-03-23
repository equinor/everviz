import os

DEFAULT_CONFIG = "everviz_webviz_config.yml"


def get_everviz_folder(api):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")
    if not os.path.exists(everviz_path):
        os.makedirs(everviz_path)
    return everviz_path
