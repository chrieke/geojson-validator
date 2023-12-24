import json
from shapely.geometry import shape

from .context import checks_invalid


def test_check_unclosed():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_unclosed_polygon.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geometry = gj["features"][0]["geometry"]

    invalid = checks_invalid.check_unclosed(geometry)
    assert invalid


def test_check_duplicate_nodes():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geometry = gj["features"][0]["geometry"]
    invalid = checks_invalid.check_duplicate_nodes(geometry)
    assert invalid


def test_less_three_unique_nodes():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_has_less_than_three_unique_nodes.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geometry = gj["features"][0]["geometry"]
    invalid = checks_invalid.check_less_three_unique_nodes(geometry)
    assert invalid


def test_check_exterior_not_ccw():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_exterior_ring_not_counterclockwise_winding_order.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geom = shape(gj["features"][0]["geometry"])
    invalid = checks_invalid.check_exterior_not_ccw(geom)
    assert invalid


def test_check_interior_not_cw():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_interior_ring_not_clockwise_winding_order.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geom = shape(gj["features"][0]["geometry"])
    invalid = checks_invalid.check_interior_not_cw(geom)
    assert invalid


def test_check_inner_and_exterior_ring_intersect():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_inner_and_exterior_ring_cross.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    geom = shape(gj["features"][0]["geometry"])
    invalid = checks_invalid.check_inner_and_exterior_ring_intersect(geom)
    assert invalid


def test_check_defined_crs():
    geojson_fp = "./tests/examples_geojson/invalid/crs_defined.geojson"  # from geojson-invalid-geometry repo
    with open(geojson_fp) as f:
        gj = json.load(f)
    invalid = checks_invalid.check_crs_defined(gj)
    assert invalid
