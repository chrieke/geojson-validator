from typing import List
import copy
import sys

from shapely.geometry import shape
from loguru import logger


from . import fixes

logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")


def apply_fix(criterium: str, shapely_geom):
    """Applies the correct check for the criteria"""
    fix_func = getattr(fixes, f"fix_{criterium}")
    return fix_func(shapely_geom)


def process_fix(fc, geometry_validation_results: dict, criteria: List[str]):
    fc_copy = copy.deepcopy(fc)
    for criterium in criteria:
        if criterium in geometry_validation_results["invalid"]:
            indices = geometry_validation_results["invalid"][criterium]
        elif criterium in geometry_validation_results["problematic"]:
            indices = geometry_validation_results["problematic"][criterium]
        else:
            continue
        for idx in indices:
            if isinstance(idx, int):
                geometry = fc_copy["features"][idx]["geometry"]
                if geometry["type"] != "Polygon":
                    logger.info("Currently only fixing polygons, skipping")
                    continue
                geom = shape(geometry)
                geom_fixed = apply_fix(criterium, geom)
                fc_copy["features"][idx]["geometry"] = geom_fixed.__geo_interface__
            elif isinstance(idx, dict):  # multitype geometry e.g. idx is {0: [1, 2]}
                idx, indices_subgeoms = list(idx.items())[0]
                for idx_subgeom in indices_subgeoms:
                    if not isinstance(idx_subgeom, int):
                        raise TypeError(
                            "Fixing Multigeometries within Multigeometries not supported."
                        )
                    subgeom = shape(fc_copy["features"][idx]["geometry"]).geoms[
                        idx_subgeom
                    ]
                    subgeom_fixed = apply_fix(criterium, subgeom)
                    fc_copy["features"][idx]["geometry"][
                        idx_subgeom
                    ] = subgeom_fixed.__geo_interface__

    return fc_copy
