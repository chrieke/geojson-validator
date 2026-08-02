import json
from pathlib import Path
from typing import Union

DATA = Path(__file__).parent / "data"


def read_geojson(file_path: Union[str, Path], geometries: bool = False):
    with open(file_path, encoding="UTF-8") as f:
        fc = json.load(f)
    if geometries:
        return fc["features"][0]["geometry"]
    return fc
