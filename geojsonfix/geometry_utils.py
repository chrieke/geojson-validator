from typing import List, Union, Tuple
import json

from pathlib import Path


def read_file(filepath: Union[str, Path]):
    filepath = Path(filepath)
    if filepath.exists() and filepath.suffix in [
        ".json",
        ".JSON",
        ".geojson",
        ".GEOJSON",
    ]:
        with filepath.open(encoding="UTF-8") as f:
            return json.load(f)


def get_geometries(geojson_input: dict) -> Tuple[str, List[dict]]:
    """
    Extracts the geometries from the GeoJSON.

    Args:
        geojson_input: Input GeoJSON FeatureCollection, Feature or Geometry.

    Returns:
        Tuple: The geometry type of the initial input, list of GeoJSON geometries from the input
    """
    if isinstance(geojson_input, (str, Path)):
        geojson_input = read_file(filepath=geojson_input)
    elif hasattr(geojson_input, "__geo_interface__"):
        geojson_input = geojson_input.__geo_interface__
    elif not isinstance(geojson_input, dict) or "type" not in geojson_input:
        raise ValueError(
            f"Unsupported input {type(geojson_input)}. Input must be a GeoJSON, filepath to GeoJSON, "
            f"shapely geometry or any object with a __geo_interface__"
        )

    type_ = geojson_input.get("type", None)
    # TODO: Validate all required geojson fields
    if type_ is None:
        raise ValueError("No 'type' field found in GeoJSON")
    if type_ == "FeatureCollection":
        geometries = [feature["geometry"] for feature in geojson_input["features"]]
    elif type_ == "Feature":
        geometries = [geojson_input["geometry"]]
    elif type_ in ["Polygon", "MultiPolygon"]:
        geometries = [geojson_input]
    else:
        # TODO: Support all types
        raise ValueError(
            f"Unsupported GeoJSON type {type_}. Only FeatureCollection, Feature or Polygon/MultiPolygon "
            f"Geometry are supported."
        )

    return type_, geometries
