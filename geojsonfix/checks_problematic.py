from shapely.geometry import mapping
from shapely.geometry import shape


def check_all_problematic(geom, criteria):
    functions = {
        "holes": check_holes,
        "self_intersection": check_self_intersection,
        "excessive_coordinate_precision": check_excessive_coordinate_precision,
        "more_than_2d_coordinates": check_more_than_2d_coordinates,
        "crosses_antimeridian": check_crosses_antimeridian,
    }
    results = []
    for criterium in criteria:
        validator = functions[criterium]
        if validator(geom):
            results.append(criterium)
    return results


def check_holes(geometry) -> bool:
    has_holes = False
    try:
        geometry.interiors[0]
        has_holes = True
    except IndexError:
        pass
    return has_holes


def check_self_intersection(geometry) -> bool:
    # TODO how to check selfintersection
    return not geometry.is_valid


def check_excessive_coordinate_precision(geometry):
    # Check x coordinate of first 2 coordinate pairs in geometry
    return any(
        [
            len(str(coord[0]).split(".")[1]) > 6
            for coord in mapping(geometry)["coordinates"][:2]
        ]
    )


def check_more_than_2d_coordinates(geometry, check_all_coordinates=False):
    """
    By default checks only the first coordinate pair to speed things up.

    Args:
        geometry:
        check_all_coordinates:

    Returns:

    """
    # TODO: should check_all_coordinates be activated?
    coords = mapping(geometry)["coordinates"]
    print(coords)
    first_coord = coords[0][0]
    if len(first_coord) > 2:
        return True
    elif check_all_coordinates:
        for ring in coords:
            for coord in ring:
                if len(coord) > 2:
                    return True
    else:
        return False


def check_crosses_antimeridian(geometry):
    pass
