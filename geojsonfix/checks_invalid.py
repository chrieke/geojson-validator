# TODO: ?immer selbe response, dict mit 0/1


def check_all_invalid(df, criteria):
    functions = {
        "unclosed": check_unclosed,
        "duplicate_nodes": check_duplicate_nodes,
        "less_three_unique_nodes": check_less_three_unique_nodes,
        "exterior_not_ccw": check_exterior_not_ccw,
        "interior_not_cw": check_interior_not_cw,
        "inner_and_exterior_ring_intersect": check_inner_and_exterior_ring_intersect,
        "defined_crs": check_defined_crs
    }
    results = {}
    for criterium in criteria:
        validator = functions[criterium]
        for i, row in df.iterrows():
            if validator(row.geometry):
                results.setdefault(criterium, []).append(i)
    return results


def check_unclosed(geometry):
    # TODO: geopandas or shapely autocloses!
    coords = list(geometry.exterior.coords)
    is_closed = coords[0] == coords[-1]
    return not is_closed


def check_duplicate_nodes(geometry) -> bool:
    coords = list(geometry.exterior.coords)[
        1:-1
    ]  # TODO: could be that unclosed but still a duplicate
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
