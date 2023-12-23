from typing import Dict, Union, List
import sys

import geojson
from loguru import logger
from shapely.geometry import shape

from . import checks_invalid
from . import checks_problematic

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

    # "data_original": original_json,
    # "data_fixed": fixed_json,
    #        }
    results_invalid, results_problematic = {}, {}

    for criterium in criteria_invalid:
        for i, feature in enumerate(features):
            invalid = False
            geometry_type = feature.get("geometry", None).get("type", None)
            if geometry_type is None:
                raise ValueError("The feature must contain a geometry of type Polygon")
            geom = shape(feature["geometry"])
            # Some checks require original GeoJSON, some shapely, structure can not be simplified.
            if criterium == "unclosed":
                invalid = checks_invalid.check_unclosed(feature["geometry"])
            if criterium == "duplicate_nodes":
                invalid = checks_invalid.check_duplicate_nodes(feature["geometry"])
            if criterium == "less_three_unique_nodes":
                invalid = checks_invalid.check_less_three_unique_nodes(feature["geometry"])
            if criterium == "exterior_not_ccw":
                invalid = checks_invalid.check_exterior_not_ccw(geom)
            if criterium == "interior_not_cw":
                invalid = checks_invalid.check_interior_not_cw(geom)
            if criterium == "inner_and_exterior_ring_intersect":
                invalid = checks_invalid.check_inner_and_exterior_ring_intersect(geom)
            if criterium == "defined_crs":
                invalid = checks_invalid.check_defined_crs(feature["geometry"])
            if invalid:
                results_invalid.setdefault(criterium, []).append(i)

        for criterium in criteria_problematic:
            for i, feature in enumerate(features):
                problematic=False
                # Some checks require original GeoJSON, some shapely, structure can not be simplified.
                geom = shape(feature["geometry"])
                if criterium == "holes":
                    problematic = checks_problematic.check_holes(geom)
                if criterium == "self_intersection":
                    problematic = checks_problematic.check_self_intersection(geom)
                # if criterium == "excessive_coordinate_precision":
                #     problematic = checks_problematic.check_excessive_coordinate_precision(feature["geometry"])
                # if criterium == "more_than_2d_coordinates":
                #     problematic = checks_problematic.check_more_than_2d_coordinates(feature["geometry"])
                if criterium == "crosses_antimeridian":
                    problematic = checks_problematic.check_crosses_antimeridian(geom)
                if problematic:
                    results_problematic.setdefault(criterium, []).append(i)

    results = {"invalid": results_invalid, "problematic": results_problematic}
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
