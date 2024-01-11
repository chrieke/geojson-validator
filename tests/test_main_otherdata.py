import pytest

from .fixtures import read_geojson

from .context import main


@pytest.mark.skip(reason="1mb file")
def test_validate_countries_dataset():
    fc = read_geojson("./tests/data/countries.geojson")
    result = main.validate_geometries(fc)
    assert len(result["invalid"]) == 0
    assert len(result["problematic"]["self_intersection"]) == 1
    assert result["problematic"]["crosses_antimeridian"] == [
        {12: [7]},
        {59: [1]},
        {142: [3, 9]},
    ]
    assert len(result["problematic"]["excessive_coordinate_precision"]) == 51
    assert result["problematic"]["holes"] == [181]
    assert len(result["problematic"]) == 4
    assert result["count_geometry_types"] == {"Polygon": 188, "MultiPolygon": 46}


@pytest.mark.skip(reason="Takes 10sec, 20mb file")
def test_validate_buildings_dataset():
    fc = read_geojson("./tests/data/buildings.json")
    result = main.validate_geometries(fc)
    assert len(result["problematic"]["excessive_coordinate_precision"]) == 66510
    assert result["count_geometry_types"]["Polygon"] == 66510
