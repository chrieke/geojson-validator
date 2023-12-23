# TODO: ?immer selbe response, dict mit 0/1


def check_unclosed(geometry: dict):
    # This needs to check the original json string, as shapely or geopandas automatically close.
    coords = geometry["coordinates"][0]
    is_closed = coords[0] == coords[-1]
    return not is_closed


def check_duplicate_nodes(geometry: dict) -> bool:
    coords = geometry["coordinates"][0]
    unique_coords = set(map(tuple, coords))
    first_last_same = coords[0] == coords[-1]

    duplications = False
    if len(unique_coords) < len(coords):
        duplications = True
        # But acceptable if only the first and last coordinates are the same (closed ring)
        # and no other duplicates are present
        if (first_last_same and len(unique_coords) == len(coords) - 1):
            duplications = False
    return duplications


def check_less_three_unique_nodes(geometry):
    coords = geometry["coordinates"][0]
    return len(set(map(tuple, coords))) < 3


def check_exterior_not_ccw(geometry) -> bool:
    return not geometry.exterior.is_ccw


def check_interior_not_cw(geometry) -> bool:
    return any([interior.is_ccw for interior in geometry.interiors])


def check_inner_and_exterior_ring_intersect(geometry) -> bool:
    return any(
        [geometry.exterior.intersects(interior) for interior in geometry.interiors]
    )


def check_crs_defined(feature_collection) -> bool:
    return feature_collection.get("crs", None)
