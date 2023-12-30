from unittest.mock import patch

import pytest

from .fixtures import read_geojson
from .context import main


def test_validate_geojson_schema_conformity_valid():
    fp = "./tests/examples_geojson/valid/simple_polygon.geojson"
    fc = read_geojson(fp)
    result, message = main.validate_schema(fc)
    assert result
    assert message is None


def test_validate_geojson_schema_conformity_invalid():
    fp = "./tests/examples_geojson/valid/simple_polygon.geojson"
    fc = read_geojson(fp)
    fc["features"][0]["type"] = "NotFeature"
    result, message = main.validate_schema(fc)
    assert not result
    assert message == "'NotFeature' is not one of ['Feature']"
    print(message)


@patch("geojson_validator.main.check_criteria")
@patch("geojson_validator.main.input_to_geojson")
@patch("geojson_validator.main.any_geojson_to_featurecollection")
@patch("geojson_validator.main.process_validation")
def test_validate(
    mock_process_validation,
    mock_input_to_geojson,
    mock_any_geojson_to_featurecollection,
    mock_check_criteria,
):
    """Ensure the validate function integrates them correctly."""
    mock_input_to_geojson.return_value = {
        "type": "FeatureCollection",
        "features": [],
    }
    mock_any_geojson_to_featurecollection.return_value = {
        "type": "FeatureCollection",
        "features": [],
    }
    mock_process_validation.return_value = {"invalid": {}, "problematic": {}}

    geojson_input = {}  # Mock input
    results = main.validate_geometries(geojson_input)

    assert "invalid" in results
    assert "problematic" in results
    mock_check_criteria.assert_called()
    mock_input_to_geojson.assert_called()
    mock_any_geojson_to_featurecollection.assert_called()
    mock_process_validation.assert_called()


def test_validate_invalid():
    fc = read_geojson(
        "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson"
    )
    result = main.validate_geometries(fc)
    assert "duplicate_nodes" in result["invalid"]


def test_validate_invalid_no_checks():
    fc = read_geojson(
        "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson"
    )
    with pytest.raises(ValueError):
        main.validate_geometries(fc, criteria_invalid=None, criteria_problematic=[])


def test_validate_invalid_no_invalid_or_problematic_checks():
    fc = read_geojson(
        "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson"
    )
    result = main.validate_geometries(fc, criteria_problematic=[])
    assert "duplicate_nodes" in result["invalid"]

    result = main.validate_geometries(fc, criteria_invalid=[])
    assert not result["invalid"]
    assert not result["problematic"]


def test_validate_valid():
    fp = "./tests/examples_geojson/valid/simple_polygon.geojson"
    fc = read_geojson(fp)
    for input_ in [fc, fp]:
        result = main.validate_geometries(input_)
        assert not result["invalid"]
        assert not result["problematic"]


@pytest.mark.skip(reason="online file")
def test_validate_url():
    url = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json"
    result = main.validate_geometries(url)
    assert len(result["invalid"]["exterior_not_ccw"]) == 16


geojson_examples = [
    ("Point", "./tests/examples_geojson/valid/simple_point.geojson"),
    ("MultiPoint", "./tests/examples_geojson/valid/simple_multipoint.geojson"),
    ("LineString", "./tests/examples_geojson/valid/simple_linestring.geojson"),
    (
        "MultiLineString",
        "./tests/examples_geojson/valid/simple_multilinestring.geojson",
    ),
    ("Polygon", "./tests/examples_geojson/valid/simple_polygon.geojson"),
    ("MultiPolygon", "./tests/examples_geojson/valid/simple_multipolygon.geojson"),
]


@pytest.mark.parametrize("geometry_type, file_path", geojson_examples)
def test_process_validation_valid_all_geometry_types(geometry_type, file_path):
    fc = read_geojson(
        file_path
    )  # read_geojson function should be defined in main module
    results = main.validate_geometries(
        fc
    )  # validate function should process the feature collection and return results
    assert not results["invalid"]
    assert not results["problematic"]
    assert results["count_geometry_types"] == {geometry_type: 1}
    assert not results["skipped_validation"]


@pytest.mark.skip(reason="1mb file")
def test_validate_countries_dataset():
    fc = read_geojson("./tests/examples_geojson/countries.geojson")
    result = main.validate_geometries(fc)
    assert len(result["invalid"]) == 0
    assert len(result["problematic"]["self_intersection"]) == 1
    assert result["problematic"]["crosses_antimeridian"] == [
        {12: [7]},
        {59: [1]},
        {142: [3, 9]},
    ]
    assert len(result["problematic"]["excessive_coordinate_precision"]) == 51
    assert result["problematic"]["holes"] == [181]
    assert len(result["problematic"]) == 4
    assert result["count_geometry_types"] == {"Polygon": 188, "MultiPolygon": 46}


@pytest.mark.skip(reason="Takes 10sec, 20mb file")
def test_validate_buildings_dataset():
    fc = read_geojson("./tests/examples_geojson/buildings.json")
    result = main.validate_geometries(fc)
    assert len(result["problematic"]["excessive_coordinate_precision"]) == 66510
    assert result["count_geometry_types"]["Polygon"] == 66510


def test_fix_valid():
    fp = "./tests/examples_geojson/valid/simple_polygon.geojson"
    fc = read_geojson(fp)
    fixed_fc = main.fix_geometries(fc)
    assert fixed_fc["type"] == "FeatureCollection"
    assert fc == fixed_fc


def test_fix_invvalid():
    fp = "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson"
    fc = read_geojson(fp)
    fixed_fc = main.fix_geometries(fc)
    assert fixed_fc["type"] == "FeatureCollection"
    assert fc != fixed_fc
