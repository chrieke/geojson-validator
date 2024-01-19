from typing import List
import sys
from collections import Counter

from loguru import logger

from . import checks_invalid, checks_problematic
from .geometry_utils import prepare_geometries_for_checks, extract_single_geometries

logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")


ALL_ACCEPTED_GEOMETRY_TYPES = POI, MPOI, LS, MLS, POL, MPOL, GC = [
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
    "GeometryCollection",
]

VALIDATION_CRITERIA = {
    "invalid": {
        "unclosed": {"relevant": [POL], "input": "json_geometry"},
        "less_three_unique_nodes": {
            "relevant": [POL],
            "input": "json_geometry",
        },
        "exterior_not_ccw": {
            "relevant": [POL],
            "input": "shapely_geom",
        },
        "interior_not_cw": {
            "relevant": [POL],
            "input": "shapely_geom",
        },
        "inner_and_exterior_ring_intersect": {
            "relevant": [POL],
            "input": "shapely_geom",
        },
        # "zero-length": {"relevant": ["LineString"], "input": "json_geometry"},
    },
    "problematic": {
        "holes": {"relevant": [POL], "input": "shapely_geom"},
        "self_intersection": {
            "relevant": [POL],
            "input": "shapely_geom",
        },
        "duplicate_nodes": {
            "relevant": [LS, POL],
            "input": "json_geometry",
        },
        "excessive_coordinate_precision": {
            "relevant": [POI, LS, POL],
            "input": "json_geometry",
        },
        "excessive_vertices": {
            "relevant": [LS, POL],
            "input": "json_geometry",
        },
        "3d_coordinates": {
            "relevant": [POI, LS, POL],
            "input": "json_geometry",
        },
        "outside_lat_lon_boundaries": {
            "relevant": [POI, LS, POL],
            "input": "json_geometry",
        },
        "crosses_antimeridian": {
            "relevant": [LS, POL],
            "input": "json_geometry",
        },
        # "wrong_bbox_order: {}"
    },
}


def check_criteria(
    selected_criteria: List[str], allowed_criteria: List[str], name: str
):
    if selected_criteria:
        for criterium in selected_criteria:
            if criterium not in allowed_criteria:
                raise ValueError(
                    f"The selected criterium {criterium} is not a valid argument for {name}"
                )
        logger.info(f"Criteria '{name}': {selected_criteria}")


def apply_check(
    criterium, single_geometry, shapely_geom, geometry_type, criteria_type="invalid"
):
    """Applies the correct check for the criteria. Only accepts single geometries."""
    geometry_input_options = {
        "json_geometry": single_geometry,
        "shapely_geom": shapely_geom,
    }
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
        if geometry is None:
            logger.info("Null geometry found in GeoJSON Feature, skipping.")
            skipped_validation.append(i)
            continue
        geometry_type = geometry.get("type", None)
        geometry_types.append(geometry_type)
        if geometry_type not in ALL_ACCEPTED_GEOMETRY_TYPES:
            logger.info(
                f"Geometry of type {geometry_type} currently not supported, skipping."
            )
            skipped_validation.append(i)  # TODO: Improve skipped_validation result
            continue

        # Handle Multi-Geometries & Geometrycollections:
        # Extract the single geometries in the multi-geometry/collection, run a separate validation on each.
        # Output results in this style: {3: [1,2]} (fourth geometry, the multigeometry is invalid,
        # because the second and third sub-geometries in it are invalid).
        if "Multi" in geometry_type or geometry_type == "GeometryCollection":
            single_geometries = extract_single_geometries(geometry, geometry_type)
            results_multi = process_validation(
                single_geometries, criteria_invalid, criteria_problematic
            )
            # Take all invalid criteria from the e.g. Polygons inside the Multipolygon and indicate them
            # as the positional index of the MultiPolygon.
            for criterium in results_multi["invalid"]:
                results_invalid.setdefault(criterium, []).append(
                    {i: results_multi["invalid"][criterium]}
                )
            for criterium in results_multi["problematic"]:
                results_problematic.setdefault(criterium, []).append(
                    {i: results_multi["problematic"][criterium]}
                )
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
