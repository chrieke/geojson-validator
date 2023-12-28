from shapely.geometry import shape

from .context import fixes_invalid, checks_invalid
from .fixtures_utils import read_geojson


def test_fix_unclosed():
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_unclosed_polygon.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_unclosed(geometry)
    fixed_geometry = fixes_invalid.fix_unclosed(geom)
    assert not checks_invalid.check_unclosed(fixed_geometry.__geo_interface__)


def test_fix_duplicate_nodes():
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_duplicate_nodes(geometry)
    fixed_geometry = fixes_invalid.fix_duplicate_nodes(geom)
    assert not checks_invalid.check_duplicate_nodes(fixed_geometry.__geo_interface__)


def test_fix_exterior_not_ccw():
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_exterior_ring_not_counterclockwise_winding_order.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_exterior_not_ccw(geom)
    fixed_geom = fixes_invalid.fix_exterior_not_ccw(geom)
    assert not checks_invalid.check_exterior_not_ccw(fixed_geom)


def test_fix_interior_not_cw():
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_interior_ring_not_clockwise_winding_order.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_interior_not_cw(geom)
    fixed_geom = fixes_invalid.fix_interior_not_cw(geom)
    assert not checks_invalid.check_interior_not_cw(fixed_geom)
