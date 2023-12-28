# # from shapely.ops import orient
# # def fix_duplicate_nodes(geometry):
# #     df.geometry = df.geometry.simplify(0)
#
#
# # def fix_exterior_not_ccw(df):
# #     df.geometry = df.geometry.apply(
# #         lambda x: orient(x) if x.geom_type == "Polygon" else x
# #     )
#
#
# from shapely.geometry import Polygon, LinearRing
# from shapely.ops import unary_union
#
#
# # def fix_unclosed(geometry: dict):
# #     """Close the geometry by adding the first coordinate at the end if not closed."""
# #     coords = geometry["coordinates"][0]
# #     if coords[0] != coords[-1]:
# #         coords.append(coords[0])
# #     geometry["coordinates"] = [coords]
#
#
# def fix_duplicate_nodes(geometry: dict):
#     """Remove duplicate nodes from the geometry, excluding the closure node."""
#     coords = geometry["coordinates"][0]
#     seen = set()
#     new_coords = []
#     for coord in coords[:-1]:  # Exclude the last point for now
#         if tuple(coord) not in seen:
#             seen.add(tuple(coord))
#             new_coords.append(coord)
#     new_coords.append(new_coords[0])  # Ensure closure
#     geometry["coordinates"] = [new_coords]
#
#
# def fix_exterior_not_ccw(geom: Polygon):
#     """Reorder exterior ring to be counter-clockwise."""
#     if not geom.exterior.is_ccw:
#         geom = Polygon(list(geom.exterior.coords)[::-1])
#     return geom
#
#
# def fix_interior_not_cw(geom: Polygon):
#     """Reorder any interior rings to be clockwise."""
#     exterior = LinearRing(geom.exterior)
#     interiors = [
#         LinearRing(interior) if interior.is_ccw else LinearRing(interior.coords[::-1])
#         for interior in geom.interiors
#     ]
#     return Polygon(exterior, interiors)
#
#
# # The rest of the functions like fixing fewer than three unique nodes, fixing intersecting inner and outer rings, defining CRS, and fixing outside boundaries typically involve more complex logic, potential user input, or case-by-case handling. They are generally not as straightforward to "fix" programmatically without additional context or constraints.
