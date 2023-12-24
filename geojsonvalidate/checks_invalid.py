from shapely.geometry import Polygon


def check_unclosed(geometry: dict) -> bool:
    """Return True if the geometry is not closed (first coordinate != last coordinate)."""
    # This needs to check the original json string, as shapely or geopandas automatically close.
    coords = geometry["coordinates"][0]
    return coords[0] != coords[-1]


def check_duplicate_nodes(geometry: dict) -> bool:
    """Return True if there are duplicate nodes, excluding the acceptable duplicate of a closed ring."""
    coords = geometry["coordinates"][0]
    unique_coords = set(map(tuple, coords))

    has_duplicates = len(unique_coords) < len(coords)
    is_closed_ring = coords[0] == coords[-1]
    only_closed_ring_duplicate = (
        is_closed_ring and len(unique_coords) == len(coords) - 1
    )

    return has_duplicates and not only_closed_ring_duplicate


def check_less_three_unique_nodes(geometry: dict) -> bool:
    """Return True if there are fewer than three unique nodes in the geometry."""
    coords = geometry["coordinates"][0]
    return len(set(map(tuple, coords))) < 3


def check_exterior_not_ccw(geom: Polygon) -> bool:
    """Return True if the exterior ring is not counter-clockwise."""
    return not geom.exterior.is_ccw


def check_interior_not_cw(geom: Polygon) -> bool:
    """Return True if any interior ring is counter-clockwise."""
    return any(interior.is_ccw for interior in geom.interiors)


def check_inner_and_exterior_ring_intersect(geom: Polygon) -> bool:
    """Return True if any interior ring intersects with the exterior ring."""
    return any(geom.exterior.intersects(interior) for interior in geom.interiors)


def check_crs_defined(feature_collection: dict) -> bool:
    """Return True if a CRS (Coordinate Reference System) other than 4326 is defined in the feature collection."""
    if "crs" in feature_collection:
        return (
            feature_collection["crs"] != "EPSG:4326"
        )  # TODO: should 4326 be okay? could be written differently


def check_outside_lat_lon_boundaries(geometry: dict) -> bool:
    """Return True if not all coordinates are within the standard lat/lon boundaries."""
    coords = geometry["coordinates"][0]
    return not all(-180 <= lon <= 180 and -90 <= lat <= 90 for lon, lat in coords)
