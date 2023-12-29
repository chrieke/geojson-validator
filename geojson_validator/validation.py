import sys
import json

from loguru import logger
import jsonschema


logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")


ALL_ACCEPTED_GEOMETRY_TYPES = POI, MPOI, LS, MLS, POL, MPOL = [
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
]

VALIDATION_CRITERIA = {
    "invalid": {
        "unclosed": {"relevant": [POL, MPOL], "input": "json_geometry"},
        "duplicate_nodes": {
            "relevant": [LS, MLS, POL, MPOL],
            "input": "json_geometry",
        },
        "less_three_unique_nodes": {
            "relevant": [POL, MPOL],
            "input": "json_geometry",
        },
        "exterior_not_ccw": {
            "relevant": [POL, MPOL],
            "input": "shapely_geom",
        },
        "interior_not_cw": {
            "relevant": [POL, MPOL],
            "input": "shapely_geom",
        },
        "inner_and_exterior_ring_intersect": {
            "relevant": [POL, MPOL],
            "input": "shapely_geom",
        },
        "outside_lat_lon_boundaries": {
            "relevant": ALL_ACCEPTED_GEOMETRY_TYPES,
            "input": "json_geometry",
        },
        "crs_defined": {
            "relevant": ["FeatureCollection"],
            "input": "json_geometry",
        },
        # "zero-length": {"relevant": ["LineString"], "input": "json_geometry"},
    },
    "problematic": {
        "holes": {"relevant": [POL, MPOL], "input": "shapely_geom"},
        "self_intersection": {
            "relevant": [POL, MPOL],
            "input": "shapely_geom",
        },
        "excessive_coordinate_precision": {
            "relevant": ALL_ACCEPTED_GEOMETRY_TYPES,
            "input": "json_geometry",
        },
        "more_than_2d_coordinates": {
            "relevant": ALL_ACCEPTED_GEOMETRY_TYPES,
            "input": "json_geometry",
        },
        "crosses_antimeridian": {
            "relevant": [LS, MLS, POL, MPOL],
            "input": "json_geometry",
        },
        # "wrong_bbox_order: {}"
    },
}


def validate_geojson_schema(geojson_data):
    with open("geojson_validator/data/geojson-schema.json", "r") as f:
        geojson_schema = json.load(f)  # "http://json.schemastore.org/geojson"

    # Validate the GeoJSON
    try:
        jsonschema.validate(instance=geojson_data, schema=geojson_schema)
        print("GeoJSON is valid!")
    except jsonschema.exceptions.ValidationError as ve:
        print("GeoJSON is not valid!")
        print(ve)


def check_criteria(selected_criteria, criteria_type):
    if selected_criteria:
        for criterium in selected_criteria:
            if criterium not in VALIDATION_CRITERIA[criteria_type]:
                raise ValueError(
                    f"The selected criterium {criterium} is not a valid argument for {criteria_type}"
                )
        logger.info(f"Validation criteria '{criteria_type}': {selected_criteria}")
