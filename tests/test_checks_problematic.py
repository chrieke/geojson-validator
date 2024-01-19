from shapely.geometry import shape
import pytest

from .context import checks_problematic
from .fixtures import read_geojson


@pytest.fixture(scope="session")
def valid_geometry():
    geojson_fp = "./tests/data/valid/valid_featurecollection.geojson"
    return read_geojson(geojson_fp, geometries=True)


def test_check_holes():
    geometry = read_geojson(
        "./tests/data/problematic_geometries/problematic_holes.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    problematic = checks_problematic.check_holes(geom)
    assert problematic


def test_check_self_intersection():
    geometry = read_geojson(
        "./tests/data/problematic_geometries/problematic_self_intersection_small.geojson",
        geometries=True,
    )
    geom = shape(geometry)
    problematic = checks_problematic.check_self_intersection(geom)
    assert problematic


def test_check_duplicate_nodes(valid_geometry):
    geometry = read_geojson(
        "./tests/data/problematic_geometries/problematic_duplicate_nodes.geojson",
        geometries=True,
    )
    assert checks_problematic.check_duplicate_nodes(geometry)
    assert not checks_problematic.check_duplicate_nodes(valid_geometry)


def test_check_excessive_coordinate_precision():
    geometry = read_geojson(
        "./tests/data/problematic_geometries/problematic_excessive_coordinate_precision.geojson",
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


def test_check_excessive_vertices():
    geometry = read_geojson(
        "./tests/data/problematic_geometries/problematic_excessive_vertices.geojson",
        geometries=True,
    )
    assert checks_problematic.check_excessive_vertices(geometry)


def test_check_3d_coordinates():
    geometry = read_geojson(
        "./tests/data/problematic_geometries/problematic_3d_coordinates.geojson",
        geometries=True,
    )
    assert checks_problematic.check_3d_coordinates(geometry)


def test_check_outside_lat_lon_boundaries(valid_geometry):
    geometry = read_geojson(
        "./tests/data/problematic_geometries/problematic_outside_lat_lon_boundaries.geojson",
        geometries=True,
    )
    assert checks_problematic.check_outside_lat_lon_boundaries(geometry)
    assert not checks_problematic.check_outside_lat_lon_boundaries(valid_geometry)


def test_check_crosses_antimeridian():
    geometry = read_geojson(
        "./tests/data/problematic_geometries/problematic_crosses_antimeridian.geojson",
        geometries=True,
    )
    assert checks_problematic.check_crosses_antimeridian(geometry)
