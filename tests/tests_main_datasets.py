import pytest

from .fixtures_utils import read_geojson
from .context import main


# @pytest.mark.skip(reason="1mb file")
def test_validate_countries_dataset():
    fc = read_geojson("./tests/examples_geojson/countries.geojson")
    result = main.validate(fc)
    assert len(result["invalid"]) == 0
    assert len(result["problematic"]["self_intersection"]) == 1
    assert result["problematic"]["crosses_antimeridian"] == [12, 59, 142]
    assert len(result["problematic"]["excessive_coordinate_precision"]) == 51
    assert result["problematic"]["holes"] == [181]
    assert len(result["problematic"]) == 4
    assert result["count_geometry_types"] == {"Polygon": 188, "MultiPolygon": 46}


@pytest.mark.skip(reason="Takes 10sec, 20mb file")
def test_validate_buildings_dataset():
    fc = read_geojson("./tests/examples_geojson/buildings.json")
    result = main.validate(fc)
    assert len(result["problematic"]["excessive_coordinate_precision"]) == 66510
    assert result["count_geometry_types"]["Polygon"] == 66510
