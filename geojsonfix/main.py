from typing import Dict, Union, List
import sys

import geojson
from loguru import logger

from .checks_invalid import check_all_invalid
from .checks_problematic import check_all_problematic
from .geom import read_geometry_input

logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")

VALIDATION_CRITERIA = {
    "invalid": [
        "unclosed",
        "duplicate_nodes",
        "less_three_unique_nodes",
        "exterior_not_ccw",
        "interior_not_cw",
        "inner_and_exterior_ring_intersect",
        "defined_crs",
    ],
    "problematic": [
        "holes",
        "self_intersection",
        "excessive_coordinate_precision",
        "more_than_2d_coordinates",
        "crosses_antimeridian",
    ],
}


def validate(
    geojson: Union[geojson.FeatureCollection, str],
    criteria_invalid: Union[List[str], None] = VALIDATION_CRITERIA["invalid"],
    criteria_problematic: Union[List[str], None] = VALIDATION_CRITERIA["problematic"],
) -> Dict:
    """
    Validate that a GeoJSON conforms to the geojson specs.

    Args:
        geojson: Input GeoJSON feature collection.
        criteria_invalid: A list of validation criteria that are invalid according the GeoJSON specification.
        criteria_problematic: A list of validation criteria that are valid, but problematic with some tools.

    Returns:
        The validated & fixed GeoJSON feature collection.
    """
    df = read_geometry_input(geojson)
    original_json = df.__geo_interface__.copy()
    # fixed_json = original_json.copy()

    check_criteria(criteria_invalid, invalid=True)
    logger.info(f"Validation for criteria_invalid: {criteria_invalid}")
    check_criteria(criteria_problematic, problematic=True)
    logger.info(f"Validation for criteria_problematic: {criteria_problematic}")

    # TODO: Check geometry type? here or in func

    results_invalid = check_all_invalid(df, criteria_invalid)
    results_problematic = check_all_problematic(df, criteria_problematic)

    return {
        "invalid": results_invalid,
        "problematic": results_problematic,
        # "data_original": original_json,
        # "data_fixed": fixed_json,
    }


def check_criteria(selected_criteria, invalid=False, problematic=False):
    for criterium in selected_criteria:
        if invalid:
            if criterium not in VALIDATION_CRITERIA["invalid"]:
                raise ValueError(
                    f"The selected criterium {criterium} is not a valid argument for `criteria_invalid`"
                )
        if problematic:
            if criterium not in VALIDATION_CRITERIA["problematic"]:
                raise ValueError(
                    f"The selected criterium {criterium} is not a valid argument for `criteria_invalid`"
                )


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
