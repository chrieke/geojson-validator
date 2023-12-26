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


# def fix_self_intersection(df):
#     df.geometry = df.geometry.buffer(0)
