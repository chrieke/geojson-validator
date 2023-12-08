import geopandas as gpd

from .context import (
    check_holes,
    check_self_intersection,
    check_excessive_coordinate_precision,
    check_more_than_2d_coordinates,
    check_crosses_antimeridian,
)


def test_check_holes():
    geojson_fp = "./tests/examples_geojson/valid_but_problematic/polygon_has_holes.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_holes(df.geometry[0])  # TODO: Check multiple geoms?
    assert result


def test_check_self_intersection():
    geojson_fp = "./tests/examples_geojson/valid_but_problematic/polygon_selfintersection_small.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_self_intersection(df.geometry[0])
    assert result


def test_check_excessive_coordinate_precision():
    geojson_fp = "./tests/examples_geojson/valid_but_problematic/excessive_coordinate_precision.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_excessive_coordinate_precision(df.geometry[0])
    assert result


def test_check_more_than_2d_coordinates():
    geojson_fp = "./tests/examples_geojson/valid_but_problematic/3d_coordinates.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_more_than_2d_coordinates(df.geometry[0])
    assert result


def test_check_crosses_antimeridian():
    geojson_fp = "./tests/examples_geojson/valid_but_problematic/geometry_crosses_the_antimeridian.geojson"  # from geojson-invalid-geometry repo
    df = gpd.read_file(geojson_fp)
    result = check_crosses_antimeridian(df.geometry[0])
    assert result
