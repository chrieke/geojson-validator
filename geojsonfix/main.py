from typing import Dict, Union, List
import sys
from collections import Counter

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
        "crs_defined",
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

    check_criteria(criteria_invalid, invalid=True)
    logger.info(f"Validation for criteria_invalid: {criteria_invalid}")
    check_criteria(criteria_problematic, problematic=True)
    logger.info(f"Validation for criteria_problematic: {criteria_problematic}")

    results_invalid, results_problematic = {}, {}

    if "crs_defined" in criteria_invalid:
        # is defined on fc level, not feature
        if type_ == "FeatureCollection":
            if checks_invalid.check_crs_defined(geojson):
                # TODO: Different responses, all true instead and position different response element?
                results_invalid["crs_defined"] = True

    geometry_types = []
    for i, feature in enumerate(features):
        geometry_type = feature.get("geometry", None).get("type", None)
        if geometry_type is None:
            raise ValueError("The feature must contain a geometry of type Polygon")
        else:
            geometry_types.append(geometry_type)
        if geometry_type != "Polygon":
            logger.info(f"Geometry of type {geometry_type} currently not supported, skipping.")
            continue
        # TODO: If multipolygon loop the bottom part over it.


        geom = shape(feature["geometry"])

        if criteria_invalid:
            if "unclosed" in criteria_invalid:
                if checks_invalid.check_unclosed(feature["geometry"]):
                    results_invalid.setdefault("unclosed", []).append(i)
            if "duplicate_nodes" in criteria_invalid:
                if checks_invalid.check_duplicate_nodes(feature["geometry"]):
                    results_invalid.setdefault("duplicate_nodes", []).append(i)
            if "less_three_unique_nodes" in criteria_invalid:
                if checks_invalid.check_less_three_unique_nodes(feature["geometry"]):
                    results_invalid.setdefault("less_three_unique_nodes", []).append(i)
            if "exterior_not_ccw" in criteria_invalid:
                if checks_invalid.check_exterior_not_ccw(geom):
                    results_invalid.setdefault("exterior_not_ccw", []).append(i)
            if "interior_not_cw" in criteria_invalid:
                if checks_invalid.check_interior_not_cw(geom):
                    results_invalid.setdefault("interior_not_cw", []).append(i)
            if "inner_and_exterior_ring_intersect" in criteria_invalid:
                if checks_invalid.check_inner_and_exterior_ring_intersect(geom):
                    results_invalid.setdefault(
                        "inner_and_exterior_ring_intersect", []
                    ).append(i)

        if criteria_problematic:
            if "holes" in criteria_problematic:
                if checks_problematic.check_holes(geom):
                    results_problematic.setdefault("holes", []).append(i)
            if "self_intersection" in criteria_problematic:
                if checks_problematic.check_self_intersection(geom):
                    results_problematic.setdefault("self_intersection", []).append(i)
            # if "excessive_coordinate_precision" in criteria_problematic:
            #     if checks_problematic.check_excessive_coordinate_precision(feature["geometry"]):
            #         results_problematic.setdefault("excessive_coordinate_precision", []).append(i)
            # if "more_than_2d_coordinates" in criteria_problematic:
            #     if checks_problematic.check_more_than_2d_coordinates(feature["geometry"]):
            #         results_problematic.setdefault("more_than_2d_coordinates", []).append(i)
            if "crosses_antimeridian" in criteria_problematic:
                if checks_problematic.check_crosses_antimeridian(geom):
                    results_problematic.setdefault("crosses_antimeridian", []).append(i)

    results = {"invalid": results_invalid, "problematic": results_problematic, "count_geometry_types": Counter(geometry_types)}
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
