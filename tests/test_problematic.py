import json
from shapely.geometry import shape

from .context import checks_problematic


def read_geojson_geometry(file_name: str):
    geojson_fp = f"./tests/examples_geojson/valid_but_problematic/{file_name}"
    with open(geojson_fp) as f:
        gj = json.load(f)
    return gj["features"][0]["geometry"]


def test_check_holes():
    geometry = read_geojson_geometry("polygon_has_holes.geojson")
    geom = shape(geometry)
    problematic = checks_problematic.check_holes(geom)
    assert problematic


def test_check_self_intersection():
    geometry = read_geojson_geometry("polygon_selfintersection_small.geojson")
    geom = shape(geometry)
    problematic = checks_problematic.check_self_intersection(geom)
    assert problematic


def test_check_excessive_coordinate_precision():
    geometry = read_geojson_geometry("excessive_coordinate_precision.geojson")
    problematic = checks_problematic.check_excessive_coordinate_precision(geometry)
    assert problematic


def test_check_more_than_2d_coordinates():
    geometry = read_geojson_geometry("3d_coordinates.geojson")
    problematic = checks_problematic.check_more_than_2d_coordinates(geometry)
    assert problematic


def test_check_crosses_antimeridian():
    geometry = read_geojson_geometry("geometry_crosses_the_antimeridian.geojson")
    problematic = checks_problematic.check_crosses_antimeridian(geometry)
    assert problematic
