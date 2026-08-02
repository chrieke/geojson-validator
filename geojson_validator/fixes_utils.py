from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import copy

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry
from shapely.errors import ShapelyError
from loguru import logger


from . import fixes


def apply_fix(criterium: str, shapely_geom: BaseGeometry) -> BaseGeometry:
    """Applies the correct fix for the criteria"""
    fix_func = getattr(fixes, f"fix_{criterium}")
    return fix_func(shapely_geom)


def deep_list(obj: Any) -> Any:
    """Converts nested coordinate tuples (e.g. from __geo_interface__) to plain JSON-style lists."""
    if isinstance(obj, dict):
        return {key: deep_list(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [deep_list(value) for value in obj]
    return obj


def fix_single_geometry(geometry: dict, criteria: Sequence[str]) -> Union[dict, None]:
    """
    Applies all given fixes to one single-type geometry dict, in order.

    Returns the fixed geometry dict, or None if the geometry cannot be fixed. Parsing and
    serialising once for all criteria, instead of per criterium, avoids a round trip
    through __geo_interface__ that costs far more than the fixes themselves.
    """
    if geometry["type"] != "Polygon":
        logger.info("Currently only fixing polygons, skipping")
        return None
    try:
        geom = shape(geometry)
        for criterium in criteria:
            geom = apply_fix(criterium, geom)
    except (TypeError, ValueError, ShapelyError):
        # Parsing fails on e.g. mixed 2D/3D coordinates, and a fix can fail on its own:
        # remove_repeated_points raises GEOSException on a fully degenerate ring.
        logger.info("Geometry could not be parsed or fixed by shapely, skipping fix.")
        return None
    return deep_list(geom.__geo_interface__)


def _group_criteria_by_target(
    geometry_validation_results: Dict[str, Any], criteria: Sequence[str]
) -> Dict[Tuple[int, Optional[int]], List[str]]:
    """
    Maps each flagged geometry to the criteria flagging it, keeping the criteria order.

    Targets are keyed as (feature index, sub-geometry index), with a sub-geometry index of
    None for a whole feature. Those are distinct slots and must not be merged.
    """
    targets: Dict[Tuple[int, Optional[int]], List[str]] = {}
    for criterium in criteria:
        if criterium in geometry_validation_results["invalid"]:
            indices = geometry_validation_results["invalid"][criterium]
        elif criterium in geometry_validation_results["problematic"]:
            indices = geometry_validation_results["problematic"][criterium]
        else:
            continue
        for idx in indices:
            if isinstance(idx, int):
                targets.setdefault((idx, None), []).append(criterium)
            elif isinstance(idx, dict):  # multitype geometry e.g. idx is {0: [1, 2]}
                idx, indices_subgeoms = next(iter(idx.items()))
                for idx_subgeom in indices_subgeoms:
                    if not isinstance(idx_subgeom, int):
                        raise TypeError(
                            "Fixing Multigeometries within Multigeometries not supported."
                        )
                    targets.setdefault((idx, idx_subgeom), []).append(criterium)
    return targets


def process_fix(
    fc: dict, geometry_validation_results: Dict[str, Any], criteria: Sequence[str]
) -> Dict[str, Any]:
    fc_copy = copy.deepcopy(fc)
    targets = _group_criteria_by_target(geometry_validation_results, criteria)

    for (idx, idx_subgeom), target_criteria in targets.items():
        geometry = fc_copy["features"][idx]["geometry"]
        is_collection = geometry["type"] == "GeometryCollection"

        if idx_subgeom is None:
            subgeometry = geometry
        elif is_collection:
            subgeometry = geometry["geometries"][idx_subgeom]
        else:  # e.g. MultiPolygon -> Polygon
            subgeometry = {
                "type": geometry["type"].replace("Multi", ""),
                "coordinates": geometry["coordinates"][idx_subgeom],
            }

        fixed = fix_single_geometry(subgeometry, target_criteria)
        if fixed is None:
            continue
        if idx_subgeom is None:
            fc_copy["features"][idx]["geometry"] = fixed
        elif is_collection:
            geometry["geometries"][idx_subgeom] = fixed
        else:
            geometry["coordinates"][idx_subgeom] = fixed["coordinates"]

    return fc_copy
