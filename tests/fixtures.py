import json


def read_geojson(file_path: str, geometries=False):
    with open(file_path) as f:
        fc = json.load(f)
    if geometries:
        return fc["features"][0]["geometry"]
    return fc
