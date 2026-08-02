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
        if not isinstance(geometry, dict):
            logger.info(
                f"Geometry must be an object, but is a {type(geometry).__name__}, skipping."
            )
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

        # The value appended per flagged criterium: the geometry's own index, or
        # {index: [sub-indices]} for a multi-geometry.
        flagged_invalid: Dict[str, Any]
        flagged_problematic: Dict[str, Any]
        try:
            if "Multi" in geometry_type or geometry_type == "GeometryCollection":
                # Validate each single geometry inside the multi-geometry/collection
                # separately, and report the results under the index of the
                # multi-geometry: {3: [1, 2]} is "the fourth geometry is invalid,
                # because its second and third sub-geometries are".
                results_multi = _validate(
                    extract_single_geometries(geometry, geometry_type),
                    selected_invalid,
                    selected_problematic,
                    types_needing_shapely,
                )
                # A sub-geometry that could not be checked must not pass silently, or a
                # broken multi-geometry is indistinguishable from a valid one.
                if results_multi["skipped_validation"]:
                    skipped_validation.append(i)
                flagged_invalid = {
                    criterium: {i: indices}
                    for criterium, indices in results_multi["invalid"].items()
                }
                flagged_problematic = {
                    criterium: {i: indices}
                    for criterium, indices in results_multi["problematic"].items()
                }
            else:
                shapely_geom = (
                    to_shapely_or_none(geometry)
                    if geometry_type in types_needing_shapely
                    else None
                )
                flagged_invalid = {
                    criterium: i
                    for criterium in _apply_checks(
                        selected_invalid, geometry, shapely_geom, geometry_type
                    )
                }
                flagged_problematic = {
                    criterium: i
                    for criterium in _apply_checks(
                        selected_problematic, geometry, shapely_geom, geometry_type
                    )
                }
        except (TypeError, IndexError, KeyError) as error:
            # A structurally broken geometry, e.g. a position with a single or a
            # non-numeric value, or missing coordinates. validate_structure reports what
            # is actually wrong; here it is only skipped instead of raising.
            logger.info(f"Geometry could not be validated ({error!r}), skipping.")
            skipped_validation.append(i)
            continue

        for criterium, flagged in flagged_invalid.items():
            results_invalid.setdefault(criterium, []).append(flagged)
        for criterium, flagged in flagged_problematic.items():
            results_problematic.setdefault(criterium, []).append(flagged)

    # TODO: Results format better: feature1: flaws, feature4: flaws, feature9: flaws?
    results = {
        "invalid": results_invalid,
        "problematic": results_problematic,
        "count_geometry_types": dict(Counter(geometry_types)),
        "skipped_validation": skipped_validation,
    }

    return results
