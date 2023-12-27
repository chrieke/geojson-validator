import json
from pathlib import Path

import pytest
from shapely.geometry import shape

from .context import geometry_utils
from .fixtures_utils import read_geojson


def test_read_file():
    filepath = "./tests/examples_geojson/valid/simple_polygon.geojson"
    geojson_input = geometry_utils.read_file(filepath)
    assert isinstance(geojson_input, dict)


def test_get_geometries_file():
    fp = "./tests/examples_geojson/valid/simple_polygon.geojson"
    for f in [fp, Path(fp)]:
        type_, geometries = geometry_utils.get_geometries(f)
        assert type_ == "FeatureCollection"
        assert isinstance(geometries, list)
        assert isinstance(geometries[0], dict)


def test_get_geometries_shapely():
    fp = "./tests/examples_geojson/valid/simple_polygon.geojson"
    geom = shape(read_geojson(fp, geometries=True))
    type_, geometries = geometry_utils.get_geometries(geom)
    assert type_ == "Polygon"


def test_get_geometries_geojson_feature_collection():
    fp_geojson = "./tests/examples_geojson/valid/simple_polygon.geojson"
    fc = read_geojson(fp_geojson)
    for k, v in {
        "FeatureCollection": fc,
        "Feature": fc["features"][0],
        "Polygon": fc["features"][0]["geometry"],
    }.items():
        type_, geometries = geometry_utils.get_geometries(v)
        assert type_ == k
        assert isinstance(geometries, list)
        assert isinstance(geometries[0], dict)


def test_get_geometries_invalid_input_type():
    for x in [[], set(), TypeError]:  # random other objects
        with pytest.raises(ValueError):
            geometry_utils.get_geometries(x)


def test_get_geometries_invalid_geojson_type():
    with pytest.raises(ValueError):
        geometry_utils.get_geometries({"type": "InvalidGeoJSONType"})
