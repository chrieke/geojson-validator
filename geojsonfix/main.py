from typing import Dict, Union, List

import geojson

from .validation import Validation
from .geom import read_geometry_input

VALIDATION_CRITERIA = {
    "invalid": [
        "unclosed",
        "duplicate_nodes",
        "less_three_unique_nodes",
        "exterior_cw",
        "interior_ccw",
        "inner_and_exterior_ring_intersect",
        "defined_crs",
    ],
    "problematic": [
        "holes",
        "selfintersection",
        "excessive_coordinate_precision",
        "more_than_2d_coordinates",
        "crosses_antimeridian",
    ],
}


def validate(
    geojson: Union[geojson.FeatureCollection, str],
    validation_criteria: List[str] = ["invalid", "problematic"],
) -> Dict:
    """
    Validate that a GeoJSON conforms to the geojson specs.

    Args:
        geojson: Input GeoJSON feature collection.
        validation_criteria: A list of validation criteria. Can be of the categories ["invalid", "problematic"], specific validation criteria, or a combination.

    Returns:
        The validated & fixed GeoJSON feature collection.
    """
    df = read_geometry_input(geojson)
    original_json = df.__geo_interface__.copy()
    # fixed_json = original_json.copy()

    criteria = [
        elem for elem in validation_criteria if not "invalid" or not "problematic"
    ]
    if "invalid" in validation_criteria:
        criteria.extend(VALIDATION_CRITERIA["invalid"])
    if "problematic" in validation_criteria:
        criteria.extend(VALIDATION_CRITERIA["problematic"])
    criteria = list(set(criteria))

    validation = Validation(df)
    validation.run_validation_checks(validation_criteria=criteria)

    # TODO: evtl from criteria definition
    validation_results = {
        "unclosed": validation.unclosed,
        "duplicate_nodes": validation.duplicate_nodes,
        "less_three_unique_nodes": validation.less_three_unique_nodes,
        "exterior_cw": validation.exterior_cw,
        "interior_ccw": validation.interior_ccw,
        "inner_and_exterior_ring_intersect": validation.inner_and_exterior_ring_intersect,
        "defined_crs": "validation.defined_crs",
        "holes": validation.holes,
        "selfintersection": validation.selfintersection,
        "excessive_coordinate_precision": validation.excessive_coordinate_precision,
        "more_than_2d_coordinates": validation.more_than_2d_coordinates,
        "crosses_antimeridian": validation.crosses_antimeridian,
    }

    return {
        "invalid": validation.any_invalid,
        "status": validation_results,
        "data_original": original_json,
        # "data_fixed": fixed_json,
    }
