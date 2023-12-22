from typing import Dict, Union, List
import sys

import geojson
from loguru import logger
from shapely.geometry import shape

from .checks_invalid import check_all_invalid
from .checks_problematic import check_all_problematic

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
    check_criteria(criteria_invalid, invalid=True)
    logger.info(f"Validation for criteria_invalid: {criteria_invalid}")
    check_criteria(criteria_problematic, problematic=True)
    logger.info(f"Validation for criteria_problematic: {criteria_problematic}")

    type_ = geojson.get("type", None)
    if type_ is None:
        raise ValueError("no 'type' field found in GeoJSON")
    elif type_ == "FeatureCollection":
        features = geojson.get("features", None)
        if features is None:
            raise ValueError("no 'features' field found in GeoJSON FeatureCollection")
    elif type_ == "Feature":
        geometry = geojson.get("geometry", None)
        if geometry is None:
            raise ValueError("no 'geometry' field found in GeoJSON Feature")
    elif type_ == "Polygon":
        features = [{"type": "Feature", "properties": {}, "geometry": geojson}]
    else:
        raise ValueError(
            "The GeoJSON must consist of a FeatureCollection, Features, or Geometries of type Polygon"
        )

    results = {}
    # "invalid": dict.fromkeys(criteria_invalid, []),
    #          "problematic": dict.fromkeys(criteria_problematic, [])
    # "data_original": original_json,
    # "data_fixed": fixed_json,
    #        }

    for i, feature in enumerate(features):
        geometry_type = feature.get("geometry", None).get("type", None)
        if geometry_type is None:
            raise ValueError("The feature must contain a geometry of type Polygon")

        geom = shape(feature["geometry"])
        results_invalid = check_all_invalid(geom, criteria_invalid)
        results_problematic = check_all_problematic(geom, criteria_problematic)

        all_results_invalid = {}
        for k in results_invalid:
            all_results_invalid.setdefault(k, []).append(i)
        all_results_problematic = {}
        for k in results_problematic:
            all_results_problematic.setdefault(k, []).append(i)

    results = {"invalid": all_results_invalid, "problematic": all_results_problematic}
    return results


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
