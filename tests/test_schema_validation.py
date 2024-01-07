from pathlib import Path

import pytest

from .context import schema_validation
from .fixtures import read_geojson


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
    assert errors == [
        {"message": "Missing 'type'", "line": 3},
        {"message": "Missing 'type'", "line": 4},
        {
            "message": '"geometry" member should be an object, but is a list instead',
            "line": 17,
        },
    ]


# TODO: This is actually allowed in geojson spec
def test_schema_validation_geometry_None():
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": None,
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
    assert errors == [
        {
            "message": '"geometry" member should be an object, but is a NoneType instead',
            "line": 4,
        },
    ]


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


@pytest.fixture(scope="module")
def geojson_examples_all_valid_normal_files():
    base_path = Path("tests/examples_geojson/valid")
    return list(base_path.rglob("*.geojson"))


def test_schema_validation_all_normal_files(geojson_examples_all_valid_normal_files):
    ### All test files for invalid/probelamtic/valid geometry checks
    for file_path in geojson_examples_all_valid_normal_files:
        fc = read_geojson(file_path)
        errors = schema_validation.GeoJsonLint().lint(fc)

        print(file_path.name)
        assert not errors
