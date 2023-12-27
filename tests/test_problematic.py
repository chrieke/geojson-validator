from shapely.geometry import shape

from .context import checks_problematic
from .fixtures_utils import read_geojson


def test_check_holes():
    geometry = read_geojson(
        "./tests/examples_geojson/problematic/polygon_has_holes.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    problematic = checks_problematic.check_holes(geom)
    assert problematic


def test_check_self_intersection():
    geometry = read_geojson(
        "./tests/examples_geojson/problematic/polygon_selfintersection_small.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    problematic = checks_problematic.check_self_intersection(geom)
    assert problematic


def test_check_excessive_coordinate_precision():
    geometry = read_geojson(
        "./tests/examples_geojson/problematic/excessive_coordinate_precision.geojson",
        geometries=True,
    )
    problematic = checks_problematic.check_excessive_coordinate_precision(geometry)
    assert problematic


def test_check_excessive_coordinate_precision_no_after_comma_succeds():
    geometry_no_after_comma = {
        "coordinates": [[[-77, 26.0], [-77.17255, 25], [-77, 26]]],
        "type": "Polygon",
    }
    checks_problematic.check_excessive_coordinate_precision(geometry_no_after_comma)


def test_check_more_than_2d_coordinates():
    geometry = read_geojson(
        "./tests/examples_geojson/problematic/3d_coordinates.geojson", geometries=True
    )
    problematic = checks_problematic.check_more_than_2d_coordinates(geometry)
    assert problematic


def test_check_crosses_antimeridian():
    geometry = read_geojson(
        "./tests/examples_geojson/problematic/geometry_crosses_the_antimeridian.geojson",
        geometries=True,
    )
    problematic = checks_problematic.check_crosses_antimeridian(geometry)
    assert problematic
