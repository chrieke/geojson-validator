from .context import schema_validation


def test_schema_validation():
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"coordinates": [81.2072495864164, 13.0187039189613]},
                "properties": {"assetStatus": "FULL", "id": 1747, "item": "53 Trailer"},
            },
            {
                "type": "Feature",
                "geometry": None,
                "properties": {
                    "assetStatus": "EMPTY",
                    "id": 1746,
                    "item": "53 Trailer",
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "coordinates": [80.2067574402883, 13.0191983952581],
                    "type": "Point",
                },
                "properties": {
                    "assetStatus": "LOADED",
                    "id": 1745,
                    "item": "53 Trailer",
                },
            },
        ],
    }
    errors = schema_validation.GeoJsonLint().lint(geojson_data)
    assert errors
    assert errors == [
        {"message": "Missing 'type'", "line": 4},
        {
            "message": '"geometry" member should be an object, but is a NoneType instead',
            "line": 18,
        },
    ]
