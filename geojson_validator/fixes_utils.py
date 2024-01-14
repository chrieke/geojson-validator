from typing import List
import copy

from shapely.geometry import shape

from . import fixes


def apply_fix(criterium: str, shapely_geom):
    """Applies the correct check for the criteria"""
    fix_func = getattr(fixes, f"fix_{criterium}")
    return fix_func(shapely_geom)


def process_fix(fc, geometry_validation_results: dict, criteria: List[str]):
    fc_copy = copy.deepcopy(fc)
    # TODO: Fix multigeometries in each fix function.
    # TODO: check that applied to correct geometry type.
    for criterium in criteria:
        if criterium in geometry_validation_results["invalid"]:
            indices = geometry_validation_results["invalid"][criterium]
        elif criterium in geometry_validation_results["problematic"]:
            indices = geometry_validation_results["problematic"][criterium]
        else:
            continue
        for idx in indices:
            if isinstance(idx, int):
                geom = shape(fc_copy["features"][idx]["geometry"])
                geom_fixed = apply_fix(criterium, geom)
            elif isinstance(idx, dict):
                pass  # multitype result
            fc_copy["features"][idx]["geometry"] = geom_fixed.__geo_interface__

    # for criterium in criteria_optional:
    #     pass
    return fc_copy
