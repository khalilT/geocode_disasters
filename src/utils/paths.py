import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_PATHS = {
    "remote_data": "/path/to/cluster/data1",
}

def get_path(name):
    """
    Retrieve the path for a given dataset name.
    Raises KeyError if the name is not found.
    """
    if name in DATA_PATHS:
        return DATA_PATHS[name]
    raise KeyError(f"No path found for dataset '{name}'")
