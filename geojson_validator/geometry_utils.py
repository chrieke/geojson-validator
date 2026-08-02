from typing import Any, List, Optional, Union
from urllib.parse import urlparse
from pathlib import Path
import json

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry
from shapely.errors import ShapelyError
import requests


def read_geojson_file_or_url(fp_or_url: Union[str, Path]) -> dict:
    """Reads a geojson source from a filepath or url"""
    parsed_url = urlparse(str(fp_or_url))
    is_url = parsed_url.scheme in ("http", "https", "ftp", "ftps")
    # For urls the suffix must come from the path only, a query string would be part of it.
    suffix = Path(parsed_url.path if is_url else fp_or_url).suffix
    if suffix.lower() not in (".json", ".geojson"):
        raise ValueError("Filepath or URL must be a geojson or json file")
    if is_url:
        response = requests.get(str(fp_or_url), timeout=5)
        response.raise_for_status()  # raise a clear HTTP error instead of falling through to a file open
        return response.json()

    with Path(fp_or_url).open(encoding="UTF-8") as f:
        return json.load(f)


def input_to_geojson(geojson_input: Any) -> dict:
    """Take the input which can be various types and reads/transforms it to Geojson"""
    if isinstance(geojson_input, (str, Path)):
        return read_geojson_file_or_url(geojson_input)
    if hasattr(
        geojson_input, "__geo_interface__"
    ):  # e.g. shapely geometry object, geojson library objects
        return geojson_input.__geo_interface__
    if not isinstance(geojson_input, dict) or "type" not in geojson_input:
        raise ValueError(
            f"Unsupported input '{type(geojson_input)}'. Input must be a GeoJSON, filepath/url to GeoJSON, "
            f"shapely geometry or any object with a __geo_interface__"
        )
    return geojson_input


def any_geojson_to_featurecollection(geojson_input: dict) -> dict:
    """Take a geojson of various types (Feature, Geometry, Fc) and transform it to a featurecollection"""
    supported_geojson_types = [
        "Point",
        "MultiPoint",
        "LineString",
        "MultiLineString",
        "Polygon",
        "MultiPolygon",
        "GeometryCollection",
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


def extract_single_geometries(geometry: dict, geometry_type: str) -> List[dict]:
    if "Multi" in geometry_type:
        single_type = geometry_type.split("Multi")[1]
        return [
            {"type": single_type, "coordinates": g} for g in geometry["coordinates"]
        ]
    if geometry_type == "GeometryCollection":
        return geometry["geometries"]
    return []


def coordinate_arrays(geometry: dict) -> list:
    """
    The position arrays of a single geometry, without modifying it:
    all rings for a Polygon, one array for a LineString or Point.
    """
    geometry_type = geometry.get("type", None)
    if geometry_type == "Point":
        return [[geometry["coordinates"]]]
    if geometry_type == "LineString":
        return [geometry["coordinates"]]
    return geometry["coordinates"]


def to_shapely_or_none(geometry: dict) -> Optional[BaseGeometry]:
    """Parses the geometry dict to shapely for the validation checks that require it."""
    # Some criteria require the original json geometry dict as shapely etc. autofixes (e.g. closes) geometries.
    # Initiating the shapely type in each check function specifically is time intensive.
    try:
        return shape(geometry)
    except (TypeError, ValueError, ShapelyError):
        # e.g. mixed 2D/3D coordinates make shapely raise. Return None so the raw-JSON
        # based checks (3d_coordinates, precision, etc.) can still run; shapely-based
        # checks are skipped for this geometry.
        return None
