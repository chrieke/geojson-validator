from shapely.geometry import Polygon
from shapely.validation import explain_validity

from .geometry_utils import coordinate_arrays


def check_holes(geom: Polygon) -> bool:
    """Return True if the geometry has holes (interior rings)."""
    return len(geom.interiors) > 0


def check_self_intersection(geom: Polygon) -> bool:
    """Return True if the geometry is self-intersecting."""
    # TODO: Shapely independent?
    self_intersection = False
    if not geom.is_valid:
        self_intersection = "Self-intersection" in explain_validity(geom)
    return self_intersection


def check_inner_and_exterior_ring_intersect(geom: Polygon) -> bool:
    """Return True if any interior ring intersects the exterior ring in more than a single touching point."""
    # Rings touching at a single point are allowed, line overlaps and crossings are not.
    shell = Polygon(geom.exterior)
    for interior in geom.interiors:
        intersection = geom.exterior.intersection(interior)
        if not intersection.is_empty and intersection.geom_type != "Point":
            return True
        # A hole touching at a single point but lying outside the shell is not acceptable.
        if not shell.covers(interior):
            return True
    return False


def check_duplicate_nodes(geometry: dict) -> bool:
    """Return True if there are duplicate nodes, excluding the acceptable duplicate of a closed ring."""
    for coords in coordinate_arrays(geometry):
        if not coords:
            continue
        unique_coords = set(map(tuple, coords))
        has_duplicates = len(unique_coords) < len(coords)
        is_closed_ring = coords[0] == coords[-1]
        only_closed_ring_duplicate = (
            is_closed_ring and len(unique_coords) == len(coords) - 1
        )
        if has_duplicates and not only_closed_ring_duplicate:
            return True
    return False


def check_excessive_coordinate_precision(geometry: dict, precision=6) -> bool:
    """Return True if any coordinate has more than `precision` decimal places."""
    return any(
        round(value, precision) != value
        for coords in coordinate_arrays(geometry)
        for position in coords
        for value in position
    )


def check_excessive_vertices(
    geometry: dict,
) -> bool:
    """Return True if geometry has more than 999 vertices in total"""
    return sum(len(coords) for coords in coordinate_arrays(geometry)) > 999


def check_3d_coordinates(geometry: dict) -> bool:
    """Return True if any coordinate is more than 2D."""
    return any(
        len(position) > 2
        for coords in coordinate_arrays(geometry)
        for position in coords
    )


def check_outside_lat_lon_boundaries(geometry: dict) -> bool:
    """Return True if not all coordinates are within the standard lat/lon boundaries."""
    return not all(
        -180 <= position[0] <= 180 and -90 <= position[1] <= 90
        for coords in coordinate_arrays(geometry)
        for position in coords
    )


def check_crosses_antimeridian(geometry: dict) -> bool:
    """Return True if the geometry crosses the antimeridian (meridian at 180 longitude)."""
    for coords in coordinate_arrays(geometry):
        for start, end in zip(coords, coords[1:]):
            # Normalize longitudes to -180 to 180 range
            norm_start_lon = (start[0] + 180) % 360 - 180
            norm_end_lon = (end[0] + 180) % 360 - 180

            # Check for longitude switch indicating crossing
            if abs(norm_end_lon - norm_start_lon) > 180:
                return True
    return False
