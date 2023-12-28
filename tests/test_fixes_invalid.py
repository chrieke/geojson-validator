# import json
#
# from shapely.geometry import shape
# import pytest
#
# from .context import fixes_invalid
#
#
# def read_geojson_geometry(file_name: str):
#     geojson_fp = f"./tests/examples_geojson/invalid/{file_name}"
#     with open(geojson_fp) as f:
#         gj = json.load(f)
#     return gj["features"][0]["geometry"]
#
#
# def test_check_unclosed():
#     geometry = read_geojson_geometry("polygon_unclosed_polygon.geojson")
#     fixed_geometry = fixes_invalid.fix_unclosed(geometry)
