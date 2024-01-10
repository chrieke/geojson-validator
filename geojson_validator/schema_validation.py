import json
from json_source_map import calculate


class GeoJsonLint:
    """
    Validates if the GeoJSON conforms to the geojson json schema rules 2020-12
    (https://json-schema.org/draft/2020-12/release-notes)

    In comparison to simple comparison to the schema via jsonschema library, this adds
    error line positions and clearer handling.

    Inspired by https://github.com/mapbox/geojsonhint (paused Javascript library)
    Focuses on structural GEOJSON schema validation, not GeoJSON specification geometry rules.
    """

    GEOJSON_TYPES = [
        "FeatureCollection",
        "Feature",
        "Point",
        "LineString",
        "Polygon",
        "MultiPoint",
        "MultiLineString",
        "MultiPolygon",
        "GeometryCollection",
    ]

    def __init__(self, check_crs=False):
        self.errors = []
        self.check_crs = check_crs
        self.line_map = None

    def lint(self, geojson_data):
        if not isinstance(geojson_data, (dict, list)):
            self._add_error("The root of a GeoJSON object must be an object.", 0)
            return self.errors

        formatted_geojson_string = json.dumps(
            geojson_data, sort_keys=True, indent=2, separators=(",", ": ")
        )
        self.line_map = calculate(formatted_geojson_string)

        self._validate_geojson_root(geojson_data)

        for err in self.errors:
            if "line" in err and err["line"] is None:
                del err["line"]

        return self.errors

    def _validate_geojson_root(self, obj):
        root_path = ""
        if self._is_invalid_type(obj, root_path):
            return

        obj_type = obj.get("type")
        if obj_type == "FeatureCollection":
            self._validate_feature_collection(obj, root_path)
        elif obj_type == "Feature":
            self._validate_feature(obj, root_path)
        elif obj_type in self.GEOJSON_TYPES:
            self._validate_geometry(obj, root_path)

    def _validate_feature_collection(self, feature_collection, path):
        self._is_invalid_type(feature_collection, path)

        if self.check_crs and "crs" in feature_collection:
            self._add_error(
                "Specification of crs member (coordinate reference system) is no longer used in the "
                "GeoJSON specification, should be removed.",
                self._get_line_number(f"{path}/crs"),
            )

        if not self._is_invalid_property(feature_collection, "features", "array", path):
            for idx, feature in enumerate(feature_collection["features"]):
                if not isinstance(feature, dict):
                    self._add_error(
                        f"Every feature must be an object. feature nr {idx} is not",
                        self._get_line_number(f"{path}/features/{idx}"),
                    )
                else:
                    self._validate_feature(feature, f"{path}/features/{idx}")

    def _validate_feature(self, feature, path):
        self._is_invalid_type(feature, path)
        if "id" in feature and not isinstance(feature["id"], (str, int)):
            self._add_error(
                'Feature "id" member must have a string or number value',
                self._get_line_number(f"{path}/id"),
            )
        self._is_invalid_property(feature, "properties", "object", f"{path}/properties")
        self._is_invalid_property(feature, "geometry", "object", f"{path}/geometry")
        geom = feature.get("geometry")
        if geom:
            self._validate_geometry(geom, f"{path}/geometry")

    def _validate_geometry(self, obj, path):
        if self._is_invalid_type(obj, path):
            return

        obj_type = obj.get("type")
        if obj_type == "GeometryCollection":
            if not self._is_invalid_property(obj, "geometries", "array", path):
                for idx, geom in enumerate(obj["geometries"]):
                    self._validate_geometry(geom, f"{path}/geometries/{idx}")
        elif not self._is_invalid_property(obj, "coordinates", "array", path):
            if obj_type in ["Point"]:
                self._validate_position(obj["coordinates"], f"{path}/coordinates")
            elif obj_type in ["LineString", "MultiPoint"]:
                self._validate_position_array(
                    obj["coordinates"], 1, f"{path}/coordinates"
                )
            elif obj_type in ["Polygon", "MultiLineString"]:
                self._validate_position_array(
                    obj["coordinates"], 2, f"{path}/coordinates"
                )
            elif obj_type in ["MultiPolygon"]:
                self._validate_position_array(
                    obj["coordinates"], 3, f"{path}/coordinates"
                )

    def _validate_position(self, coords, path):
        if not isinstance(coords, list):
            return self._add_error(
                "Position should be an array",
                self._get_line_number(path),
            )
        if len(coords) < 2 or len(coords) > 3:
            return self._add_error(
                "Position must have exactly 2 or 3 values",
                self._get_line_number(path),
            )
        if not all(isinstance(coord, (int, float)) for coord in coords):
            return self._add_error(
                "Each element in a position must be a number",
                self._get_line_number(path),
            )

    def _validate_position_array(self, coords, depth, path):
        if depth == 0:
            return self._validate_position(coords, path)
        if not isinstance(coords, list):
            return self._add_error(
                "Expected an array of coordinates",
                self._get_line_number(path),
            )
        for idx, c in enumerate(coords):
            self._validate_position_array(c, depth - 1, f"{path}/{idx}")

    def _add_error(self, message, line):
        self.errors.append({"message": message, "line": line or None})

    def _get_line_number(self, path):
        entry = self.line_map.get(path)
        # +1 as lines are zero-indexed
        return entry.value_start.line + 1 if entry else None

    def _is_invalid_type(self, obj, path):
        if not isinstance(obj, dict):
            return True
        obj_type = obj.get("type")
        if not obj_type or obj_type not in self.GEOJSON_TYPES:
            message = "Missing 'type'" if not obj_type else f"Invalid type '{obj_type}'"
            self._add_error(message, self._get_line_number(path))
            return True
        return False

    def _is_invalid_property(self, obj, name, type_str, path):
        if name not in obj:
            self._add_error(
                f'"{name}" member required',
                self._get_line_number(path.split("/" + name)[0]),
            )
            return True
        elif type_str == "array" and not isinstance(obj[name], list):
            self._add_error(
                f'"{name}" member should be an array, but is a {type(obj[name]).__name__} instead',
                self._get_line_number(path),
            )
            return True
        elif type_str == "object" and not isinstance(obj[name], dict):
            if name in ["geometry", "properties"] and obj[name] is None:
                return False
            self._add_error(
                f'"{name}" member should be an object, but is a {type(obj[name]).__name__} instead',
                self._get_line_number(path),
            )
            return True
        return False
