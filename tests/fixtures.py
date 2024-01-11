import json
from pathlib import Path
from typing import List

import pytest


def read_geojson(file_path: str, geometries=False):
    with open(file_path) as f:
        fc = json.load(f)
    if geometries:
        return fc["features"][0]["geometry"]
    return fc


@pytest.fixture(scope="module")
def fixture_geojson_examples_all_normal_files() -> List[Path]:
    base_path = Path("tests/data")
    all_normal_files = []
    for folder in ["valid", "invalid_geometries", "problematic_geometries"]:
        paths_in_folder = list(Path(base_path / folder).rglob("*.geojson"))
        assert paths_in_folder
        all_normal_files.extend(paths_in_folder)
    return all_normal_files
