import json
from json_source_map import calculate


class GeoJsonLint:
    """
    Validates if the GeoJSON conforms to the geojson json schema rules 2020-12
    (https://json-schema.org/draft/2020-12/release-notes)

    In comparison to simple comparison to the schema via jsonschema library, this adds
    error line positions and clearer handling.

    Inspired by https://github.com/mapbox/geojsonhint (paused Javascript library)
    Adapted to Python and focuses on structural GEOJSON schema validation, not GeoJSON
    specification geometry rules.
    """

    def __init__(self):
        self.errors = []
        self.line_map = None
        self.geojson_types = [
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

    def lint(self, gj):
        formatted_gj_string = json.dumps(
            gj, sort_keys=True, indent=2, separators=(",", ": ")
        )
        self.line_map = calculate(formatted_gj_string)

        if type(gj) not in [dict, list]:
            self.errors.append(
                {
                    "message": "The root of a GeoJSON object must be an object.",
                    "line": 0,
                }
            )
            return self.errors

        self.root(gj, "")
        for err in self.errors:
            if "line" in err and err["line"] is None:
                del err["line"]
        return self.errors

    def root(self, obj, path):
        if self.invalid_required_type(obj, path):
            return

        obj_type = obj.get("type")
        if obj_type == "FeatureCollection":
            self.feature_collection(obj, path)
        elif obj_type == "Feature":
            self.feature(obj, path)
        elif obj_type in self.geojson_types:
            self.geometry(obj, path)
        # self.geometry_types[obj.get('type')](obj, path)

    def feature_collection(self, feature_collection, path):
        self.invalid_required_type(feature_collection, path)
        if not self.invalid_required_property(
            feature_collection, "features", "array", path
        ):
            for idx, feature in enumerate(feature_collection["features"]):
                if not isinstance(feature, dict):
                    self.errors.append(
                        {
                            "message": f"Every feature must be an object. feature nr {idx} is not",
                            "line": self.get_line_number(f"{path}/features/{idx}"),
                        }
                    )
                else:
                    self.feature(feature, f"{path}/features/{idx}")

    def feature(self, feature, path):
        self.invalid_required_type(feature, path)
        if "id" in feature and not isinstance(feature["id"], (str, int)):
            self.errors.append(
                {
                    "message": 'Feature "id" member must have a string or number value',
                    "line": self.get_line_number(f"{path}/id"),
                }
            )
        self.invalid_required_property(
            feature, "properties", "object", f"{path}/properties"
        )
        self.invalid_required_property(
            feature, "geometry", "object", f"{path}/geometry"
        )
        geom = feature.get("geometry")
        if geom:
            self.geometry(geom, f"{path}/geometry")

    def geometry(self, obj, path):
        if self.invalid_required_type(obj, path):
            return

        obj_type = obj.get("type")
        if obj_type == "GeometryCollection":
            if not self.invalid_required_property(obj, "geometries", "array", path):
                for idx, geom in enumerate(obj["geometries"]):
                    self.geometry(geom, f"{path}/geometries/{idx}")
        elif not self.invalid_required_property(obj, "coordinates", "array", path):
            if obj_type in ["Point"]:
                self.position(obj["coordinates"], f"{path}/coordinates")
            elif obj_type in ["LineString", "MultiPoint"]:
                self.position_array(obj["coordinates"], 1, f"{path}/coordinates")
            elif obj_type in ["Polygon", "MultiLineString"]:
                self.position_array(obj["coordinates"], 2, f"{path}/coordinates")
            elif obj_type in ["MultiPolygon"]:
                self.position_array(obj["coordinates"], 2, f"{path}/coordinates")

    def get_line_number(self, path):
        entry = self.line_map.get(path)
        if entry:
            return entry.value_start.line + 1  # +1 as lines are zero-indexed
        return None

    def invalid_required_type(self, obj, path):
        obj_type = obj.get("type")
        if not obj_type or obj_type not in self.geojson_types:
            if not obj_type:
                message = "Missing 'type'"
            elif obj_type not in self.geojson_types:
                message = f"Invalid type '{obj_type}'"
            self.errors.append({"message": message, "line": self.get_line_number(path)})
            return True
        return False

    def invalid_required_property(self, obj, name, type_str, path):
        if name not in obj:
            self.errors.append(
                {
                    "message": f'"{name}" member required',
                    "line": self.get_line_number(path.split("/" + name)[0]),
                }
            )
            return True
        elif type_str == "array" and not isinstance(obj[name], list):
            self.errors.append(
                {
                    "message": f'"{name}" member should be an array, but is a {type(obj[name]).__name__} instead',
                    "line": self.get_line_number(path),
                }
            )
            return True
        elif type_str == "object" and not isinstance(obj[name], dict):
            # TODO: For geometry this is valid but problematic?
            self.errors.append(
                {
                    "message": f'"{name}" member should be an object, but is a {type(obj[name]).__name__} instead',
                    "line": self.get_line_number(path),
                }
            )
            return True
        return False

    def position(self, coords, path):
        if not isinstance(coords, list):
            return self.errors.append(
                {
                    "message": "Position should be an array",
                    "line": self.get_line_number(path),
                }
            )
        if len(coords) < 2 or len(coords) > 3:
            return self.errors.append(
                {
                    "message": "Position must have 2 or more elements",
                    "line": self.get_line_number(path),
                }
            )
        if not all(isinstance(coord, (int, float)) for coord in coords):
            return self.errors.append(
                {
                    "message": "Each element in a position must be a number",
                    "line": self.get_line_number(path),
                }
            )

    def position_array(self, coords, depth, path):
        if depth == 0:
            return self.position(coords, path)
        if not isinstance(coords, list):
            return self.errors.append(
                {
                    "message": "Expected an array of coordinates",
                    "line": self.get_line_number(path),
                }
            )
        for idx, c in enumerate(coords):
            self.position_array(c, depth - 1, f"{path}/{idx}")
