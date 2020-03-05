def dropdown_callback(selected_control, indexed_controls):
    if selected_control is None:
        dropdown_options = list(indexed_controls.keys())
    else:
        dropdown_options = [
            name
            for name, index in indexed_controls.items()
            if len(index) == len(indexed_controls[selected_control])
        ]
    return [{"label": i, "value": i} for i in dropdown_options]
