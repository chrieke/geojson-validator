# def fix_duplicate_nodes(geometry):
#     df.geometry = df.geometry.simplify(0)


# def fix_exterior_not_ccw(df):
#     df.geometry = df.geometry.apply(
#         lambda x: orient(x) if x.geom_type == "Polygon" else x
#     )
