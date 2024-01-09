from pathlib import Path

import pytest
from shapely.geometry import shape, Point, LineString

from .context import geometry_utils
from .fixtures import read_geojson


def test_read_geojson_file_or_url_filepath():
    filepath = "./tests/data/valid/valid_featurecollection.geojson"
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


def test_input_to_geojson_file():
    fp = "./tests/data/valid/valid_featurecollection.geojson"
    for f in [fp, Path(fp), shape(read_geojson(fp, geometries=True))]:
        geojson_data = geometry_utils.input_to_geojson(f)
        assert geojson_data["type"]


def test_input_to_geojson_invalid_input_type():
    for x in [[], set(), TypeError]:  # random other objects
        with pytest.raises(ValueError):
            geometry_utils.input_to_geojson(x)


def test_any_geojson_to_featurecollection_various_geojson_types():
    fp_geojson = "./tests/data/valid/valid_featurecollection.geojson"
    fc_in = read_geojson(fp_geojson)
    for geojson_element in [
        fc_in,
        fc_in["features"][0],
        fc_in["features"][0]["geometry"],
    ]:
        fc_out = geometry_utils.any_geojson_to_featurecollection(geojson_element)
        assert fc_out["type"] == "FeatureCollection"


def test_any_geojson_to_featurecollection_invalid_geojson_type():
    with pytest.raises(ValueError):
        geometry_utils.any_geojson_to_featurecollection({"type": "InvalidGeoJSONType"})


def test_prepare_geometries_for_checks():
    point_geojson = {"type": "Point", "coordinates": [10, 20]}
    modified_point, shapely_point = geometry_utils.prepare_geometries_for_checks(
        point_geojson
    )
    assert modified_point["coordinates"] == [[[10, 20]]]
    assert isinstance(shapely_point, Point)

    linestring_geojson = {"type": "LineString", "coordinates": [[10, 20], [30, 40]]}
    (
        modified_linestring,
        shapely_linestring,
    ) = geometry_utils.prepare_geometries_for_checks(linestring_geojson)
    assert modified_linestring["coordinates"] == [[[10, 20], [30, 40]]]
    assert isinstance(shapely_linestring, LineString)
