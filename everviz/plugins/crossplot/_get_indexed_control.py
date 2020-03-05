from collections import defaultdict


def _identify_indexed_controls(controls):
    base_names = defaultdict(list)
    for control in controls:
        try:
            base_name, index = control.split("-")
            if index.isnumeric():
                base_names[base_name].append(int(index))
        except ValueError:
            continue

    return base_names
