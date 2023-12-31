from typing import Union, Any
from urllib.parse import urlparse
from pathlib import Path
import json

from shapely.geometry import shape
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


def input_to_geojson(geojson_input: Union[str, Path, dict, Any]) -> dict:
    """Take the input which can be various types and reads/transforms it to Geojson"""
    if isinstance(geojson_input, (str, Path)):
        geojson_input = read_geojson_file_or_url(geojson_input)
    elif hasattr(
        geojson_input, "__geo_interface__"
    ):  # e.g. shapely geometry object, geojson library objects
        geojson_input = geojson_input.__geo_interface__
    elif not isinstance(geojson_input, (dict)) or "type" not in geojson_input:
        raise ValueError(
            f"Unsupported input {type(geojson_input)}. Input must be a GeoJSON, filepath/url to GeoJSON, "
            f"shapely geometry or any object with a __geo_interface__"
        )
    return geojson_input


def any_geojson_to_featurecollection(
    geojson_input: Union[str, Path, dict, Any]
) -> dict:
    """Take a geojson of various types (Feature, Geometry, Fc) and transform it to a featurecollection"""
    supported_geojson_types = [
        "Point",
        "MultiPoint",
        "Linestring",
        "MulltiLineString",
        "Polygon",
        "MultiPolygon",
    ]
    type_ = geojson_input.get("type", None)  # FeatureCollection, Feature, Geometry
    if type_ is None:
        raise ValueError("No 'type' field found in GeoJSON")
    if type_ == "FeatureCollection":
        fc = geojson_input
    elif type_ == "Feature":
        fc = {"type": "FeatureCollection", "features": [geojson_input]}
    elif type_ in supported_geojson_types:
        fc = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": geojson_input}],
        }
    else:
        raise ValueError(
            f"Unsupported GeoJSON type {type_}. Supported are {supported_geojson_types}"
        )

    return fc


def prepare_geometries_for_checks(geometry):
    """Prepares the Geometries for the validation checks"""
    # Some criteria require the original json geometry dict as shapely etc. autofixes (e.g. closes) geometries.
    # Initiating the shapely type in each check function specifically is time intensive.
    shapely_geom = shape(geometry)

    # To avoid adjusting the checks code for each geometry type, they are brought to the same
    # list depth (not ideal but okay).
    geometry_type = geometry.get("type", None)
    if geometry_type == "Point":
        geometry["coordinates"] = [[geometry["coordinates"]]]
    if geometry_type == "LineString":
        geometry["coordinates"] = [geometry["coordinates"]]
    return geometry, shapely_geom
