from shapely.geometry import shape

from geojson_validator import checks_invalid
from .helpers import DATA, read_geojson


def test_check_unclosed(valid_geometry):
    geometry = read_geojson(
        DATA / "invalid_geometries/invalid_unclosed.geojson",
        geometries=True,
    )
    assert checks_invalid.check_unclosed(geometry)
    assert not checks_invalid.check_unclosed(valid_geometry)


def test_check_unclosed_interior_ring():
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
            [[1, 1], [2, 1], [2, 2], [1, 2]],  # unclosed hole
        ],
    }
    assert checks_invalid.check_unclosed(geometry)


def test_check_unclosed_empty_ring():
    geometry = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], []],
    }
    assert not checks_invalid.check_unclosed(geometry)


def test_less_three_unique_nodes(valid_geometry):
    geometry = read_geojson(
        DATA / "invalid_geometries/invalid_less_three_unique_nodes.geojson",
        geometries=True,
    )
    assert checks_invalid.check_less_three_unique_nodes(geometry)
    assert not checks_invalid.check_less_three_unique_nodes(valid_geometry)


def test_check_exterior_not_ccw(valid_geometry):
    geometry = read_geojson(
        DATA / "invalid_geometries/invalid_exterior_not_ccw.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_exterior_not_ccw(geom)
    assert not checks_invalid.check_exterior_not_ccw(shape(valid_geometry))


def test_check_interior_not_cw(valid_geometry):
    geometry = read_geojson(
        DATA / "invalid_geometries/invalid_interior_not_cw.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    assert checks_invalid.check_interior_not_cw(geom)
    assert not checks_invalid.check_interior_not_cw(shape(valid_geometry))
