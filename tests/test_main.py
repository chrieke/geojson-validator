import json

from .context import validate


def read_geojson_geometry(file_path: str):
    with open(file_path) as f:
        gj = json.load(f)
    return gj


def test_validate_invalid():
    fc = read_geojson_geometry(
        "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson"
    )
    result = validate(fc)
    assert "duplicate_nodes" in result["invalid"]


def test_validate_valid():
    fc = read_geojson_geometry("./tests/examples_geojson/valid/simple_polygon.geojson")
    result = validate(fc)
    assert not result["invalid"]
    assert not result["problematic"]
