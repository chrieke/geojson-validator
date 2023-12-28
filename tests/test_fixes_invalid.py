from shapely.geometry import shape

from .context import fixes_invalid, checks_invalid
from .fixtures_utils import read_geojson


def test_fix_interior_not_cw():
    geometry = read_geojson(
        "./tests/examples_geojson/invalid/polygon_interior_ring_not_clockwise_winding_order.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_interior_not_cw(geom)
    fixed_geom = fixes_invalid.fix_interior_not_cw(geom)
    assert not checks_invalid.check_interior_not_cw(fixed_geom)
