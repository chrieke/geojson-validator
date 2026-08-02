import copy
from pathlib import Path
from unittest.mock import patch

import pytest


from geojson_validator import main
from .helpers import DATA, read_geojson


def test_py_typed_marker_shipped_with_package():
    assert (Path(main.__file__).parent / "py.typed").is_file()


def test_validate_schema_conformity_valid():
    fp = DATA / "valid/valid_featurecollection.geojson"
    fc = read_geojson(fp)
    errors = main.validate_structure(fc)
    assert not errors


def test_validate_schema_conformity_invalid():
    fp = DATA / "valid/valid_featurecollection.geojson"
    fc = read_geojson(fp)
    fc["features"][0]["type"] = "Some_weird_Feature_name"
    errors = main.validate_structure(fc)
    assert errors
    assert errors == {
        "Invalid 'type' member, is 'Some_weird_Feature_name', must be one of ['Feature']": {
            "path": ["/features/0/type"],
            "feature": [0],
        }
    }


@patch("geojson_validator.main.check_criteria")
@patch("geojson_validator.main.input_to_geojson")
@patch("geojson_validator.main.any_geojson_to_featurecollection")
@patch("geojson_validator.main.process_validation")
def test_validate_geometries_calls(
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


def test_validate__geometries_invalid():
    fc = read_geojson(DATA / "invalid_geometries/invalid_unclosed.geojson")
    result = main.validate_geometries(fc)
    assert "unclosed" in result["invalid"]


def test_validate_geometries_invalid_no_checks():
    fc = read_geojson(DATA / "invalid_geometries/invalid_unclosed.geojson")
    with pytest.raises(ValueError):
        main.validate_geometries(fc, criteria_invalid=None, criteria_problematic=[])


def test_validate_geometries_invalid_no_invalid_or_problematic_checks():
    fc = read_geojson(DATA / "invalid_geometries/invalid_unclosed.geojson")
    result = main.validate_geometries(fc, criteria_problematic=[])
    assert "unclosed" in result["invalid"]

    result = main.validate_geometries(fc, criteria_invalid=[])
    assert not result["invalid"]
    assert not result["problematic"]


def test_validate_geometries_does_not_mutate_input():
    fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "Point", "coordinates": [1.0, 2.0]},
            },
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
            },
        ],
    }
    fc_before = copy.deepcopy(fc)
    main.validate_geometries(fc)
    assert fc == fc_before


def test_validate__geometries_valid():
    fp = DATA / "valid/valid_featurecollection.geojson"
    fc = read_geojson(fp)
    for input_ in [fc, fp]:
        result = main.validate_geometries(input_)
        assert not result["invalid"]
        assert not result["problematic"]


@pytest.mark.skip(reason="online file")
def test_validate_geometries_url():
    url = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json"
    result = main.validate_geometries(url)
    assert len(result["invalid"]["exterior_not_ccw"]) == 16


geojson_geometry_type_examples = [
    ("Point", DATA / "valid/valid_geometry_point.geojson"),
    ("MultiPoint", DATA / "valid/valid_geometry_multipoint.geojson"),
    ("LineString", DATA / "valid/valid_geometry_linestring.geojson"),
    (
        "MultiLineString",
        DATA / "valid/valid_geometry_multilinestring.geojson",
    ),
    ("Polygon", DATA / "valid/valid_geometry_polygon.geojson"),
    ("MultiPolygon", DATA / "valid/valid_geometry_multipolygon.geojson"),
    (
        "GeometryCollection",
        DATA / "valid/valid_geometry_geometrycollection.geojson",
    ),
]


@pytest.mark.parametrize("geometry_type, file_path", geojson_geometry_type_examples)
def test_validate_geometries_valid_all_geometry_types(geometry_type, file_path):
    fc = read_geojson(file_path)
    results = main.validate_geometries(fc)
    assert not results["invalid"]
    assert not results["problematic"]
    assert results["count_geometry_types"] == {geometry_type: 1}
    assert not results["skipped_validation"]


def test_validate_geometries_runs_all_normal_files(
    all_normal_geojson_files,
):
    ### All test files for invalid/probelamtic/valid geometry checks
    for file_path in all_normal_geojson_files:
        assert file_path.exists()
        print(file_path.name)
        if file_path.name not in [
            "invalid_incorrect_geometry_data_type.geojson",  # shapely issue
            "valid_featurecollection_empty_features.geojson",  # skipped
        ]:  # schema checks
            fc = read_geojson(file_path)
            results = main.validate_geometries(fc)

            assert results["count_geometry_types"] or results["skipped_validation"]


def test_validations_raise_bad_filepath():
    filepath = "abc.geojson"
    with pytest.raises(FileNotFoundError):
        main.validate_structure(filepath)
    with pytest.raises(FileNotFoundError):
        main.validate_geometries(filepath)


def test_fix_valid():
    fp = DATA / "valid/valid_featurecollection.geojson"
    fc = read_geojson(fp)
    fixed_fc = main.fix_geometries(fc)
    assert fixed_fc["type"] == "FeatureCollection"
    assert fc == fixed_fc


def test_fix_invalid():
    fp = DATA / "invalid_geometries/invalid_unclosed.geojson"
    fc = read_geojson(fp)
    fixed_fc = main.fix_geometries(fc)
    assert fixed_fc["type"] == "FeatureCollection"
    assert fc != fixed_fc


@pytest.mark.parametrize("optional", [None, [], ("duplicate_nodes",)])
def test_fix_geometries_optional_argument_types(optional):
    fc = read_geojson(DATA / "invalid_geometries/invalid_unclosed.geojson")
    fixed_fc = main.fix_geometries(fc, optional=optional)
    assert fixed_fc["type"] == "FeatureCollection"


def test_fix_geometries_optional_single_string_raises():
    fc = read_geojson(DATA / "invalid_geometries/invalid_unclosed.geojson")
    with pytest.raises(ValueError, match="must be a list of criteria names"):
        main.fix_geometries(fc, optional="duplicate_nodes")
