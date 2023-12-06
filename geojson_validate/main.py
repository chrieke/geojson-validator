from typing import Dict

import geojson

from .validation import Validation


def validate_geojson(geojson_dict: geojson.FeatureCollection) -> Dict:
    """
    Validate that a GeoJSON conforms to the geojson specs.

    Args:
        geojson: Input GeoJSON feature collection.

    Returns:
        The validated & fixed GeoJSON feature collection.
    """
    validation = Validation.from_geojson_dict(geojson_dict=geojson_dict)
    original_json = validation.df.__geo_interface__.copy()
    # fixed_json = original_json.copy()

    validation.run_validation_checks()

    validation_results = {
        "unclosed": validation.unclosed,
        "duplicate_nodes": validation.duplicate_nodes,
        "less_three_unique_nodes": validation.less_three_unique_nodes,
        "exterior_cw": validation.exterior_cw,
        "interior_ccw": validation.interior_ccw,
        "holes": validation.holes,
        "selfintersection": validation.selfintersection,
    }

    return {
        "invalid": validation.any_invalid,
        "status": validation_results,
        "data_original": original_json,
        # "data_fixed": fixed_json,
    }
