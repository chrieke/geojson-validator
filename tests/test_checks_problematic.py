from shapely.geometry import shape

from geojson_validator import checks_problematic
from .helpers import DATA, read_geojson


def test_check_holes():
    geometry = read_geojson(
        DATA / "problematic_geometries/problematic_holes.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    problematic = checks_problematic.check_holes(geom)
    assert problematic


def test_check_self_intersection():
    geometry = read_geojson(
        DATA / "problematic_geometries/problematic_self_intersection_small.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    problematic = checks_problematic.check_self_intersection(geom)
    assert problematic


def test_check_inner_and_exterior_ring_intersect(valid_geometry):
    geometry = read_geojson(
        DATA / "invalid_geometries/invalid_inner_and_exterior_ring_intersect.geojson",
        geometries=True,
    )
    assert checks_problematic.check_inner_and_exterior_ring_intersect(shape(geometry))
    assert not checks_problematic.check_inner_and_exterior_ring_intersect(
        shape(valid_geometry)
    )


def test_check_inner_and_exterior_ring_touching_at_single_point_allowed():
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
            [[0, 5], [2, 4], [2, 6], [0, 5]],  # touches the exterior only at (0, 5)
        ],
    }
    assert not checks_problematic.check_inner_and_exterior_ring_intersect(
        shape(geometry)
    )


def test_check_inner_ring_outside_exterior_touching_at_single_point():
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
            [[10, 5], [12, 6], [12, 4], [10, 5]],  # hole lies outside the exterior
        ],
    }
    assert checks_problematic.check_inner_and_exterior_ring_intersect(shape(geometry))


def test_check_duplicate_nodes(valid_geometry):
    geometry = read_geojson(
        DATA / "problematic_geometries/problematic_duplicate_nodes.geojson",
        geometries=True,
    )
    assert checks_problematic.check_duplicate_nodes(geometry)
    assert not checks_problematic.check_duplicate_nodes(valid_geometry)


def test_check_duplicate_nodes_empty_ring():
    geometry = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], []],
    }
    assert not checks_problematic.check_duplicate_nodes(geometry)


def test_check_excessive_coordinate_precision():
    geometry = read_geojson(
        DATA
        / "problematic_geometries/problematic_excessive_coordinate_precision.geojson",
        geometries=True,
    )
    assert checks_problematic.check_excessive_coordinate_precision(geometry)


def test_check_excessive_coordinate_precision_no_after_comma_succeds():
    geometry_no_after_comma = {
        "coordinates": [[[-77, 26.0], [-77.17255, 25], [-77, 26]]],
        "type": "Polygon",
    }
    assert not checks_problematic.check_excessive_coordinate_precision(
        geometry_no_after_comma
    )


def test_check_excessive_coordinate_precision_on_later_vertex():
    # Excessive precision only on the 3rd vertex; must still be detected (not just first 2).
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [[0.0, 0.0], [1.0, 0.0], [1.1234567, 1.0], [0.0, 1.0], [0.0, 0.0]]
        ],
    }
    assert checks_problematic.check_excessive_coordinate_precision(geometry)


def test_check_excessive_coordinate_precision_interior_ring_and_exponent():
    # Excessive precision only in the hole; must still be detected (not just exterior ring).
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
            [[1, 1], [2, 1], [2, 2.1234567], [1, 2], [1, 1]],
        ],
    }
    assert checks_problematic.check_excessive_coordinate_precision(geometry)
    # Exponent notation (1e-07 = 0.0000001, 7 decimal places)
    assert checks_problematic.check_excessive_coordinate_precision(
        {"type": "Point", "coordinates": [1e-07, 0.0]}
    )


def test_check_excessive_vertices():
    geometry = read_geojson(
        DATA / "problematic_geometries/problematic_excessive_vertices.geojson",
        geometries=True,
    )
    assert checks_problematic.check_excessive_vertices(geometry)


def test_check_3d_coordinates():
    geometry = read_geojson(
        DATA / "problematic_geometries/problematic_3d_coordinates.geojson",
        geometries=True,
    )
    assert checks_problematic.check_3d_coordinates(geometry)


def test_check_3d_coordinates_on_later_vertex():
    # 3D coordinate only on the 3rd vertex; must still be detected (not just first 2).
    geometry = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [1, 0], [1, 1, 5], [0, 1], [0, 0]]],
    }
    assert checks_problematic.check_3d_coordinates(geometry)


def test_check_outside_lat_lon_boundaries(valid_geometry):
    geometry = read_geojson(
        DATA / "problematic_geometries/problematic_outside_lat_lon_boundaries.geojson",
        geometries=True,
    )
    assert checks_problematic.check_outside_lat_lon_boundaries(geometry)
    assert not checks_problematic.check_outside_lat_lon_boundaries(valid_geometry)


def test_check_crosses_antimeridian():
    geometry = read_geojson(
        DATA / "problematic_geometries/problematic_crosses_antimeridian.geojson",
        geometries=True,
    )
    assert checks_problematic.check_crosses_antimeridian(geometry)
