from shapely.geometry import shape
import pytest

from .context import checks_invalid
from .fixtures import read_geojson


@pytest.fixture(scope="session")
def valid_geometry():
    geojson_fp = "./tests/examples_geojson/valid/simple_polygon.geojson"
    return read_geojson(geojson_fp, geometries=True)


def test_check_unclosed(valid_geometry):
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_unclosed_polygon.geojson",
        geometries=True,
    )
    assert checks_invalid.check_unclosed(geometry)
    assert not checks_invalid.check_unclosed(valid_geometry)


def test_check_duplicate_nodes(valid_geometry):
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson",
        geometries=True,
    )
    assert checks_invalid.check_duplicate_nodes(geometry)
    assert not checks_invalid.check_duplicate_nodes(valid_geometry)


def test_less_three_unique_nodes(valid_geometry):
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_has_less_than_three_unique_nodes.geojson",
        geometries=True,
    )
    assert checks_invalid.check_less_three_unique_nodes(geometry)
    assert not checks_invalid.check_less_three_unique_nodes(valid_geometry)


def test_check_exterior_not_ccw(valid_geometry):
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_exterior_ring_not_counterclockwise_winding_order.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_exterior_not_ccw(geom)
    assert not checks_invalid.check_exterior_not_ccw(shape(valid_geometry))


def test_check_interior_not_cw(valid_geometry):
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_interior_ring_not_clockwise_winding_order.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_interior_not_cw(geom)
    assert not checks_invalid.check_interior_not_cw(shape(valid_geometry))


def test_check_inner_and_exterior_ring_intersect(valid_geometry):
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_inner_and_exterior_ring_cross.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_inner_and_exterior_ring_intersect(geom)
    assert not checks_invalid.check_inner_and_exterior_ring_intersect(
        shape(valid_geometry)
    )


def test_check_outside_lat_lon_boundaries(valid_geometry):
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/outside_lat_lon_boundaries.geojson",
        geometries=True,
    )
    assert checks_invalid.check_outside_lat_lon_boundaries(geometry)
    assert not checks_invalid.check_outside_lat_lon_boundaries(valid_geometry)
