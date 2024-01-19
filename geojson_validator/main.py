from typing import Dict, Union, List, Tuple, Any
import sys
from pathlib import Path

from loguru import logger

from .schema_validation import GeoJsonLint
from .geometry_utils import (
    input_to_geojson,
    any_geojson_to_featurecollection,
)
from .geometry_validation import (
    VALIDATION_CRITERIA,
    check_criteria,
    process_validation,
)
from .fixes_utils import process_fix

logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")


def validate_structure(
    geojson_input: Union[dict, str, Path, Any], check_crs: bool = False
) -> Tuple[bool, Union[str, None]]:
    """
    Returns (True, None) if the input geojson conforms to the geojson json schema v7,
    and (False, "reason") if not.
    Enhances error messages by specifying which elements failed validation.
    """
    geojson_data = input_to_geojson(geojson_input)
    errors = GeoJsonLint(check_crs=check_crs).lint(geojson_data)
    return errors


def validate_geometries(
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
    check_criteria(criteria_invalid, VALIDATION_CRITERIA["invalid"], name="invalid")
    check_criteria(
        criteria_problematic, VALIDATION_CRITERIA["problematic"], name="problematic"
    )

    geojson_input = input_to_geojson(geojson_input)
    fc = any_geojson_to_featurecollection(geojson_input)

    geometries = [feature["geometry"] for feature in fc["features"]]
    results = process_validation(geometries, criteria_invalid, criteria_problematic)

    logger.info(f"Validation results: {results}")
    return results


def fix_geometries(
    geojson_input: Union[dict, str, Path, Any],
    optional=[
        "excessive_coordinate_precision",
        "duplicate_nodes",
    ],
):
    criteria = [
        "unclosed",
        "exterior_not_ccw",
        "interior_not_cw",
    ]
    allowed_optional = [
        "excessive_coordinate_precision",
        "duplicate_nodes",
    ]
    check_criteria(optional, allowed_optional, name="optional")

    geometry_validation_results = validate_geometries(
        geojson_input,
        criteria_invalid=criteria,
        criteria_problematic=optional,
    )
    geojson_input = input_to_geojson(geojson_input)
    validate_structure(geojson_input)
    fc = any_geojson_to_featurecollection(geojson_input)

    if optional:
        criteria.extend(optional)
    fixed_fc = process_fix(fc, geometry_validation_results, criteria)
    return fixed_fc
