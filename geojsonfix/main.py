from typing import Dict, Union, List
import sys
from collections import Counter
from pathlib import Path

from loguru import logger
from shapely.geometry import shape

from . import checks_invalid
from . import checks_problematic
from .geometry_utils import get_geometries


logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")

VALIDATION_CRITERIA = {
    "invalid": {
        "unclosed": {"relevant": ["Polygon", "MultiPolygon"], "input": "json_geometry"},
        "duplicate_nodes": {
            "relevant": ["LineString", "MultiLineString", "Polygon", "MultiPolygon"],
            "input": "json_geometry",
        },
        "less_three_unique_nodes": {
            "relevant": ["Polygon", "MultiPolygon"],
            "input": "json_geometry",
        },
        "exterior_not_ccw": {
            "relevant": ["Polygon", "MultiPolygon"],
            "input": "shapely_geom",
        },
        "interior_not_cw": {
            "relevant": ["Polygon", "MultiPolygon"],
            "input": "shapely_geom",
        },
        "inner_and_exterior_ring_intersect": {
            "relevant": ["Polygon", "MultiPolygon"],
            "input": "shapely_geom",
        },
        "outside_lat_lon_boundaries": {
            "relevant": [
                "Point",
                "MultiPoint",
                "Linestring",
                "MultiLineString",
                "Polygon",
                "MultiPolygon",
            ],
            "input": "json_geometry",
        },
        "crs_defined": {
            "relevant": ["FeatureCollection"],
            "input": "json_geometry",
        },  # TODO
        # "zero-length": {"relevant": ["LineString"], "input": "json_geometry"},
    },
    "problematic": {
        "holes": {"relevant": ["Polygon", "MultiPolygon"], "input": "shapely_geom"},
        "self_intersection": {
            "relevant": ["Polygon", "MultiPolygon"],
            "input": "shapely_geom",
        },
        "excessive_coordinate_precision": {
            "relevant": [
                "Point",
                "MultiPoint",
                "Linestring",
                "MultiLineString",
                "Polygon",
                "MultiPolygon",
            ],
            "input": "json_geometry",
        },
        "more_than_2d_coordinates": {
            "relevant": [
                "Point",
                "MultiPoint",
                "Linestring",
                "MultiLineString",
                "Polygon",
                "MultiPolygon",
            ],
            "input": "json_geometry",
        },
        "crosses_antimeridian": {
            "relevant": ["Linestring", "MultiLineString", "Polygon", "MultiPolygon"],
            "input": "json_geometry",
        },
        # "wrong_bbox_order: {}"
    },
}


def check_criteria(selected_criteria, criteria_type):
    for criterium in selected_criteria:
        if criterium not in VALIDATION_CRITERIA[criteria_type]:
            raise ValueError(
                f"The selected criterium {criterium} is not a valid argument for {criteria_type}"
            )
    logger.info(f"Validation criteria '{criteria_type}': {selected_criteria}")


def process_validation(geometries, criteria_invalid, criteria_problematic):
    results_invalid, results_problematic = {}, {}
    skipped_validation = []
    geometry_types = []

    for i, geometry in enumerate(geometries):
        geometry_type = geometry.get("type", None)
        if geometry_type is None:
            raise ValueError("no 'geometry' field found in GeoJSON Feature")
        geometry_types.append(geometry_type)
        if geometry_type not in [
            "Point",
            "MultiPoint",
            "LineString",
            "Polygon",
            "MultiPolygon",
        ]:  # TODO
            logger.info(
                f"Geometry of type {geometry_type} currently not supported, skipping."
            )
            skipped_validation.append(i)
            continue
        if "Multi" in geometry_type:
            single_type = geometry_type.split("Multi")[1]
            single_geometries = [
                {"type": single_type, "coordinates": g} for g in geometry["coordinates"]
            ]
            results_mp = process_validation(
                single_geometries, criteria_invalid, criteria_problematic
            )
            # Take all invalid criteria from the e.g. Polygons inside the Multipolygon and indicate them
            # as the position index of the MultiPolygon.
            for criterium in results_mp["invalid"]:
                results_invalid.setdefault(criterium, []).append(i)
            for criterium in results_mp["problematic"]:
                results_problematic.setdefault(criterium, []).append(i)
            continue

        # Some criteria require the original json geometry dict as shapely etc. autofixes (e.g. closes) geometries.
        # Initiating the shapely type in each check function specifically is time intensive.
        input_options = {"json_geometry": geometry, "shapely_geom": shape(geometry)}

        for criterium in criteria_invalid:
            if geometry_type in VALIDATION_CRITERIA["invalid"][criterium]["relevant"]:
                check_func = getattr(checks_invalid, f"check_{criterium}")
                if check_func(
                    input_options[VALIDATION_CRITERIA["invalid"][criterium]["input"]]
                ):
                    results_invalid.setdefault(criterium, []).append(i)

        for criterium in criteria_problematic:
            if (
                geometry_type
                in VALIDATION_CRITERIA["problematic"][criterium]["relevant"]
            ):
                check_func = getattr(checks_problematic, f"check_{criterium}")
                if check_func(
                    input_options[
                        VALIDATION_CRITERIA["problematic"][criterium]["input"]
                    ]
                ):
                    results_problematic.setdefault(criterium, []).append(i)

    results = {
        "invalid": results_invalid,
        "problematic": results_problematic,
        "count_geometry_types": dict(Counter(geometry_types)),
        "skipped_validation": skipped_validation,
    }

    return results


def validate(
    geojson_input: Union[dict, str, Path],
    criteria_invalid: Union[List[str], None] = VALIDATION_CRITERIA["invalid"],
    criteria_problematic: Union[List[str], None] = VALIDATION_CRITERIA["problematic"],
) -> Dict:
    """
    Validate that a GeoJSON conforms to the geojson specs.

    Args:
        geojson: Input GeoJSON FeatureCollection, Feature, Geometry or filepath to (Geo)JSON/file.
        criteria_invalid: A list of validation criteria that are invalid according the GeoJSON specification.
        criteria_problematic: A list of validation criteria that are valid, but problematic with some tools.

    Returns:
        The validated & fixed GeoJSON feature collection.
    """
    check_criteria(criteria_invalid, criteria_type="invalid")
    check_criteria(criteria_problematic, criteria_type="problematic")

    type_, geometries = get_geometries(geojson_input)

    results = process_validation(geometries, criteria_invalid, criteria_problematic)

    if "crs_defined" in criteria_invalid:
        if type_ == "FeatureCollection":
            if checks_invalid.check_crs_defined(geojson_input):
                results["invalid"]["crs_defined"] = True

    logger.info(f"Validation results: {results}")
    return results


# def fix(
#     geojson,
#     criteria_invalid: Union[List[str], None] = VALIDATION_CRITERIA["invalid"],
#     criteria_problematic: Union[List[str], None] = VALIDATION_CRITERIA["problematic"],
# ):
#     pass
