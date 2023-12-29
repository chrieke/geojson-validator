from typing import Dict, Union, List
import sys
import copy
from collections import Counter
from pathlib import Path

from loguru import logger
from shapely.geometry import shape

from . import checks_invalid, checks_problematic, fixes_invalid
from .geometry_utils import input_to_featurecollection, prepare_geometries_for_checks


logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")


ALL_ACCEPTED_GEOMETRY_TYPES = POI, MPOI, LS, MLS, POL, MPOL = [
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
]

VALIDATION_CRITERIA = {
    "invalid": {
        "unclosed": {"relevant": [POL, MPOL], "input": "json_geometry"},
        "duplicate_nodes": {
            "relevant": [LS, MLS, POL, MPOL],
            "input": "json_geometry",
        },
        "less_three_unique_nodes": {
            "relevant": [POL, MPOL],
            "input": "json_geometry",
        },
        "exterior_not_ccw": {
            "relevant": [POL, MPOL],
            "input": "shapely_geom",
        },
        "interior_not_cw": {
            "relevant": [POL, MPOL],
            "input": "shapely_geom",
        },
        "inner_and_exterior_ring_intersect": {
            "relevant": [POL, MPOL],
            "input": "shapely_geom",
        },
        "outside_lat_lon_boundaries": {
            "relevant": ALL_ACCEPTED_GEOMETRY_TYPES,
            "input": "json_geometry",
        },
        "crs_defined": {
            "relevant": ["FeatureCollection"],
            "input": "json_geometry",
        },
        # "zero-length": {"relevant": ["LineString"], "input": "json_geometry"},
    },
    "problematic": {
        "holes": {"relevant": [POL, MPOL], "input": "shapely_geom"},
        "self_intersection": {
            "relevant": [POL, MPOL],
            "input": "shapely_geom",
        },
        "excessive_coordinate_precision": {
            "relevant": ALL_ACCEPTED_GEOMETRY_TYPES,
            "input": "json_geometry",
        },
        "more_than_2d_coordinates": {
            "relevant": ALL_ACCEPTED_GEOMETRY_TYPES,
            "input": "json_geometry",
        },
        "crosses_antimeridian": {
            "relevant": [LS, MLS, POL, MPOL],
            "input": "json_geometry",
        },
        # "wrong_bbox_order: {}"
    },
}


def check_criteria(selected_criteria, criteria_type):
    if selected_criteria:
        for criterium in selected_criteria:
            if criterium not in VALIDATION_CRITERIA[criteria_type]:
                raise ValueError(
                    f"The selected criterium {criterium} is not a valid argument for {criteria_type}"
                )
        logger.info(f"Validation criteria '{criteria_type}': {selected_criteria}")


def apply_check(
    criterium, geometry, shapely_geom, geometry_type, criteria_type="invalid"
):
    """Applies the correct check for the criteria"""
    geometry_input_options = {"json_geometry": geometry, "shapely_geom": shapely_geom}
    relevant_geometry_type = VALIDATION_CRITERIA[criteria_type][criterium]["relevant"]
    if geometry_type in relevant_geometry_type:
        check_module = (
            checks_invalid if criteria_type == "invalid" else checks_problematic
        )
        check_func = getattr(check_module, f"check_{criterium}")
        required_input_type = VALIDATION_CRITERIA[criteria_type][criterium]["input"]
        return check_func(geometry_input_options[required_input_type])


def process_validation(geometries, criteria_invalid, criteria_problematic):
    results_invalid, results_problematic = {}, {}
    skipped_validation = []
    geometry_types = []

    for i, geometry in enumerate(geometries):
        geometry_type = geometry.get("type", None)
        if geometry_type is None:
            raise ValueError("no 'geometry' field found in GeoJSON Feature")
        geometry_types.append(geometry_type)
        if geometry_type not in ALL_ACCEPTED_GEOMETRY_TYPES:
            logger.info(
                f"Geometry of type {geometry_type} currently not supported, skipping."
            )
            skipped_validation.append(i)  # TODO: Improve skipped_validation result
            continue

        # Handle Multi-Geometries:
        # Explode the single geometries in the multi-geometry to a featurecollection, run a seperate validation.
        # Output results as {3: [1,2]} (fourth geometry, the multigeometry is invalid, because the second and third
        # subgeometries in it are invalid.
        if "Multi" in geometry_type:
            single_type = geometry_type.split("Multi")[1]
            single_geometries = [
                {"type": single_type, "coordinates": g} for g in geometry["coordinates"]
            ]
            results_mp = process_validation(
                single_geometries, criteria_invalid, criteria_problematic
            )
            # Take all invalid criteria from the e.g. Polygons inside the Multipolygon and indicate them
            # as the positional index of the MultiPolygon.
            for criterium in results_mp["invalid"]:
                results_invalid.setdefault(criterium, []).append(
                    {i: results_mp["invalid"][criterium]}
                )
            for criterium in results_mp["problematic"]:
                results_problematic.setdefault(criterium, []).append(
                    {i: results_mp["problematic"][criterium]}
                )
                # results_problematic.setdefault(criterium, []).append(i)  # TODO: Really better?
            continue

        # Handle Single-Geometries
        geometry, shapely_geom = prepare_geometries_for_checks(geometry)
        if criteria_invalid:
            for criterium in criteria_invalid:
                if apply_check(
                    criterium, geometry, shapely_geom, geometry_type, "invalid"
                ):
                    results_invalid.setdefault(criterium, []).append(i)
        if criteria_problematic:
            for criterium in criteria_problematic:
                if apply_check(
                    criterium, geometry, shapely_geom, geometry_type, "problematic"
                ):
                    results_problematic.setdefault(criterium, []).append(i)

    # TODO: Results format better: feature1: flaws, feature4: flaws, feature9: flaws?
    results = {
        "invalid": results_invalid,
        "problematic": results_problematic,
        "count_geometry_types": dict(Counter(geometry_types)),
        "skipped_validation": skipped_validation,
    }

    return results


def validate(
    geojson_input: Union[dict, str, Path],
    criteria_invalid: List[str] = VALIDATION_CRITERIA["invalid"],
    criteria_problematic: List[str] = VALIDATION_CRITERIA["problematic"],
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
    if not criteria_invalid and not criteria_problematic:
        raise ValueError(
            "Select at least one criteria in `criteria_invalid` or `criteria_problematic`"
        )
    check_criteria(criteria_invalid, criteria_type="invalid")
    check_criteria(criteria_problematic, criteria_type="problematic")

    fc = input_to_featurecollection(geojson_input)

    geometries = [feature["geometry"] for feature in fc["features"]]
    # TODO: Could extract geometries here and use as input as before.
    results = process_validation(geometries, criteria_invalid, criteria_problematic)

    if criteria_invalid and "crs_defined" in criteria_invalid and "crs" in fc:
        results["invalid"]["crs_defined"] = True

    logger.info(f"Validation results: {results}")
    return results


def apply_fix(criterium, shapely_geom):
    """Applies the correct check for the criteria"""
    fix_func = getattr(fixes_invalid, f"fix_{criterium}")
    return fix_func(shapely_geom)


def process_fix(fc, results, criteria_to_fix):
    fc_copy = copy.deepcopy(fc)
    # Fix geometries
    for criterium in criteria_to_fix:
        if (
            criterium in results["invalid"]
        ):  # TODO: Change here if problematic fixes added here
            indices = results["invalid"][criterium]
            for idx in indices:
                if isinstance(idx, int):
                    geom = shape(fc_copy["features"][idx]["geometry"])
                    geom_fixed = apply_fix(criterium, geom)
                elif isinstance(idx, dict):
                    pass  # multitype result
                fc_copy["features"][idx][
                    "geometry"
                ] = geom_fixed.__geo_interface__  # TODO: List instead of tuples
    return fc_copy


def fix(geojson_input):
    criteria_to_fix = [
        "unclosed",
        "duplicate_nodes",
        "exterior_not_ccw",
        "interior_not_cw",
    ]
    results = validate(
        geojson_input, criteria_invalid=criteria_to_fix, criteria_problematic=None
    )
    fc = input_to_featurecollection(geojson_input)

    # Apply results and fix.
    fixed_fc = process_fix(
        fc, results, criteria_to_fix
    )  # TODO: check if the original fc was edited
    return fixed_fc
