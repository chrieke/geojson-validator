import json
from shapely.geometry import shape

from .context import checks_invalid


def read_geojson_geometry(file_name: str):
    geojson_fp = f"./tests/examples_geojson/invalid/{file_name}"
    with open(geojson_fp) as f:
        gj = json.load(f)
    return gj["features"][0]["geometry"]


def test_check_unclosed():
    geometry = read_geojson_geometry("polygon_unclosed_polygon.geojson")
    invalid = checks_invalid.check_unclosed(geometry)
    assert invalid


def test_check_duplicate_nodes():
    geometry = read_geojson_geometry("polygon_has_duplicate_nodes.geojson")
    invalid = checks_invalid.check_duplicate_nodes(geometry)
    assert invalid


def test_less_three_unique_nodes():
    geometry = read_geojson_geometry("polygon_has_less_than_three_unique_nodes.geojson")
    invalid = checks_invalid.check_less_three_unique_nodes(geometry)
    assert invalid


def test_check_exterior_not_ccw():
    geometry = read_geojson_geometry(
        "polygon_exterior_ring_not_counterclockwise_winding_order.geojson"
    )
    geom = shape(geometry)
    invalid = checks_invalid.check_exterior_not_ccw(geom)
    assert invalid


def test_check_interior_not_cw():
    geometry = read_geojson_geometry(
        "polygon_interior_ring_not_clockwise_winding_order.geojson"
    )
    geom = shape(geometry)
    invalid = checks_invalid.check_interior_not_cw(geom)
    assert invalid


def test_check_inner_and_exterior_ring_intersect():
    geometry = read_geojson_geometry("polygon_inner_and_exterior_ring_cross.geojson")
    geom = shape(geometry)
    invalid = checks_invalid.check_inner_and_exterior_ring_intersect(geom)
    assert invalid


def test_check_defined_crs():
    geojson_fp = "./tests/examples_geojson/invalid/crs_defined.geojson"
    with open(geojson_fp) as f:
        gj = json.load(f)
    invalid = checks_invalid.check_crs_defined(gj)
    assert invalid
