from typing import Dict, Union, List
import sys

import geojson
from loguru import logger

from .invalid import check_all_invalid
from .problematic import check_all_problematic
from .geom import read_geometry_input
from .utils import consolidate_criteria

logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")


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

    criteria = consolidate_criteria(validation_criteria)
    logger.info(f"Validation criteria: {criteria}")

    results_invalid = check_all_invalid(df, criteria)
    results_problematic = check_all_problematic(df, criteria)

    return {
        "invalid": results_invalid,
        "problematic": results_problematic,
        # "data_original": original_json,
        # "data_fixed": fixed_json,
    }


# def fix(geojson, fix_criteria=["invalid", "problematic"]):
#
#     df = read_geometry_input(geojson)
#     original_json = df.__geo_interface__.copy()
#
#     criteria = consolidate_criteria(fix_criteria)
#     logger.info(f"Fix criteria: {criteria}")
#
#     results_invalid = fix_all_invalid(df, criteria)
#     results_problematic = fix_all_problematic(df, criteria)
