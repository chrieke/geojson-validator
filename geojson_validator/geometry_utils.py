from typing import List, Union, Tuple
import json
from urllib.parse import urlparse
from pathlib import Path

import requests


def read_geojson_file_or_url(fp_or_url: Union[str, Path]):
    """Reads a geojson source from a filepath or url"""
    if Path(fp_or_url).suffix not in [
        ".json",
        ".JSON",
        ".geojson",
        ".GEOJSON",
    ]:
        raise ValueError("Filepath or URL must be a geojson or json file")
    if isinstance(fp_or_url, Path) or Path(fp_or_url).is_file():
        fp = Path(fp_or_url)
        if fp.exists():
            with fp.open(encoding="UTF-8") as f:
                return json.load(f)
    elif urlparse(fp_or_url).scheme in ("http", "https", "ftp", "ftps"):
        response = requests.get(str(fp_or_url), timeout=5)
        if response.status_code == 200:  # Check if the request was successful
            return response.json()


def get_geometries(geojson_input: dict) -> Tuple[str, List[dict]]:
    """
    Extracts the geometries from the GeoJSON.

    Args:
        geojson_input: Input GeoJSON FeatureCollection, Feature or Geometry.

    Returns:
        Tuple: The geometry type of the initial input, list of GeoJSON geometries from the input
    """
    if isinstance(geojson_input, (str, Path)):
        geojson_input = read_geojson_file_or_url(geojson_input)
    elif hasattr(geojson_input, "__geo_interface__"):
        geojson_input = geojson_input.__geo_interface__
    elif not isinstance(geojson_input, dict) or "type" not in geojson_input:
        raise ValueError(
            f"Unsupported input {type(geojson_input)}. Input must be a GeoJSON, filepath/url to GeoJSON, "
            f"shapely geometry or any object with a __geo_interface__"
        )

    supported_geojson_types = [
        "Point",
        "MultiPoint",
        "Linestring",
        "MulltiLineString",
        "Polygon",
        "MultiPolygon",
    ]
    # TODO: Validate all required geojson fields
    type_ = geojson_input.get("type", None)  # FeatureCollection, Feature, Geometry
    if type_ is None:
        raise ValueError("No 'type' field found in GeoJSON")
    if type_ == "FeatureCollection":
        geometries = [feature["geometry"] for feature in geojson_input["features"]]
    elif type_ == "Feature":
        geometries = [geojson_input["geometry"]]
    elif type_ in supported_geojson_types:
        geometries = [geojson_input]
    else:
        raise ValueError(
            f"Unsupported GeoJSON type {type_}. Supported are {supported_geojson_types}"
        )

    return type_, geometries
