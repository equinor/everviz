import os
from everviz.util import get_everviz_folder, DEFAULT_CONFIG


def page_layout(api):
    everviz_path = get_everviz_folder(api)
    config_path = os.path.join(everviz_path, DEFAULT_CONFIG)
    return {
        "title": "Config editor",
        "content": [
            {
                "ConfigEditor": {
                    "data_path": config_path,
                },
            },
        ],
    }
