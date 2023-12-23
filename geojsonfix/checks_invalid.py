# TODO: ?immer selbe response, dict mit 0/1


def check_unclosed(geometry: dict):
    # shapely or Geopandas, this needs to check the original json string!
    coords = geometry["coordinates"][0][0]
    is_closed = coords[0] == coords[-1]
    return not is_closed


def check_duplicate_nodes(geometry: dict) -> bool:
    # TODO: could be that unclosed but still a duplicate
    coords = geometry["coordinates"][0][0][
        1:-1
    ]
    has_duplicate_node = len(coords) != len(set(coords))
    return has_duplicate_node


def check_less_three_unique_nodes(geometry):
    # TODO: geopandas or shapely autocloses, makes 4 nodes.
    pass


def check_exterior_not_ccw(geometry) -> bool:
    return not geometry.exterior.is_ccw


def check_interior_not_cw(geometry) -> bool:
    return any([interior.is_ccw for interior in geometry.interiors])


def check_inner_and_exterior_ring_intersect(geometry) -> bool:
    return any(
        [geometry.exterior.intersects(interior) for interior in geometry.interiors]
    )


def check_defined_crs(geometry) -> bool:
    # geopandas should ignore crs from geojson? shapely doesnt have crs
    pass
