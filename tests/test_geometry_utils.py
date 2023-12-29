from pathlib import Path

import pytest
from shapely.geometry import shape

from .context import geometry_utils
from .fixtures_utils import read_geojson


def test_read_geojson_file_or_url_filepath():
    filepath = "./tests/examples_geojson/valid/simple_polygon.geojson"
    fc = geometry_utils.read_geojson_file_or_url(filepath)
    assert isinstance(fc, dict)


def test_read_geojson_file_or_url_url():
    filepath = (
        "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/"
        "2_bundeslaender/1_sehr_hoch.geo.json"
    )
    fc = geometry_utils.read_geojson_file_or_url(filepath)
    assert isinstance(fc, dict)
    assert fc["type"] == "FeatureCollection"


def test_input_to_featurecollection_file():
    fp = "./tests/examples_geojson/valid/simple_polygon.geojson"
    for f in [fp, Path(fp)]:
        fc = geometry_utils.input_to_featurecollection(f)
        assert fc["type"] == "FeatureCollection"
        assert isinstance(fc, dict)
        assert isinstance(fc["features"][0], dict)


def test_input_to_featurecollection_shapely():
    fp = "./tests/examples_geojson/valid/simple_polygon.geojson"
    geom = shape(read_geojson(fp, geometries=True))
    fc = geometry_utils.input_to_featurecollection(geom)
    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 1
    assert fc["features"][0]["geometry"]["type"] == "Polygon"


def test_input_to_featurecollection_various_geojson_types():
    fp_geojson = "./tests/examples_geojson/valid/simple_polygon.geojson"
    fc_in = read_geojson(fp_geojson)
    for i in [fc_in, fc_in["features"][0], fc_in["features"][0]["geometry"]]:
        fc_out = geometry_utils.input_to_featurecollection(i)
        assert fc_out["type"] == "FeatureCollection"


def test_input_to_featurecollection_invalid_input_type():
    for x in [[], set(), TypeError]:  # random other objects
        with pytest.raises(ValueError):
            geometry_utils.input_to_featurecollection(x)


def test_get_geometries_invalid_geojson_type():
    with pytest.raises(ValueError):
        geometry_utils.input_to_featurecollection({"type": "InvalidGeoJSONType"})
