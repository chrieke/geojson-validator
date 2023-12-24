from shapely.geometry import shape

# Some criteria require the original json geometry dict as shapely etc. autofixes (e.g. closes) geometries.


def check_holes(geometry: dict) -> bool:
    """Return True if the geometry has holes (interior rings)."""
    geom = shape(geometry)
    return len(geom.interiors) > 0


def check_self_intersection(geometry: dict) -> bool:
    """Return True if the geometry is self-intersecting."""
    # TODO how to check selfintersection in shapely
    geom = shape(geometry)
    return not geom.is_valid


def check_excessive_coordinate_precision(geometry: dict) -> bool:
    """Return True if any coordinate has more than 6 decimal places in the longitude."""
    # For speedup, only checks the x coordinate of first 2 coordinate pairs in the geometry
    # TODO: Correct, do more?
    coords = geometry["coordinates"][0]
    return any([len(str(coord[0]).split(".")[1]) > 6 for coord in coords[:2]])


def check_more_than_2d_coordinates(geometry: dict, check_all_coordinates=False) -> bool:
    """Return True if any coordinates are more than 2D."""
    # TODO: should check_all_coordinates be activated?
    coords = geometry["coordinates"][0]
    if check_all_coordinates:
        for ring in coords:
            for coord in ring:
                if len(coord) > 2:
                    return True
    first_coordinate = coords[0]
    return len(first_coordinate) > 2


def check_crosses_antimeridian(geometry: dict) -> bool:
    """Return True if the geometry crosses the antimeridian."""
    coords = geometry["coordinates"][0]
    for start, end in zip(coords, coords[1:]):
        # Normalize longitudes to -180 to 180 range
        norm_start_lon = (start[0] + 180) % 360 - 180
        norm_end_lon = (end[0] + 180) % 360 - 180

        # Check for longitude switch indicating crossing
        if abs(norm_end_lon - norm_start_lon) > 180:
            return True
    return False
