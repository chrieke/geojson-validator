from typing import Dict, Union, List
import sys
from collections import Counter

from loguru import logger
from shapely.geometry import shape

from . import checks_invalid
from . import checks_problematic

logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")

VALIDATION_CRITERIA = {
    "invalid": {
        "unclosed": "json_geometry",
        "duplicate_nodes": "json_geometry",
        "less_three_unique_nodes": "json_geometry",
        "exterior_not_ccw": "shapely_geom",
        "interior_not_cw": "shapely_geom",
        "inner_and_exterior_ring_intersect": "shapely_geom",
        "crs_defined": "json_geometry",
        "outside_lat_lon_boundaries": "json_geometry",
    },
    "problematic": {
        "holes": "shapely_geom",
        "self_intersection": "shapely_geom",
        "excessive_coordinate_precision": "json_geometry",
        "more_than_2d_coordinates": "json_geometry",
        "crosses_antimeridian": "json_geometry",
    },
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
    results.setdefault(key, []).append(index)


def process_geometries_validation(geometries, criteria_invalid, criteria_problematic):
    results_invalid, results_problematic = {}, {}
    geometry_types = []

    for i, geometry in enumerate(geometries):
        geometry_type = geometry.get("type", None)
        if geometry_type is None:
            raise ValueError("no 'geometry' field found in GeoJSON Feature")
        geometry_types.append(geometry_type)
        if geometry_type not in ["Polygon", "MultiPolygon"]:  # TODO: Multipolygon
            logger.info(
                f"Geometry of type {geometry_type} currently not supported, skipping."
            )
            continue

        # Some criteria require the original json geometry dict as shapely etc. autofixes (e.g. closes) geometries.
        # Initiating the shapely type in each check function specifically is time intensive.
        input_options = {"json_geometry": geometry, "shapely_geom": shape(geometry)}

        for criterium in criteria_invalid:
            check_func = getattr(checks_invalid, f"check_{criterium}")
            if check_func(input_options[VALIDATION_CRITERIA["invalid"][criterium]]):
                append_result(results_invalid, criterium, i)

        for criterium in criteria_problematic:
            check_func = getattr(checks_problematic, f"check_{criterium}")
            if check_func(input_options[VALIDATION_CRITERIA["problematic"][criterium]]):
                append_result(results_problematic, criterium, i)

    results = {
        "invalid": results_invalid,
        "problematic": results_problematic,
        "count_geometry_types": dict(Counter(geometry_types)),
    }

    return results


def validate(
    geojson_input: Union[dict, str],
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
    elif type_ in ["Polygon", "MultiPolygon"]:  # TODO: Add MultiPolygon
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
