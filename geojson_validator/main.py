from typing import Any, Dict, Sequence, Union, TYPE_CHECKING
import sys
from pathlib import Path

from loguru import logger

from .schema_validation import GeoJsonLint
from .geometry_utils import (
    input_to_geojson,
    any_geojson_to_featurecollection,
)
from .geometry_validation import (
    INVALID_CRITERIA,
    PROBLEMATIC_CRITERIA,
    check_criteria,
    process_validation,
)
from .fixes_utils import process_fix

if TYPE_CHECKING:
    from loguru import Logger

logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")


def validate_structure(
    geojson_input: Union[dict, str, Path, Any], check_crs: bool = False
) -> Dict[str, Any]:
    """
    Validate that the input conforms to the GeoJSON json schema.

    Args:
        geojson_input: Input GeoJSON FeatureCollection, Feature, Geometry or filepath/url to (Geo)JSON.
        check_crs: Also flag a crs member, which the GeoJSON specification disallows.

    Returns:
        A dictionary of error messages with the affected json paths and feature indices, e.g.
        {"Missing 'type' member": {"path": ["/features/0"], "feature": [0]}}.
        Empty if the structure is valid.
    """
    geojson_data = input_to_geojson(geojson_input)
    errors = GeoJsonLint(check_crs=check_crs).lint(geojson_data)
    logger.info(f"Structure validation results: {errors}")
    return errors


def validate_geometries(
    geojson_input: Union[dict, str, Path, Any],
    criteria_invalid: Sequence[str] = INVALID_CRITERIA,
    criteria_problematic: Sequence[str] = PROBLEMATIC_CRITERIA,
) -> Dict[str, Any]:
    """
    Validate that a GeoJSON conforms to the geojson specs.

    Args:
        geojson_input: Input GeoJSON FeatureCollection, Feature, Geometry or filepath/url to (Geo)JSON.
        criteria_invalid: A list of validation criteria that are invalid according the GeoJSON specification.
        criteria_problematic: A list of validation criteria that are valid, but problematic with some tools.

    Returns:
        A dictionary with the violated criteria and the affected feature indices, e.g.
        {"invalid": {"unclosed": [0]}, "problematic": {}, ...}.
    """
    if not criteria_invalid and not criteria_problematic:
        raise ValueError(
            "Select at least one criteria in `criteria_invalid` or `criteria_problematic`"
        )
    check_criteria(criteria_invalid, INVALID_CRITERIA, name="invalid")
    check_criteria(criteria_problematic, PROBLEMATIC_CRITERIA, name="problematic")

    geojson_input = input_to_geojson(geojson_input)
    fc = any_geojson_to_featurecollection(geojson_input)

    # A missing geometry member is treated like an explicit null geometry, which
    # process_validation already reports as skipped.
    geometries = [feature.get("geometry") for feature in fc["features"]]
    results = process_validation(geometries, criteria_invalid, criteria_problematic)

    logger.info(f"Validation results: {results}")
    return results


def fix_geometries(
    geojson_input: Union[dict, str, Path, Any],
    optional: Sequence[str] = ("duplicate_nodes",),
) -> Dict[str, Any]:
    """
    Fix invalid geometries in the GeoJSON.

    Always applies the fixes for ["unclosed", "exterior_not_ccw", "interior_not_cw"].

    Args:
        geojson_input: Input GeoJSON FeatureCollection, Feature, Geometry or filepath/url to (Geo)JSON.
        optional: Additional, non-essential fixes, one of ["duplicate_nodes"].

    Returns:
        The GeoJSON feature collection with fixed geometries.
    """
    criteria = [
        "unclosed",
        "exterior_not_ccw",
        "interior_not_cw",
    ]
    allowed_optional = ["duplicate_nodes"]
    check_criteria(optional, allowed_optional, name="optional")
    optional = list(optional or [])

    geojson_input = input_to_geojson(geojson_input)
    geometry_validation_results = validate_geometries(
        geojson_input,
        criteria_invalid=criteria,
        criteria_problematic=optional,
    )
    fc = any_geojson_to_featurecollection(geojson_input)

    # The optional criteria go last: they are the ones that can remove nodes.
    all_criteria = [*criteria, *optional]
    fixed_fc = process_fix(fc, geometry_validation_results, all_criteria)
    logger.info(f"Fixed geometries for criteria {all_criteria}")
    return fixed_fc


def configure_logging(enabled: bool = True, level: str = "INFO") -> "Logger":
    """
    Configures the library logging behavior.

    Args:
        enabled: If False, disables all logging.
        level: Logging level, e.g., 'INFO', 'DEBUG', 'WARNING', 'ERROR'.

    Returns:
        The configured loguru logger instance.
    """
    logger.remove()  # Clear all existing loggers
    if enabled:
        logger.add(sink=sys.stderr, format=logger_format, level=level)
    return logger
