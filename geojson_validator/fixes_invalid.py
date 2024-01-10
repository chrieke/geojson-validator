from shapely.geometry import Polygon, LinearRing


# Needs manual check: check_less_three_unique_nodes
# Possible but problematic: check_outside_lat_lon_boundaries, check_inner_and_exterior_ring_intersect
def fix_unclosed(geom: Polygon):
    """Close the geometry by adding the first coordinate at the end if not closed."""
    # TODO Shapely closes anyway
    coords = list(geom.exterior.coords)
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    closed_polygon = Polygon(coords)
    return closed_polygon


def fix_duplicate_nodes(geom: Polygon):
    """Remove duplicate nodes from the geometry."""
    return geom.simplify(0)


def fix_exterior_not_ccw(geom: Polygon):
    """Reorder exterior ring to be counter-clockwise."""
    if not geom.exterior.is_ccw:
        geom = Polygon(list(geom.exterior.coords)[::-1])
    return geom


def fix_interior_not_cw(geom: Polygon):
    """Reorder any interior rings to be clockwise."""
    interiors = []
    exterior = LinearRing(geom.exterior)
    for interior in geom.interiors:
        if interior.is_ccw:
            interiors.append(LinearRing(interior.coords[::-1]))
        else:
            interiors.append(LinearRing(interior))
    return Polygon(exterior, interiors)
