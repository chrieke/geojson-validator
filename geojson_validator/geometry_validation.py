from typing import Any, Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple
from collections import Counter
from dataclasses import dataclass, field

from loguru import logger
from shapely.geometry.base import BaseGeometry

from . import checks_invalid, checks_problematic
from .geometry_utils import (
    ALL_ACCEPTED_GEOMETRY_TYPES,
    POINT,
    LINESTRING,
    POLYGON,
    to_shapely_or_none,
    extract_single_geometries,
)


@dataclass(frozen=True)
class Check:
    """A validation criterium: what to run it on, and what input form it needs."""

    func: Callable[[Any], bool]
    relevant: FrozenSet[str]
    # Checks that take a shapely geometry rather than the raw json geometry dict. The raw
    # dict is needed by the others because shapely silently repairs (e.g. closes) rings.
    needs_shapely: bool = field(default=False)


VALIDATION_CRITERIA: Dict[str, Dict[str, Check]] = {
    "invalid": {
        "unclosed": Check(checks_invalid.check_unclosed, frozenset({POLYGON})),
        "less_three_unique_nodes": Check(
            checks_invalid.check_less_three_unique_nodes, frozenset({POLYGON})
        ),
        "exterior_not_ccw": Check(
            checks_invalid.check_exterior_not_ccw, frozenset({POLYGON}), True
        ),
        "interior_not_cw": Check(
            checks_invalid.check_interior_not_cw, frozenset({POLYGON}), True
        ),
    },
    "problematic": {
        "holes": Check(checks_problematic.check_holes, frozenset({POLYGON}), True),
        # Valid by the GeoJSON specification, but invalid by the OGC Simple Features standard
        # which many tools follow.
        "inner_and_exterior_ring_intersect": Check(
            checks_problematic.check_inner_and_exterior_ring_intersect,
            frozenset({POLYGON}),
            True,
        ),
        "self_intersection": Check(
            checks_problematic.check_self_intersection, frozenset({POLYGON}), True
        ),
        "duplicate_nodes": Check(
            checks_problematic.check_duplicate_nodes, frozenset({LINESTRING, POLYGON})
        ),
        "excessive_coordinate_precision": Check(
            checks_problematic.check_excessive_coordinate_precision,
            frozenset({POINT, LINESTRING, POLYGON}),
        ),
        "excessive_vertices": Check(
            checks_problematic.check_excessive_vertices,
            frozenset({LINESTRING, POLYGON}),
        ),
        "3d_coordinates": Check(
            checks_problematic.check_3d_coordinates,
            frozenset({POINT, LINESTRING, POLYGON}),
        ),
        "outside_lat_lon_boundaries": Check(
            checks_problematic.check_outside_lat_lon_boundaries,
            frozenset({POINT, LINESTRING, POLYGON}),
        ),
        "crosses_antimeridian": Check(
            checks_problematic.check_crosses_antimeridian,
            frozenset({LINESTRING, POLYGON}),
        ),
    },
}

INVALID_CRITERIA: Tuple[str, ...] = tuple(VALIDATION_CRITERIA["invalid"])
PROBLEMATIC_CRITERIA: Tuple[str, ...] = tuple(VALIDATION_CRITERIA["problematic"])

SelectedChecks = List[Tuple[str, Check]]


def check_criteria(
    selected_criteria: Sequence[str], allowed_criteria: Sequence[str], name: str
) -> None:
    if isinstance(selected_criteria, str):
        raise ValueError(
            f"`{name}` must be a list of criteria names, not the single string '{selected_criteria}'"
        )
    if selected_criteria:
        for criterium in selected_criteria:
            if criterium not in allowed_criteria:
                raise ValueError(
                    f"The selected criterium {criterium} is not a valid argument for {name}"
                )
        logger.info(f"Criteria '{name}': {selected_criteria}")


def _select(criteria_type: str, selected_criteria: Sequence[str]) -> SelectedChecks:
    """Resolves criteria names to their checks once, keeping the caller's order."""
    return [
        (name, VALIDATION_CRITERIA[criteria_type][name]) for name in selected_criteria
    ]


def _apply_checks(
    selected: SelectedChecks,
    geometry: dict,
    shapely_geom: Optional[BaseGeometry],
    geometry_type: str,
) -> List[str]:
    """The names of the criteria that flag this single geometry."""
    flagged = []
    for name, check in selected:
        if geometry_type not in check.relevant:
            continue
        if check.needs_shapely:
            if shapely_geom is None:
                logger.info(
                    f"Skipping check '{name}', geometry could not be parsed by shapely."
                )
                continue
            if check.func(shapely_geom):
                flagged.append(name)
        elif check.func(geometry):
            flagged.append(name)
    return flagged


def process_validation(
    geometries: Sequence[Optional[dict]],
    criteria_invalid: Sequence[str],
    criteria_problematic: Sequence[str],
) -> Dict[str, Any]:
    selected_invalid = _select("invalid", criteria_invalid)
    selected_problematic = _select("problematic", criteria_problematic)
    # Only build the shapely geometry for types that a selected check actually needs it
    # for, so e.g. validating a FeatureCollection of Points does not parse every feature.
    types_needing_shapely = frozenset(
        geometry_type
        for _, check in selected_invalid + selected_problematic
        if check.needs_shapely
        for geometry_type in check.relevant
    )
    return _validate(
        geometries, selected_invalid, selected_problematic, types_needing_shapely
    )


def _validate(
    geometries: Sequence[Optional[dict]],
    selected_invalid: SelectedChecks,
    selected_problematic: SelectedChecks,
    types_needing_shapely: FrozenSet[str],
) -> Dict[str, Any]:
    results_invalid: Dict[str, List[Any]] = {}
    results_problematic: Dict[str, List[Any]] = {}
    skipped_validation: List[int] = []
    geometry_types: List[Optional[str]] = []

    for i, geometry in enumerate(geometries):
        if geometry is None:
            logger.info("Null geometry found in GeoJSON Feature, skipping.")
            skipped_validation.append(i)
            continue
        geometry_type = geometry.get("type", None)
        geometry_types.append(geometry_type)
        if geometry_type not in ALL_ACCEPTED_GEOMETRY_TYPES:
            logger.info(
                f"Geometry of type {geometry_type} currently not supported, skipping."
            )
            skipped_validation.append(i)  # TODO: Improve skipped_validation result
            continue

        # Handle Multi-Geometries & Geometrycollections:
        # Extract the single geometries in the multi-geometry/collection, run a separate validation on each.
        # Output results in this style: {3: [1,2]} (fourth geometry, the multigeometry is invalid,
        # because the second and third sub-geometries in it are invalid).
        if "Multi" in geometry_type or geometry_type == "GeometryCollection":
            single_geometries = extract_single_geometries(geometry, geometry_type)
            results_multi = _validate(
                single_geometries,
                selected_invalid,
                selected_problematic,
                types_needing_shapely,
            )
            # Take all invalid criteria from the e.g. Polygons inside the Multipolygon and indicate them
            # as the positional index of the MultiPolygon.
            for criterium in results_multi["invalid"]:
                results_invalid.setdefault(criterium, []).append(
                    {i: results_multi["invalid"][criterium]}
                )
            for criterium in results_multi["problematic"]:
                results_problematic.setdefault(criterium, []).append(
                    {i: results_multi["problematic"][criterium]}
                )
            continue

        # Handle Single-Geometries
        shapely_geom = (
            to_shapely_or_none(geometry)
            if geometry_type in types_needing_shapely
            else None
        )
        for criterium in _apply_checks(
            selected_invalid, geometry, shapely_geom, geometry_type
        ):
            results_invalid.setdefault(criterium, []).append(i)
        for criterium in _apply_checks(
            selected_problematic, geometry, shapely_geom, geometry_type
        ):
            results_problematic.setdefault(criterium, []).append(i)

    # TODO: Results format better: feature1: flaws, feature4: flaws, feature9: flaws?
    results = {
        "invalid": results_invalid,
        "problematic": results_problematic,
        "count_geometry_types": dict(Counter(geometry_types)),
        "skipped_validation": skipped_validation,
    }

    return results
