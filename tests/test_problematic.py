from shapely.geometry import shape

from .context import checks_problematic
from .fixtures_utils import read_geometry_of_geojson


def test_check_holes():
    geometry = read_geometry_of_geojson(
        "./tests/examples_geojson/problematic/polygon_has_holes.geojson"
    )
    geom = shape(geometry)
    problematic = checks_problematic.check_holes(geom)
    assert problematic


def test_check_self_intersection():
    geometry = read_geometry_of_geojson(
        "./tests/examples_geojson/problematic/polygon_selfintersection_small.geojson"
    )
    geom = shape(geometry)
    problematic = checks_problematic.check_self_intersection(geom)
    assert problematic


def test_check_excessive_coordinate_precision():
    geometry = read_geometry_of_geojson(
        "./tests/examples_geojson/problematic/excessive_coordinate_precision.geojson"
    )
    problematic = checks_problematic.check_excessive_coordinate_precision(geometry)
    assert problematic


def test_check_more_than_2d_coordinates():
    geometry = read_geometry_of_geojson(
        "./tests/examples_geojson/problematic/3d_coordinates.geojson"
    )
    problematic = checks_problematic.check_more_than_2d_coordinates(geometry)
    assert problematic


def test_check_crosses_antimeridian():
    geometry = read_geometry_of_geojson(
        "./tests/examples_geojson/problematic/geometry_crosses_the_antimeridian.geojson"
    )
    problematic = checks_problematic.check_crosses_antimeridian(geometry)
    assert problematic
