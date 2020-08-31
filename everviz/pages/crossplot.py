from everviz.util import identify_indexed_controls

_crossplot_doc = """
This plot will load all the data from everest export and all columns can be visualized in a crossplot
""".strip()
_crossplot_indexed_doc = """
This plot will load the indexed control values and they can be visualized in a crossplot
""".strip()


def page_layout(api):
    everest_export = api.everest_csv
    if everest_export is not None:
        plots = [
            _crossplot_doc,
            {
                "Crossplot": {
                    "data_path": everest_export,
                },
            },
        ]

        indexed_controls = identify_indexed_controls(api.control_names)
        if len(indexed_controls) > 0:
            plots.extend(
                [
                    _crossplot_indexed_doc,
                    {
                        "CrossplotIndexed": {
                            "data_path": everest_export,
                        }
                    },
                ]
            )

        return {
            "title": "Cross plots",
            "content": plots,
        }
    return ""
