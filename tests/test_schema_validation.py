from pathlib import Path

import pytest

from .context import schema_validation
from .fixtures import read_geojson

# pylint: disable=unused-import
from .fixtures import (
    fixture_geojson_examples_all_normal_files,
)


def test_schema_validation_invalid_various_issues():
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "geometry": {"coordinates": [81.2072495864164, 13.0187039189613]},
                "properties": {"assetStatus": "FULL", "id": 1747, "item": "53 Trailer"},
            },
            {
                "type": "Feature",
                "geometry": [83.2072495864164, 14.0187039189613],
                "properties": {
                    "assetStatus": "EMPTY",
                    "id": 1746,
                    "item": "53 Trailer",
                },
            },
        ],
    }
    errors = schema_validation.GeoJsonLint().lint(geojson_data)
    assert errors
    assert errors == {
        "Missing 'type' member": {
            "path": ["/features/0", "/features/0/geometry"],
            "feature": [0, 0],
        },
        '"geometry" member must be an object/dictionary, but is a list instead': {
            "path": ["/features/1/geometry"],
            "feature": [1],
        },
    }


def test_schema_validation_crs_member_optional_check():
    geojson_data = {
        "type": "FeatureCollection",
        "crs": {
            "type": "crs-name",
            "properties": {"name": "urn:ogc:def:crs:EPSG::32632"},
        },
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [81.2072495864164, 13.0187039189613],
                },
                "properties": {},
            },
        ],
    }
    assert not schema_validation.GeoJsonLint().lint(geojson_data)
    errors = schema_validation.GeoJsonLint(check_crs=True).lint(geojson_data)
    assert errors[list(errors.keys())[0]]["path"] == ["/crs"]


def test_schema_validation_quotes_around_geometry():
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": '{"type":"Polygon","coordinates":[[[6.66079022243348,51.140794993202],'
                "[6.66080873391236,51.1407981018504],[6.66079022243348,51.140794993202]]]}",
                "properties": {},
            }
        ],
    }

    errors = schema_validation.GeoJsonLint().lint(geojson_data)
    assert errors


def test_schema_validation_all_normal_files(fixture_geojson_examples_all_normal_files):
    ### All test files with correct schema (from invalid/probelamtic/valid geometry checks)
    for file_path in fixture_geojson_examples_all_normal_files:
        assert file_path.exists()
        if file_path.name not in [
            "invalid_incorrect_geometry_data_type.geojson"  # too nested
        ]:
            fc = read_geojson(file_path)
            print(file_path.name)
            errors = schema_validation.GeoJsonLint().lint(fc)
            assert not errors


@pytest.fixture(scope="module")
def geojson_invalid_schema():
    base_path = Path("tests/data/invalid_schema")
    return list(base_path.rglob("*.geojson"))


def test_schema_validation_all_invalid_schema_files(geojson_invalid_schema):
    ### All invalid schema test files
    for file_path in geojson_invalid_schema:
        print(file_path.name)
        if file_path.name not in [
            "invalid_featurecollection_crs_defined.geojson",
            "invalid_geometry_geometrycollection_nested.geojson",  # TODO, but is should not be
            "invalid_geometry_geometrycollection_single.geojson",  # TODO, but is should
        ]:
            fc = read_geojson(file_path)
            errors = schema_validation.GeoJsonLint().lint(fc)

            assert errors


# def test_justnow(geojson_invalid_schema):
#     fc = {"type": "GeometryCollection", "geometries": [False]}
#
#     errors = schema_validation.GeoJsonLint().lint(fc)
#
#     assert not errors
