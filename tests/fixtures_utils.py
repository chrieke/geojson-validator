import json


def read_geojson(file_path: str, geometries=False):
    with open(file_path) as f:
        gj = json.load(f)
    if geometries:
        return gj["features"][0]["geometry"]
    return gj
