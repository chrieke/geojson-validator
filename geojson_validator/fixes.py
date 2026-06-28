from shapely import remove_repeated_points
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient


# Needs manual check: check_less_three_unique_nodes
# Possible but problematic: check_outside_lat_lon_boundaries, check_inner_and_exterior_ring_intersect
def fix_unclosed(geom: Polygon):
    """Close the geometry by adding the first coordinate at the end if not closed."""
    # Constructing a shapely Polygon already closes the ring, so by the time a geometry
    # reaches this function it is closed. Kept for explicit, name-based fix dispatch.
    return geom


def fix_exterior_not_ccw(geom: Polygon):
    """Orient the polygon to the GeoJSON right-hand rule (exterior CCW, interiors CW)."""
    return orient(geom, sign=1.0)


def fix_interior_not_cw(geom: Polygon):
    """Orient the polygon to the GeoJSON right-hand rule (exterior CCW, interiors CW)."""
    return orient(geom, sign=1.0)


def fix_duplicate_nodes(geom: Polygon):
    """Remove consecutive duplicate nodes, preserving meaningful (collinear) vertices."""
    # shapely.remove_repeated_points only drops repeated points; unlike simplify(0) it does
    # not collapse collinear vertices.
    return remove_repeated_points(geom, 0)


# def fix_excessive_coordinate_precision(geom: Polygon):
#     # TODO: Could also be applied to non polygon
#     pass
