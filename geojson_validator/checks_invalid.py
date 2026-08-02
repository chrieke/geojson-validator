from shapely.geometry import Polygon

from .geometry_utils import coordinate_arrays


def check_unclosed(geometry: dict) -> bool:
    """Return True if any ring is not closed (first coordinate != last coordinate)."""
    # This needs to check the original json string, as shapely or geopandas automatically close.
    return any(ring and ring[0] != ring[-1] for ring in coordinate_arrays(geometry))


def check_less_three_unique_nodes(geometry: dict) -> bool:
    """Return True if any ring has fewer than three unique nodes."""
    return any(len(set(map(tuple, ring))) < 3 for ring in coordinate_arrays(geometry))


def check_exterior_not_ccw(geom: Polygon) -> bool:
    """Return True if the exterior ring is not counter-clockwise."""
    return not geom.exterior.is_ccw


def check_interior_not_cw(geom: Polygon) -> bool:
    """Return True if any interior ring is counter-clockwise."""
    return any(interior.is_ccw for interior in geom.interiors)
