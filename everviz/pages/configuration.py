import os
from everviz.util import get_everviz_folder, DEFAULT_CONFIG


def _markdown_text():
    return """
## The configuration file

The following configuration content was used to generate the current report. 
Everviz supports the same configuration format as webviz, a basic example can be found [here](https://github.com/equinor/webviz-config/blob/master/examples/basic_example.yaml) 

"""


def _set_up_data_sources(api):
    everviz_path = get_everviz_folder(api)

    markdown_path = os.path.join(everviz_path, "how_it_was_made.md")
    config_path = os.path.join(everviz_path, DEFAULT_CONFIG)
    with open(markdown_path, "w") as f:
        f.write(_markdown_text())
    return config_path, markdown_path


def page_layout(api):
    config_path, markdown_path = _set_up_data_sources(api)
    return {
        "title": "Everviz configuration",
        "content": [
            {"Markdown": {"markdown_file": markdown_path}},
            {"SyntaxHighlighter": {"filename": config_path,},},
        ],
    }
