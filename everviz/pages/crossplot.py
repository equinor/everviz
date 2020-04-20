from everviz.util import identify_indexed_controls


def page_layout(api):
    everest_export = api.everest_csv
    if everest_export is not None:
        plots = [{"Crossplot": {"data_path": everest_export,},}]

        indexed_controls = identify_indexed_controls(api.control_names)
        if len(indexed_controls) > 0:
            plots.append({"CrossplotIndexed": {"data_path": everest_export,}})

        return {
            "title": "Cross plots",
            "content": plots,
        }
    return ""
