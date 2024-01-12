import copy

from shapely.geometry import shape

from . import fixes_invalid


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
        ):  # TODO: Change here if more problematic fixes added here
            indices = results["invalid"][criterium]
            for idx in indices:
                if isinstance(idx, int):
                    geom = shape(fc_copy["features"][idx]["geometry"])
                    geom_fixed = apply_fix(criterium, geom)
                elif isinstance(idx, dict):
                    pass  # multitype result
                fc_copy["features"][idx]["geometry"] = geom_fixed.__geo_interface__
    return fc_copy
