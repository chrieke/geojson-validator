from shapely.geometry import shape

from .context import fixes, checks_invalid, checks_problematic
from .fixtures import read_geojson


def test_fix_unclosed():
    geometry = read_geojson(
        "./tests/data/invalid_geometries/invalid_unclosed.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_unclosed(geometry)
    fixed_geometry = fixes.fix_unclosed(geom)
    assert not checks_invalid.check_unclosed(fixed_geometry.__geo_interface__)


def test_fix_duplicate_nodes():
    geometry = read_geojson(
        "./tests/data/problematic_geometries/problematic_duplicate_nodes.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_problematic.check_duplicate_nodes(geometry)
    fixed_geometry = fixes.fix_duplicate_nodes(geom)
    assert not checks_problematic.check_duplicate_nodes(
        fixed_geometry.__geo_interface__
    )


def test_fix_exterior_not_ccw():
    geometry = read_geojson(
        "./tests/data/invalid_geometries/invalid_exterior_not_ccw.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_exterior_not_ccw(geom)
    fixed_geom = fixes.fix_exterior_not_ccw(geom)
    assert not checks_invalid.check_exterior_not_ccw(fixed_geom)


def test_fix_interior_not_cw():
    geometry = read_geojson(
        "./tests/data/invalid_geometries/invalid_interior_not_cw.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_interior_not_cw(geom)
    fixed_geom = fixes.fix_interior_not_cw(geom)
    assert not checks_invalid.check_interior_not_cw(fixed_geom)
