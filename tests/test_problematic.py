import json
from shapely.geometry import shape

from .context import checks_problematic


def test_check_holes():
    geojson_fp = "./tests/examples_geojson/valid_but_problematic/polygon_has_holes.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geom = shape(gj["features"][0]["geometry"])
    problematic = checks_problematic.check_holes(geom)
    assert problematic


def test_check_self_intersection():
    geojson_fp = "./tests/examples_geojson/valid_but_problematic/polygon_selfintersection_small.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geom = shape(gj["features"][0]["geometry"])
    problematic = checks_problematic.check_self_intersection(geom)
    assert problematic


def test_check_excessive_coordinate_precision():
    geojson_fp = "./tests/examples_geojson/valid_but_problematic/excessive_coordinate_precision.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geometry = gj["features"][0]["geometry"]
    problematic = checks_problematic.check_excessive_coordinate_precision(geometry)
    assert problematic


def test_check_more_than_2d_coordinates():
    geojson_fp = "./tests/examples_geojson/valid_but_problematic/3d_coordinates.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geometry = gj["features"][0]["geometry"]
    problematic = checks_problematic.check_more_than_2d_coordinates(geometry)
    assert problematic


def test_check_crosses_antimeridian():
    geojson_fp = "./tests/examples_geojson/valid_but_problematic/geometry_crosses_the_antimeridian.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geometry = gj["features"][0]["geometry"]
    problematic = checks_problematic.check_crosses_antimeridian(geometry)
    assert problematic
