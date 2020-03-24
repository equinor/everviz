def dropdown_callback(selected_control, controls):
    if selected_control is None:
        dropdown_options = controls
    else:
        dropdown_options = [
            name
            for name in controls
            if name.startswith(selected_control)
        ]
    return [{"label": i, "value": i} for i in dropdown_options]
