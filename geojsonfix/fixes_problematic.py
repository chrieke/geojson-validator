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

# if (
#         "No Self-Intersection" in validation_criteria
#         and not vector.is_no_selfintersection
# ):
#     vector.df.geometry = vector.df.geometry.apply(lambda x: x.buffer(0))
#     st.info("Removing Self-Intersections by applying buffer(0)...")
# if "No Holes" in validation_criteria and not vector.is_no_holes:
#     vector.df.geometry = vector.df.geometry.apply(lambda x: utils.close_holes(x))
#     st.info("Closing holes in geometry...")
# if "Counterclockwise" in validation_criteria and not vector.is_ccw:
#     vector.df.geometry = vector.df.geometry.apply(
#         lambda x: orient(x) if x.geom_type == "Polygon" else x
#     )
#     st.info("Applying right-hand/ccw winding ...")
# if (
#         "No Duplicated Vertices" in validation_criteria
#         and not vector.is_no_duplicated_vertices
# ):
#     vector.df.geometry = vector.df.geometry.simplify(0)
#     st.info("Removing duplicated vertices ...")
