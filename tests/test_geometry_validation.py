import pytest

from geojson_validator import geometry_validation


def test_check_criteria_invalid():
    with pytest.raises(ValueError):
        geometry_validation.check_criteria(
            ["non_existent_criteria"],
            geometry_validation.INVALID_CRITERIA,
            "invalid",
        )


def test_check_criteria_valid():
    try:
        geometry_validation.check_criteria(
            ["unclosed", "less_three_unique_nodes"],
            geometry_validation.INVALID_CRITERIA,
            "invalid",
        )
        geometry_validation.check_criteria(
            ["holes"],
            geometry_validation.PROBLEMATIC_CRITERIA,
            "problematic",
        )
    except ValueError:
        pytest.fail("Unexpected ValueError for valid criteria")


def test_check_criteria_single_string_raises():
    with pytest.raises(ValueError, match="must be a list of criteria names"):
        geometry_validation.check_criteria(
            "unclosed", geometry_validation.INVALID_CRITERIA, "invalid"
        )


@pytest.mark.parametrize(
    "geometry",
    [
        {"type": "Point", "coordinates": [1]},  # position with a single value
        {"type": "Point", "coordinates": ["1", "2"]},  # non-numeric coordinate
        {"type": "LineString", "coordinates": [[1, 2], [3, None]]},  # null coordinate
        {"type": "Polygon", "coordinates": [[1, 2]]},  # not nested deep enough
        {"type": "Polygon"},  # missing coordinates
        {"type": "MultiPolygon"},  # missing coordinates, multi-geometry path
        "a string, not an object",
        True,
    ],
)
def test_process_validation_skips_structurally_broken_geometry(geometry):
    # These are reported properly by validate_structure; validate_geometries must skip
    # them rather than raising IndexError/TypeError/KeyError/AttributeError.
    results = geometry_validation.process_validation(
        [geometry],
        geometry_validation.INVALID_CRITERIA,
        geometry_validation.PROBLEMATIC_CRITERIA,
    )
    assert results["skipped_validation"] == [0]
    assert not results["invalid"]
    assert not results["problematic"]


def test_process_validation_skips_only_the_broken_geometry():
    geometries = [
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
        {"type": "Point", "coordinates": [1]},  # broken
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1]]]},
    ]
    results = geometry_validation.process_validation(
        geometries,
        geometry_validation.INVALID_CRITERIA,
        geometry_validation.PROBLEMATIC_CRITERIA,
    )
    assert results["skipped_validation"] == [1]
    assert results["invalid"]["unclosed"] == [2]  # the third geometry is still checked


@pytest.mark.parametrize(
    "geometry",
    [
        # Rings one level too shallow, so the sub-polygon itself is not checkable.
        {"type": "MultiPolygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
        {"type": "MultiPoint", "coordinates": [[1]]},  # position with a single value
        {"type": "GeometryCollection", "geometries": [False]},  # not an object
        {"type": "GeometryCollection", "geometries": [None]},  # null sub-geometry
    ],
)
def test_process_validation_skips_multi_geometry_with_broken_subgeometry(geometry):
    # The skip of a sub-geometry must reach the result, otherwise a broken
    # multi-geometry is indistinguishable from a valid one.
    results = geometry_validation.process_validation(
        [geometry],
        geometry_validation.INVALID_CRITERIA,
        geometry_validation.PROBLEMATIC_CRITERIA,
    )
    assert results["skipped_validation"] == [0]
    assert not results["invalid"]
    assert not results["problematic"]


def test_process_validation_partly_broken_multi_geometry_is_skipped_and_flagged():
    # A multi-geometry can be both: partly checked and flagged, partly not checkable.
    geometries = [
        {
            "type": "MultiPolygon",
            "coordinates": [
                [[0, 0], [1, 0], [1, 1], [0, 0]],  # broken, rings too shallow
                [[[0, 0], [1, 0], [1, 1], [0, 1]]],  # checkable, and unclosed
            ],
        }
    ]
    results = geometry_validation.process_validation(
        geometries,
        geometry_validation.INVALID_CRITERIA,
        geometry_validation.PROBLEMATIC_CRITERIA,
    )
    assert results["skipped_validation"] == [0]
    assert results["invalid"]["unclosed"] == [{0: [1]}]


def test_process_validation_valid_polygon_without_criteria():
    geometries = [
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [1, 0], [0, 0]]]}
    ]
    results = geometry_validation.process_validation(geometries, [], [])
    assert not results["invalid"]
    assert not results["problematic"]


def test_process_validation_invalid_geometry():
    # unclosed
    geometries = [
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [1, 0]]]}
    ]  # Missing closing point
    invalid_criteria = ["unclosed"]
    results = geometry_validation.process_validation(geometries, invalid_criteria, [])
    assert "unclosed" in results["invalid"]


def test_process_validation_no_error_no_type():
    # Test handling of geometry missing the 'type' field
    geometries = [{"coordinates": [[[0, 0], [1, 1], [1, 0], [0, 0]]]}]  # No type field
    assert geometry_validation.process_validation(geometries, [], [])


def test_process_validation_multipolygon():
    # Second geometry in Multipolygon and third geometry is unclosed
    geometries = [
        {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0, 0], [2, 2], [2, 0], [0, 0]]],
                [[[0, 0], [2, 2], [2, 0], [0, 1]]],  # invalid
                [[[0, 0], [1, 1], [1, 0]]],  # invalid
            ],
        },
    ]
    invalid_criteria = ["unclosed"]
    results = geometry_validation.process_validation(geometries, invalid_criteria, [])
    assert results["invalid"]["unclosed"] == [{0: [1, 2]}]
    assert results["count_geometry_types"] == {"MultiPolygon": 1}


def test_process_validation_geometrycollection():
    geometries = [
        {
            "type": "GeometryCollection",
            "geometries": [
                {"coordinates": [11.691336, 51.804026], "type": "Point"},
                {
                    "coordinates": [[[0, 0], [1, 1], [1, 0]]],
                    "type": "Polygon",
                },  # invalid
                {"coordinates": [[[0, 0], [2, 2], [2, 0], [0, 0]]], "type": "Polygon"},
            ],
        }
    ]
    invalid_criteria = ["unclosed"]
    results = geometry_validation.process_validation(geometries, invalid_criteria, [])
    assert results["invalid"]["unclosed"] == [{0: [1]}]
    assert results["count_geometry_types"] == {"GeometryCollection": 1}


def test_process_validation_multipolygon_in_geometrycollection():
    # Second geometry in Multipolygon and third geometry is unclosed
    geometries = [
        {
            "type": "GeometryCollection",
            "geometries": [
                {"coordinates": [11.691336, 51.804026], "type": "Point"},
                {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [[[0, 0], [2, 2], [2, 0], [0, 0]]],
                        [[[0, 0], [2, 2], [2, 0], [0, 1]]],  # invalid
                        [[[0, 0], [1, 1], [1, 0]]],  # invalid
                    ],
                },
            ],
        }
    ]
    invalid_criteria = ["unclosed"]
    results = geometry_validation.process_validation(geometries, invalid_criteria, [])
    assert results["invalid"]["unclosed"] == [{0: [{1: [1, 2]}]}]
    assert results["count_geometry_types"] == {"GeometryCollection": 1}


def test_process_validation_mixed_dimension_does_not_crash():
    # Mixed 2D/3D coordinates make shapely raise on construction; the raw-JSON checks
    # (e.g. 3d_coordinates) must still run instead of crashing the whole validation.
    geometries = [
        {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1, 5], [0, 1], [0, 0]]],
        }
    ]
    results = geometry_validation.process_validation(geometries, [], ["3d_coordinates"])
    assert "3d_coordinates" in results["problematic"]


def test_process_validation_multiple_types():
    # Second geometry in Multipolygon and third geometry is unclosed
    geometries = [
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [1, 0], [0, 0]]]},
        {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0, 0], [2, 2], [2, 0], [0, 0]]],
                [[[0, 0], [2, 2], [2, 0], [0, 1]]],  # invalid
                [[[0, 0], [1, 1], [1, 0]]],  # invalid
            ],
        },
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [1, 0]]]},
    ]
    invalid_criteria = ["unclosed"]
    results = geometry_validation.process_validation(geometries, invalid_criteria, [])
    assert results["invalid"]["unclosed"] == [{1: [1, 2]}, 2]
    assert results["count_geometry_types"] == {"Polygon": 2, "MultiPolygon": 1}
