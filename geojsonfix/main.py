from typing import Dict, Union, List
import sys

import geojson
from loguru import logger

from .checks_invalid import *
from .checks_problematic import *
from .geom import read_geometry_input

logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")

VALIDATION_CRITERIA = {
    "invalid": [
        "unclosed",
        "duplicate_nodes",
        "less_three_unique_nodes",
        "exterior_cw",
        "interior_ccw",
        "inner_and_exterior_ring_intersect",
        "defined_crs",
    ],
    "problematic": [
        "holes",
        "selfintersection",
        "excessive_coordinate_precision",
        "more_than_2d_coordinates",
        "crosses_antimeridian",
    ],
}


def validate(
    geojson: Union[geojson.FeatureCollection, str],
    validation_criteria: List[str] = ["invalid", "problematic"],
) -> Dict:
    """
    Validate that a GeoJSON conforms to the geojson specs.

    Args:
        geojson: Input GeoJSON feature collection.
        validation_criteria: A list of validation criteria. Can be of the categories ["invalid", "problematic"], specific validation criteria, or a combination.

    Returns:
        The validated & fixed GeoJSON feature collection.
    """
    df = read_geometry_input(geojson)
    original_json = df.__geo_interface__.copy()
    # fixed_json = original_json.copy()

    criteria = [
        elem for elem in validation_criteria if not "invalid" or not "problematic"
    ]
    if "invalid" in validation_criteria:
        criteria.extend(VALIDATION_CRITERIA["invalid"])
    if "problematic" in validation_criteria:
        criteria.extend(VALIDATION_CRITERIA["problematic"])
    criteria = list(set(criteria))

    ### Invalid ###
    invalid_results = {}
    if "duplicate_nodes" in criteria:
        if check_duplicate_nodes(df):
            invalid_results["duplicate_nodes"] = True

    if "exterior_ccw" in criteria:
        if check_exterior_ccw(df):
            invalid_results["exterior_ccw"] = True

    ### Problematic ###
    problematic_results = {}
    if "no_holes" in criteria:
        if check_holes(df):
            problematic_results["no_holes"] = True

    if "no_selfintersection" in criteria:
        if check_selfintersection(df):
            problematic_results["no_selfintersection"] = True

    return {
        "invalid": list(invalid_results.keys()),
        "problematic": list(problematic_results.keys()),
        # "data_original": original_json,
        # "data_fixed": fixed_json,
    }
