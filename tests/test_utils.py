import json


def read_geojson_geometry(geojson_fp: str):
    with open(geojson_fp) as f:
        gj = json.load(f)
    return gj["features"][0]["geometry"]
