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


def test_process_validation_error_no_type():
    # Test handling of geometry missing the 'type' field
    geometries = [{"coordinates": [[[0, 0], [1, 1], [1, 0], [0, 0]]]}]  # No type field
    with pytest.raises(ValueError):
        main.process_validation(geometries, [], [])


@patch("geojson_validator.main.check_criteria")
@patch("geojson_validator.main.get_geometries")
@patch("geojson_validator.main.process_validation")
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
    fp = "./tests/examples_geojson/valid/simple_polygon.geojson"
    fc = read_geojson(fp)
    for input_ in [fc, fp]:
        result = main.validate(input_)
        assert not result["invalid"]
        assert not result["problematic"]


@pytest.mark.skip(reason="online file")
def test_validate_url():
    url = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json"
    result = main.validate(url)
    assert len(result["invalid"]["exterior_not_ccw"]) == 16


geojson_examples = [
    ("Point", "./tests/examples_geojson/valid/simple_point.geojson"),
    # ("MultiPoint", "./tests/examples_geojson/valid/simple_multipoint.geojson"),
    ("LineString", "./tests/examples_geojson/valid/simple_linestring.geojson"),
    (
        "MultiLineString",
        "./tests/examples_geojson/valid/simple_multilinestring.geojson",
    ),
    # ("Polygon", "./tests/examples_geojson/valid/simple_polygon.geojson"),
    # ("MultiPolygon", "./tests/examples_geojson/valid/simple_multipolygon.geojson"),
]


# TODO: Linestring
@pytest.mark.parametrize("geometry_type, file_path", geojson_examples)
def test_process_validation_valid_all_geometry_types(geometry_type, file_path):
    fc = read_geojson(
        file_path
    )  # read_geojson function should be defined in main module
    results = main.validate(
        fc
    )  # validate function should process the feature collection and return results
    assert not results["invalid"]
    assert not results["problematic"]
    assert results["count_geometry_types"] == {geometry_type: 1}
    # TODO: Check that not skipped
    assert not results["skipped_validation"]


def test_process_validation_multiple_types():
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
