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


def check_criteria(selected_criteria, criteria_type):
    for criterium in selected_criteria:
        if criterium not in VALIDATION_CRITERIA[criteria_type]:
            raise ValueError(
                f"The selected criterium {criterium} is not a valid argument for {criteria_type}"
            )
    logger.info(f"Validation criteria '{criteria_type}': {selected_criteria}")


def validate_geojson_type(geojson):
    # TODO: Add shapely type?
    type_ = geojson.get("type", None)
    if type_ is None:
        raise ValueError("No 'type' field found in GeoJSON")
    if type_ not in ["FeatureCollection", "Feature", "Polygon", "MultiPolygon"]:
        raise ValueError(
            "Only a GeoJSON FeatureCollection, Feature or Polygon/MultiPolygon Geometry are supported as input."
        )
    return type_


def run_checks(geometry, criteria, results, checks_module, index):
    geom = shape(geometry)
    for criterium in criteria:
        # Determine the appropriate input for the check function
        if criterium in [
            "duplicate_nodes",
            "excessive_coordinate_precision",
            "more_than_2d_coordinates",
            "unclosed",
        ]:
            input_data = geometry  # These functions need the raw GeoJSON geometry
        else:
            input_data = geom  # Others need the shapely geometry

        check_function = getattr(checks_module, f"check_{criterium}", None)

        if callable(check_function) and check_function(input_data):
            results.setdefault(criterium, []).append(index)


def append_result(results, key, index):
    if key not in results:
        results[key] = []
    results[key].append(index)


def process_geometries_validation(geometries, criteria_invalid, criteria_problematic):
    results_invalid, results_problematic = {}, {}
    geometry_types = []

    for i, geometry in enumerate(geometries):
        geometry_type = geometry.get("type", None)
        if geometry_type is None:
            raise ValueError("no 'geometry' field found in GeoJSON Feature")
        geometry_types.append(geometry_type)
        if geometry_type != "Polygon":
            logger.info(
                f"Geometry of type {geometry_type} currently not supported, skipping."
            )
            continue
        # TODO: If multipolygon loop the bottom part over it.

        geom = shape(geometry)

        if criteria_invalid:
            if "unclosed" in criteria_invalid and checks_invalid.check_unclosed(
                geometry
            ):
                append_result(results_invalid, "unclosed", i)
            if (
                "duplicate_nodes" in criteria_invalid
                and checks_invalid.check_duplicate_nodes(geometry)
            ):
                append_result(results_invalid, "duplicate_nodes", i)
            if (
                "less_three_unique_nodes" in criteria_invalid
                and checks_invalid.check_less_three_unique_nodes(geometry)
            ):
                append_result(results_invalid, "less_three_unique_nodes", i)
            if (
                "exterior_not_ccw" in criteria_invalid
                and checks_invalid.check_exterior_not_ccw(geom)
            ):
                append_result(results_invalid, "exterior_not_ccw", i)
            if (
                "interior_not_cw" in criteria_invalid
                and checks_invalid.check_interior_not_cw(geom)
            ):
                append_result(results_invalid, "interior_not_cw", i)
            if (
                "inner_and_exterior_ring_intersect" in criteria_invalid
                and checks_invalid.check_inner_and_exterior_ring_intersect(geom)
            ):
                append_result(results_invalid, "inner_and_exterior_ring_intersect", i)

        if criteria_problematic:
            if "holes" in criteria_problematic and checks_problematic.check_holes(geom):
                append_result(results_problematic, "holes", i)
            if (
                "self_intersection" in criteria_problematic
                and checks_problematic.check_self_intersection(geom)
            ):
                append_result(results_problematic, "self_intersection", i)
            if (
                "excessive_coordinate_precision" in criteria_problematic
                and checks_problematic.check_excessive_coordinate_precision(geometry)
            ):
                append_result(results_problematic, "excessive_coordinate_precision", i)
            if (
                "more_than_2d_coordinates" in criteria_problematic
                and checks_problematic.check_more_than_2d_coordinates(geometry)
            ):
                append_result(results_problematic, "more_than_2d_coordinates", i)
            if (
                "crosses_antimeridian" in criteria_problematic
                and checks_problematic.check_crosses_antimeridian(geometry)
            ):
                append_result(results_problematic, "crosses_antimeridian", i)

    results = {
        "invalid": results_invalid,
        "problematic": results_problematic,
        "count_geometry_types": dict(Counter(geometry_types)),
    }

    return results


def validate(
    geojson_input: Union[geojson.FeatureCollection, str],
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
    type_ = validate_geojson_type(geojson_input)
    check_criteria(criteria_invalid, criteria_type="invalid")
    check_criteria(criteria_problematic, criteria_type="problematic")

    # Process based on the type of GeoJSON object
    crs_defined = False
    if type_ == "FeatureCollection":
        # TODO: Validate all required fields
        geometries = [feature["geometry"] for feature in geojson_input["features"]]
        if "crs_defined" in criteria_invalid:
            crs_defined = checks_invalid.check_crs_defined(geojson_input)
    elif type_ == "Feature":
        geometries = [geojson_input["geometry"]]
    elif type_ == "Polygon":  # TODO: Add MultiPolygon
        geometries = [geojson_input]
    else:
        raise ValueError(
            "Only a GeoJSON FeatureCollection, Feature or Polygon/MultiPolygon Geometry are supported as input."
        )

    results = process_geometries_validation(
        geometries, criteria_invalid, criteria_problematic
    )

    if crs_defined:
        results["invalid"] = True
    logger.info(f"Validation results: {results}")
    return results


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
