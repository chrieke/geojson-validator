from unittest.mock import patch

import pytest

from .fixtures_utils import read_geojson
from .context import main


def test_check_criteria_invalid():
    with pytest.raises(ValueError):
        main.check_criteria(["non_existent_criteria"], "invalid")


def test_check_criteria_valid():
    try:
        main.check_criteria(["unclosed", "duplicate_nodes"], "invalid")
        main.check_criteria(["holes"], "problematic")
    except ValueError:
        pytest.fail("Unexpected ValueError for valid criteria")


def test_process_validation_valid_polygon_without_criteria():
    geometries = [
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [1, 0], [0, 0]]]}
    ]
    results = main.process_validation(geometries, [], [])
    assert not results["invalid"]
    assert not results["problematic"]


def test_process_validation_invalid_geometry():
    # unclosed
    geometries = [
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [1, 0]]]}
    ]  # Missing closing point
    invalid_criteria = ["unclosed"]
    results = main.process_validation(geometries, invalid_criteria, [])
    assert "unclosed" in results["invalid"]


def test_process_validation_multi_polygon():
    # Second geometry in Multipolygon and third geometry is unclosed
    geometries = [
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [1, 0], [0, 0]]]},
        {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0, 0], [2, 2], [2, 0], [0, 0]]],
                [[[0, 0], [1, 1], [1, 0]]],
            ],
        },
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [1, 0]]]},
    ]
    invalid_criteria = ["unclosed"]
    results = main.process_validation(geometries, invalid_criteria, [])
    assert results["invalid"]["unclosed"] == [1, 2]
    assert results["count_geometry_types"] == {"Polygon": 2, "MultiPolygon": 1}


def test_process_validation_error_no_type():
    # Test handling of geometry missing the 'type' field
    geometries = [{"coordinates": [[[0, 0], [1, 1], [1, 0], [0, 0]]]}]  # No type field
    with pytest.raises(ValueError):
        main.process_validation(geometries, [], [])


@patch("geojsonfix.main.check_criteria")
@patch("geojsonfix.main.get_geometries")
@patch("geojsonfix.main.process_validation")
def test_validate(mock_process_validation, mock_get_geometries, mock_check_criteria):
    """Ensure the validate function integrates them correctly."""
    mock_get_geometries.return_value = ("FeatureCollection", [])
    mock_process_validation.return_value = {"invalid": {}, "problematic": {}}

    geojson_input = {}  # Mock input
    results = main.validate(geojson_input)

    assert "invalid" in results
    assert "problematic" in results
    mock_check_criteria.assert_called()
    mock_get_geometries.assert_called_with(geojson_input)
    mock_process_validation.assert_called()


def test_validate_invalid():
    fc = read_geojson(
        "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson"
    )
    result = main.validate(fc)
    assert "duplicate_nodes" in result["invalid"]


def test_validate_valid():
    fc = read_geojson("./tests/examples_geojson/valid/simple_polygon.geojson")
    result = main.validate(fc)
    assert not result["invalid"]
    assert not result["problematic"]


@pytest.mark.skip()
def test_validate_countries():
    fc = read_geojson("./tests/examples_geojson/countries.geojson")
    result = main.validate(fc)
    assert len(result["invalid"]) == 0
    assert len(result["problematic"]["self_intersection"]) == 1
    assert result["problematic"]["crosses_antimeridian"] == [12, 59, 142]
    assert len(result["problematic"]["excessive_coordinate_precision"]) == 51
    assert result["problematic"]["holes"] == [181]
    assert len(result["problematic"]) == 4
    assert result["count_geometry_types"] == {"Polygon": 188, "MultiPolygon": 46}
