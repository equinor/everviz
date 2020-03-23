def page_layout(api):
    everest_export = api.everest_csv
    if everest_export is not None:
        return {
            "title": "Cross plots",
            "content": [
                {"Crossplot": {"data_path": everest_export,},},
                {"CrossplotIndexed": {"data_path": everest_export,}},
            ],
        }
    else:
        return ""
