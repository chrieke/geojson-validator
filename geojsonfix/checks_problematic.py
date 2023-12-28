from shapely.geometry import Polygon
from shapely.validation import explain_validity


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


def check_excessive_coordinate_precision(
    geometry: dict, precision=6, n_first_coords=2
) -> bool:
    """Return True if coordinates have more than 6 decimal places in the longitude."""
    # For speedup, by default only checks the x&y coordinates of the n_first_coords=2 coordinate pairs.
    coords = geometry["coordinates"][0][:n_first_coords]
    for coord_xy in coords:
        for coord in coord_xy:
            splits = str(coord).split(".")
            if (
                len(splits) == 2 and len(splits[1]) > precision
            ):  # catch coord without after comma
                return True
    return False


def check_more_than_2d_coordinates(geometry: dict, n_first_coords=2) -> bool:
    """Return True if any coordinates are more than 2D."""
    # TODO: should all coordinates be checked?
    for coords in geometry["coordinates"][0][:n_first_coords]:
        if len(coords) > 2:
            return True
    return False


def check_crosses_antimeridian(geometry: dict) -> bool:
    """Return True if the geometry crosses the antimeridian (meridian at 180 longitude)."""
    coords = geometry["coordinates"][0]
    for start, end in zip(coords, coords[1:]):
        # Normalize longitudes to -180 to 180 range
        norm_start_lon = (start[0] + 180) % 360 - 180
        norm_end_lon = (end[0] + 180) % 360 - 180

        # Check for longitude switch indicating crossing
        if abs(norm_end_lon - norm_start_lon) > 180:
            return True
    return False
