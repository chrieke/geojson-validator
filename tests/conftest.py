from pathlib import Path
from typing import List

import pytest

from .helpers import DATA, read_geojson


@pytest.fixture(scope="session")
def valid_geometry() -> dict:
    return read_geojson(DATA / "valid/valid_featurecollection.geojson", geometries=True)


def _files_in(folder: str) -> List[Path]:
    paths = list((DATA / folder).rglob("*.geojson"))
    assert paths, f"No geojson test files found in {folder}"
    return paths


@pytest.fixture(scope="module")
def all_normal_geojson_files() -> List[Path]:
    """All test files with a correct structure, from the geometry check folders."""
    return [
        fp
        for folder in ["valid", "invalid_geometries", "problematic_geometries"]
        for fp in _files_in(folder)
    ]


@pytest.fixture(scope="module")
def invalid_structure_files() -> List[Path]:
    return _files_in("invalid_structure")


@pytest.fixture(scope="module")
def problematic_structure_files() -> List[Path]:
    return _files_in("problematic_structure")
