import pytest

from .context import geometry_validation


def test_check_criteria_invalid():
    with pytest.raises(ValueError):
        geometry_validation.check_criteria(
            ["non_existent_criteria"],
            geometry_validation.VALIDATION_CRITERIA["invalid"],
            "invalid",
        )


def test_check_criteria_valid():
    try:
        geometry_validation.check_criteria(
            ["unclosed", "less_three_unique_nodes"],
            geometry_validation.VALIDATION_CRITERIA["invalid"],
            "invalid",
        )
        geometry_validation.check_criteria(
            ["holes"],
            geometry_validation.VALIDATION_CRITERIA["problematic"],
            "problematic",
        )
    except ValueError:
        pytest.fail("Unexpected ValueError for valid criteria")


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
