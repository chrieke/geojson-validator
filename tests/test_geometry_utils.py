from pathlib import Path

import pytest
from shapely.geometry import shape, Point

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


def test_coordinate_arrays():
    point_geojson = {"type": "Point", "coordinates": [10, 20]}
    assert geometry_utils.coordinate_arrays(point_geojson) == [[[10, 20]]]
    # Does not modify the input geometry
    assert point_geojson["coordinates"] == [10, 20]

    linestring_geojson = {"type": "LineString", "coordinates": [[10, 20], [30, 40]]}
    assert geometry_utils.coordinate_arrays(linestring_geojson) == [
        [[10, 20], [30, 40]]
    ]

    polygon_coordinates = [
        [[0, 0], [10, 0], [10, 10], [0, 0]],
        [[1, 1], [2, 1], [2, 2], [1, 1]],
    ]
    polygon_geojson = {"type": "Polygon", "coordinates": polygon_coordinates}
    assert geometry_utils.coordinate_arrays(polygon_geojson) == polygon_coordinates


def test_to_shapely_or_none():
    shapely_point = geometry_utils.to_shapely_or_none(
        {"type": "Point", "coordinates": [10, 20]}
    )
    assert isinstance(shapely_point, Point)

    mixed_dimensions = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [1, 0], [1, 1, 5], [0, 1], [0, 0]]],
    }
    assert geometry_utils.to_shapely_or_none(mixed_dimensions) is None
