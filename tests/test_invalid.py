import geojson

from .context import (
    check_unclosed,
    check_duplicate_nodes,
    check_less_three_unique_nodes,
    check_exterior_not_ccw,
    check_interior_not_cw,
    check_inner_and_exterior_ring_intersect,
    check_crs_defined,
)


def test_check_unclosed():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_unclosed_polygon.geojson"  # from geojson-invalid-geometry repo


    with open(geojson_fp) as f:
        gj = geojson.load(f)
    features = gj['features'][0]

    result = check_unclosed(geometry)
    assert result


def test_check_duplicate_nodes():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_has_duplicate_nodes.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_duplicate_nodes(df.geometry[0])
    assert result


def test_less_three_unique_nodes():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_has_less_than_three_unique_nodes.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_less_three_unique_nodes(df.geometry[0])
    assert result


def test_check_exterior_not_ccw():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_exterior_ring_not_counterclockwise_winding_order.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_exterior_not_ccw(df.geometry[0])
    assert result


def test_check_interior_not_cw():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_interior_ring_not_clockwise_winding_order.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_interior_not_cw(df.geometry[0])
    assert result


def test_check_inner_and_exterior_ring_intersect():
    geojson_fp = "./tests/examples_geojson/invalid/polygon_inner_and_exterior_ring_cross.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_inner_and_exterior_ring_intersect(df.geometry[0])
    assert result


def test_check_defined_crs():
    geojson_fp = "./tests/examples_geojson/invalid/crs_defined.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_crs_defined(df.geometry[0])
    assert result
