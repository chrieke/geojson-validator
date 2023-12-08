from geopandas import GeoDataFrame

from shapely.geometry import mapping


def check_all_problematic(df, criteria):
    problematic_results = {}

    for i, row in df.iterrows():
        if "holes" in criteria:
            if check_holes(row.geometry):
                problematic_results.setdefault("holes", []).append(i)

        if "self_intersection" in criteria:
            if check_self_intersection(row.geometry):
                problematic_results.setdefault("self_intersection", []).append(i)

        if "excessive_coordinate_precision" in criteria:
            if check_excessive_coordinate_precision(row.geometry):
                problematic_results.setdefault(
                    "excessive_coordinate_precision", []
                ).append(i)

        if "more_than_2d_coordinates" in criteria:
            if check_more_than_2d_coordinates(row.geometry):
                problematic_results.setdefault("more_than_2d_coordinates", []).append(i)

        if "crosses_antimeridian" in criteria:
            if check_crosses_antimeridian(row.geometry):
                problematic_results.setdefault("crosses_antimeridian", []).append(i)

    return problematic_results


def check_holes(geometry) -> bool:
    has_holes = False
    if geometry.geom_type == "Polygon":
        try:
            geometry.interiors[0]
            has_holes = True
        except IndexError:
            pass
        return has_holes
    else:
        raise TypeError("geometry is not a Polygon")


# def fix_holes(df):
#     def close_holes(poly: Polygon) -> Polygon:
#         """
#         Close polygon holes by limitation to the exterior ring.
#         Args:
#             poly: Input shapely Polygon
#         Example:
#             df.geometry.apply(lambda p: close_holes(p))
#         """
#         if poly.interiors:
#             return Polygon(list(poly.exterior.coords))
#         else:
#             return poly
#
#     df.geometry = df.geometry.apply(close_holes)


def check_self_intersection(geometry) -> bool:
    # TODO how to check selfintersection
    return not geometry.is_valid


# def fix_self_intersection(df):
#     df.geometry = df.geometry.buffer(0)


def check_excessive_coordinate_precision(geometry):
    # Check x coordinate of first 2 coordinate pairs in geometry
    return any(
        [
            len(str(coord[0]).split(".")[1]) > 6
            for coord in mapping(geometry)["coordinates"][:2]
        ]
    )


def check_more_than_2d_coordinates(geometry):
    # Check length of first two coordinate pairs
    return any([len(coord) > 2 for coord in mapping(geometry)["coordinates"][:2]])


def check_crosses_antimeridian(geometry):
    pass
