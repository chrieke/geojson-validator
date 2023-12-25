import json
from unittest.mock import patch

import pytest

from .context import main


def read_geojson_geometry(file_path: str):
    with open(file_path) as f:
        gj = json.load(f)
    return gj


def test_check_criteria_invalid():
    with pytest.raises(ValueError):
        main.check_criteria(["non_existent_criteria"], "invalid")

def test_check_criteria_valid():
    try:
        main.check_criteria(["unclosed", "duplicate_nodes"], "invalid")
        main.check_criteria(["holes"], "problematic")
    except ValueError:
        pytest.fail("Unexpected ValueError for valid criteria")


def test_read_file():
    filepath = "./tests/examples_geojson/valid/simple_polygon.geojson"
    geojson_input = main.read_file(filepath)
    assert isinstance(geojson_input, dict)


def test_get_geometries_feature_collection():
    fc = read_geojson_geometry("./tests/examples_geojson/valid/simple_polygon.geojson")
    type_, geometries = main.get_geometries(fc)
    assert type_ == "FeatureCollection"
    assert isinstance(geometries, list)
    assert isinstance(geometries[0], dict)

def test_get_geometries_invalid_type():
    with pytest.raises(ValueError):
        main.get_geometries({"type": "InvalidType"})


@patch('geojson_validate.main.check_criteria')
@patch('geojson_validate.main.get_geometries')
@patch('geojson_validate.main.process_validation')
def test_validate(mock_process_validation, mock_get_geometries, mock_check_criteria):
    """Ensure the validate function integrates them correctly."""
    mock_get_geometries.return_value = ("FeatureCollection", [])
    mock_process_validation.return_value = {"invalid": {}, "problematic": {}}

    geojson_input = {}  # Mock input
    results = main.validate(geojson_input)

    assert 'invalid' in results
    assert 'problematic' in results
    mock_check_criteria.assert_called()
    mock_get_geometries.assert_called_with(geojson_input)
    mock_process_validation.assert_called()



def test_validate_invalid():
    fc = read_geojson_geometry(
        "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson"
    )
    result = main.validate(fc)
    assert "duplicate_nodes" in result["invalid"]


def test_validate_valid():
    fc = read_geojson_geometry("./tests/examples_geojson/valid/simple_polygon.geojson")
    result = main.validate(fc)
    assert not result["invalid"]
    assert not result["problematic"]
