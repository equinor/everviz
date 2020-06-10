import os
from collections import defaultdict

DEFAULT_CONFIG = "everviz_webviz_config.yml"


def get_everviz_folder(api):
    everest_folder = api.output_folder
    everviz_path = os.path.join(everest_folder, "everviz")
    if not os.path.exists(everviz_path):
        os.makedirs(everviz_path)
    return everviz_path


def identify_indexed_controls(controls):
    base_names = defaultdict(list)
    for control in controls:
        try:
            base_name, index = control.split("-")
            if index.isnumeric():
                base_names[base_name].append(int(index))
        except ValueError:
            continue

    return base_names


def parse_range(numbers):
    result = set()
    if numbers is not None:
        for number in numbers.split(","):
            number = number.strip()
            if number.isdigit():
                result.add(int(number))
            elif "-" in number:
                number_range = number.split("-")
                start = number_range[0]
                stop = number_range[1]
                if start.isdigit() and stop.isdigit():
                    result |= set(range(int(start), int(stop) + 1))
    return result
