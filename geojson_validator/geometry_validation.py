from typing import List, Dict, Any, Optional, Tuple
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


def process_validate_geometries(
    geometries: List[Optional[Dict[str, Any]]],
    criteria_invalid: Optional[List[str]],
    criteria_problematic: Optional[List[str]],
) -> Dict[str, Any]:
    results_invalid, results_problematic = {}, {}
    skipped_validation = []
    geometry_types = []

    # For each geometry, record issues, skipped validation, types and position of the offerender.
    for i, geometry in enumerate(geometries):
        if geometry is None:
            logger.info("Null geometry found in GeoJSON Feature, skipping validation.")
            skipped_validation.append(i)
            continue

        geometry_type = geometry.get("type", None)
        geometry_types.append(geometry_type)

        if geometry_type not in ALL_ACCEPTED_GEOMETRY_TYPES:
            logger.info(
                f"Geometry of type {geometry_type} currently not supported, skipping."
            )
            skipped_validation.append(i)
            continue

        # Handle Multi-Geometries & Geometrycollections
        if _is_multi_geometry(geometry_type):
            multi_invalid, multi_problematic = _handle_multi_geometry(
                geometry, geometry_type, i, criteria_invalid, criteria_problematic
            )
            _merge_results(results_invalid, multi_invalid)
            _merge_results(results_problematic, multi_problematic)
            continue

        # Handle Single-Geometries
        geometry, shapely_geom = prepare_geometries_for_checks(geometry)
        single_invalid, single_problematic = _validate_single_geometry(
            geometry,
            shapely_geom,
            geometry_type,
            i,
            criteria_invalid,
            criteria_problematic,
        )
        _merge_results(results_invalid, single_invalid)
        _merge_results(results_problematic, single_problematic)

    # TODO: Results format better: feature1: flaws, feature4: flaws, feature9: flaws?
    results = {
        "invalid": results_invalid,
        "problematic": results_problematic,
        "count_geometry_types": dict(Counter(geometry_types)),
        "skipped_validation": skipped_validation,
    }

    return results


def apply_check(
    criterium: str,
    single_geometry: Dict[str, Any],
    shapely_geom: Any,
    geometry_type: str,
    criteria_type: str = "invalid",
) -> Optional[bool]:
    """Apply the correct check for the criteria. Only accepts single geometries.

    Args:
        criterium: The validation criterion to check
        single_geometry: The GeoJSON geometry as a dictionary
        shapely_geom: The Shapely geometry object
        geometry_type: The type of geometry (Point, Polygon, etc.)
        criteria_type: Either "invalid" or "problematic"

    Returns:
        True if the check fails (geometry has the issue), False if passes, None if not applicable
    """
    if criteria_type not in VALIDATION_CRITERIA:
        return None

    if criterium not in VALIDATION_CRITERIA[criteria_type]:
        return None

    criterion_config = VALIDATION_CRITERIA[criteria_type][criterium]
    relevant_geometry_types = criterion_config["relevant"]

    if geometry_type not in relevant_geometry_types:
        return None

    # Select appropriate input based on configuration
    geometry_input = (
        single_geometry
        if criterion_config["input"] == "json_geometry"
        else shapely_geom
    )

    # Get the appropriate check module and function
    check_module = checks_invalid if criteria_type == "invalid" else checks_problematic
    check_func = getattr(check_module, f"check_{criterium}")

    return check_func(geometry_input)


def _is_multi_geometry(geometry_type: str) -> bool:
    """Check if geometry is a multi-geometry or geometry collection."""
    return "Multi" in geometry_type or geometry_type == "GeometryCollection"


def _handle_multi_geometry(
    geometry: Dict[str, Any],
    geometry_type: str,
    index: int,
    criteria_invalid: Optional[List[str]],
    criteria_problematic: Optional[List[str]],
) -> Tuple[Dict[str, List], Dict[str, List]]:
    """Handle validation of multi-geometries and geometry collections."""
    single_geometries = extract_single_geometries(geometry, geometry_type)
    results_multi = process_validate_geometries(
        single_geometries, criteria_invalid, criteria_problematic
    )

    results_invalid, results_problematic = {}, {}

    # Map multi-geometry results to the parent geometry index
    for criterium in results_multi["invalid"]:
        results_invalid.setdefault(criterium, []).append(
            {index: results_multi["invalid"][criterium]}
        )
    for criterium in results_multi["problematic"]:
        results_problematic.setdefault(criterium, []).append(
            {index: results_multi["problematic"][criterium]}
        )

    return results_invalid, results_problematic


def _validate_single_geometry(
    geometry: Dict[str, Any],
    shapely_geom: Any,
    geometry_type: str,
    index: int,
    criteria_invalid: Optional[List[str]],
    criteria_problematic: Optional[List[str]],
) -> Tuple[Dict[str, List], Dict[str, List]]:
    """Validate a single geometry against criteria."""
    results_invalid, results_problematic = {}, {}

    if criteria_invalid:
        for criterium in criteria_invalid:
            if apply_check(criterium, geometry, shapely_geom, geometry_type, "invalid"):
                results_invalid.setdefault(criterium, []).append(index)

    if criteria_problematic:
        for criterium in criteria_problematic:
            if apply_check(
                criterium, geometry, shapely_geom, geometry_type, "problematic"
            ):
                results_problematic.setdefault(criterium, []).append(index)

    return results_invalid, results_problematic


def _merge_results(target_dict: Dict[str, List], source_dict: Dict[str, List]) -> None:
    """Merge validation results from source into target dictionary."""
    for criterium, values in source_dict.items():
        target_dict.setdefault(criterium, []).extend(values)


def check_selected_criteria_are_allowed(
    selected_criteria: List[str], allowed_criteria: List[str], name: str
) -> None:
    """Validate that selected criteria are in allowed criteria list."""
    if selected_criteria:
        for criterium in selected_criteria:
            if criterium not in allowed_criteria:
                raise ValueError(
                    f"The selected criterium {criterium} is not a valid argument for {name}"
                )
        logger.info(f"Criteria '{name}': {selected_criteria}")
