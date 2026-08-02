from typing import List, Union
import copy

from shapely.geometry import shape
from loguru import logger


from . import fixes


def apply_fix(criterium: str, shapely_geom):
    """Applies the correct fix for the criteria"""
    fix_func = getattr(fixes, f"fix_{criterium}")
    return fix_func(shapely_geom)


def deep_list(obj):
    """Converts nested coordinate tuples (e.g. from __geo_interface__) to plain JSON-style lists."""
    if isinstance(obj, dict):
        return {key: deep_list(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [deep_list(value) for value in obj]
    return obj


def fix_single_geometry(geometry: dict, criterium: str) -> Union[dict, None]:
    """Fixes one single-type geometry dict, returns the fixed geometry dict or None if not fixable."""
    if geometry["type"] != "Polygon":
        logger.info("Currently only fixing polygons, skipping")
        return None
    try:
        geom = shape(geometry)
    except (TypeError, ValueError):
        logger.info("Geometry could not be parsed by shapely, skipping fix.")
        return None
    return deep_list(apply_fix(criterium, geom).__geo_interface__)


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
                fixed = fix_single_geometry(geometry, criterium)
                if fixed is not None:
                    fc_copy["features"][idx]["geometry"] = fixed
            elif isinstance(idx, dict):  # multitype geometry e.g. idx is {0: [1, 2]}
                idx, indices_subgeoms = next(iter(idx.items()))
                geometry = fc_copy["features"][idx]["geometry"]
                for idx_subgeom in indices_subgeoms:
                    if not isinstance(idx_subgeom, int):
                        raise TypeError(
                            "Fixing Multigeometries within Multigeometries not supported."
                        )
                    if geometry["type"] == "GeometryCollection":
                        subgeometry = geometry["geometries"][idx_subgeom]
                    else:  # e.g. MultiPolygon -> Polygon
                        subgeometry = {
                            "type": geometry["type"].replace("Multi", ""),
                            "coordinates": geometry["coordinates"][idx_subgeom],
                        }
                    fixed = fix_single_geometry(subgeometry, criterium)
                    if fixed is None:
                        continue
                    if geometry["type"] == "GeometryCollection":
                        geometry["geometries"][idx_subgeom] = fixed
                    else:
                        geometry["coordinates"][idx_subgeom] = fixed["coordinates"]

    return fc_copy
