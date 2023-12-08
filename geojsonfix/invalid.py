from shapely.ops import orient


def check_all_invalid(df, criteria):
    invalid_results = {}

    for i, row in df.iterrows():
        if "unclosed" in criteria:
            if check_unclosed(row.geometry):
                invalid_results.setdefault("unclosed", []).append(i)

        if "less_three_unique_nodes" in criteria:
            if check_less_three_unique_nodes(row.geometry):
                invalid_results.setdefault("less_three_unique_nodes", []).append(i)

        if "duplicate_nodes" in criteria:
            if check_duplicate_nodes(row.geometry):
                invalid_results.setdefault("duplicate_nodes", []).append(i)

        if "exterior_not_ccw" in criteria:
            if check_exterior_not_ccw(row.geometry):
                invalid_results.setdefault("exterior_not_ccw", []).append(i)

        if "interior_not_cw" in criteria:
            if check_interior_not_cw(row.geometry):
                invalid_results.setdefault("interior_not_cw", []).append(i)

        if "inner_and_exterior_ring_intersect" in criteria:
            if check_inner_and_exterior_ring_intersect(row.geometry):
                invalid_results.setdefault(
                    "inner_and_exterior_ring_intersect", []
                ).append(i)

    return invalid_results


def check_unclosed(geometry):
    # TODO: geopandas or shapely autocloses!
    if geometry.geom_type == "Polygon":
        coords = list(geometry.exterior.coords)
        is_closed = coords[0] == coords[-1]
        return not is_closed
    else:
        raise TypeError("geometry is not a Polygon")


def check_duplicate_nodes(geometry) -> bool:
    if geometry.geom_type == "Polygon":
        coords = list(geometry.exterior.coords)[
            1:-1
        ]  # TODO: could be that unclosed but still a duplicate
        has_duplicate_node = len(coords) != len(set(coords))
        return has_duplicate_node
    else:
        raise TypeError("geometry is not a Polygon")


# def fix_duplicate_nodes(geometry):
#     df.geometry = df.geometry.simplify(0)


def check_less_three_unique_nodes(geometry):
    # TODO: geopandas or shapely autocloses, makes 4 nodes.
    pass


def check_exterior_not_ccw(geometry) -> bool:
    if geometry.geom_type == "Polygon":  # move maybe from every function in topfunc?
        return not geometry.exterior.is_ccw
    else:
        raise TypeError("geometry is not a Polygon")


# def fix_exterior_not_ccw(df):
#     df.geometry = df.geometry.apply(
#         lambda x: orient(x) if x.geom_type == "Polygon" else x
#     )


def check_interior_not_cw(geometry) -> bool:
    if geometry.geom_type == "Polygon":
        return any([interior.is_ccw for interior in geometry.interiors])
    else:
        raise TypeError("geometry is not a Polygon")


def check_inner_and_exterior_ring_intersect(geometry) -> bool:
    pass
    if geometry.geom_type == "Polygon":
        return any(
            [geometry.exterior.intersects(interior) for interior in geometry.interiors]
        )
    else:
        raise TypeError("geometry is not a Polygon")


def check_defined_crs(geometry) -> bool:
    # geopandas should ignore crs from geojson? shapely doesnt have crs
    pass
