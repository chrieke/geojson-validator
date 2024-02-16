from typing import List, Any, Union


class GeoJsonLint:
    """
    Validates if the GeoJSON conforms to the geojson json schema rules 2020-12
    (https://json-schema.org/draft/2020-12/release-notes)

    In comparison to simple comparison to the schema via jsonschema library, this adds
    error line positions and clearer handling.

    Inspired by https://github.com/mapbox/geojsonhint (paused Javascript library)
    Focuses on structural GEOJSON schema validation, not GeoJSON specification geometry rules.
    """

    GEOMETRY_TYPES_DEPTHS = {
        "Point": {"array_depth": 1, "min_max_positions": (1, 1)},
        "LineString": {"array_depth": 2, "min_max_positions": (2, None)},
        "MultiPoint": {
            "array_depth": 2,
            "min_max_positions": (1, None),
        },  # should have 2 positions but is allowed 1
        "Polygon": {"array_depth": 3, "min_max_positions": (4, None)},
        "MultiLineString": {"array_depth": 3, "min_max_positions": (2, None)},
        "MultiPolygon": {"array_depth": 4, "min_max_positions": (4, None)},
        "GeometryCollection": {"array_depth": None, "min_max_positions": (None, None)},
    }
    GEOMETRY_TYPES = list(GEOMETRY_TYPES_DEPTHS.keys())
    GEOJSON_TYPES = [
        "FeatureCollection",
        "Feature",
    ] + GEOMETRY_TYPES

    def __init__(self, check_crs: bool = False):
        self.check_crs = check_crs
        self.feature_idx = None
        self.line_map = None
        self.errors = {}

    def lint(self, geojson_data: Union[dict, Any]):
        root_path = ""
        if not isinstance(geojson_data, dict):
            self._add_error("Root of GeoJSON must be an object/dictionary", root_path)
            return self.errors

        self._validate_geojson_root(geojson_data)

        return self.errors

    def _add_error(self, message: str, path: str):
        if message not in self.errors:
            self.errors[message] = {"path": [path]}
            if self.feature_idx is not None:
                self.errors[message]["feature"] = [self.feature_idx]
        else:
            self.errors[message]["path"].append(path)
            if self.feature_idx is not None:
                self.errors[message]["feature"].append(self.feature_idx)

    def _validate_geojson_root(self, obj: Union[dict, Any]):
        """Validate that the geojson object root directory conforms to the requirements."""
        root_path = ""
        if self._is_invalid_type_property(obj, self.GEOJSON_TYPES, root_path):
            return

        obj_type = obj.get("type")
        if obj_type == "FeatureCollection":
            self._validate_feature_collection(obj, root_path)
        elif obj_type == "Feature":
            self._validate_feature(obj, root_path)
        elif obj_type in self.GEOMETRY_TYPES:
            self._validate_geometry(obj, root_path)

    def _validate_feature_collection(
        self, feature_collection: Union[dict, Any], path: str
    ):
        """Validate that the featurecollection object conforms to the requirements."""
        self._is_invalid_type_property(
            feature_collection, ["FeatureCollection"], f"{path}/type"
        )

        if self.check_crs and "crs" in feature_collection:
            self._add_error(
                "The newest GeoJSON specification defines GeoJSON as always latitude/longitude, remove "
                "CRS (coordinate reference system) member",
                f"{path}/crs",
            )

        if (
            not self._is_invalid_property(
                feature_collection, "features", "array", f"{path}/features"
            )
            and feature_collection["features"]
        ):  # allowed to be empty
            for idx, feature in enumerate(feature_collection["features"]):
                self.feature_idx = idx
                if not isinstance(feature, dict):
                    self._add_error(
                        "Every feature must be a dictionary/object.",
                        f"{path}/features/{idx}",
                    )
                else:
                    self._validate_feature(feature, f"{path}/features/{idx}")

        bbox = feature_collection.get("bbox")
        if bbox:
            self._validate_bbox(bbox, f"{path}/bbox")

    def _validate_feature(self, feature: Union[dict, Any], path: str):
        """Validate that the feature object conforms to the requirements."""
        self._is_invalid_type_property(feature, ["Feature"], f"{path}/type")
        if "id" in feature and not isinstance(feature["id"], (str, int)):
            self._add_error(
                'Feature "id" member must be a string or int number',
                f"{path}/id",
            )
        self._is_invalid_property(feature, "properties", "object", f"{path}/properties")
        self._is_invalid_property(feature, "geometry", "object", f"{path}/geometry")

        geom = feature.get("geometry")
        if geom:
            self._validate_geometry(geom, f"{path}/geometry")

        bbox = feature.get("bbox")
        if bbox:
            self._validate_bbox(bbox, f"{path}/bbox")

    def _validate_geometry(self, geometry: dict, path: str):
        """Validate that the geometry object conforms to the requirements."""
        if self._is_invalid_type_property(
            geometry, self.GEOMETRY_TYPES, f"{path}/type"
        ):
            return

        obj_type = geometry.get("type")
        if obj_type == "GeometryCollection":
            if not self._is_invalid_property(geometry, "geometries", "array", path):
                for idx, geom in enumerate(geometry["geometries"]):
                    if not self._is_invalid_datatype(
                        geom, dict, path
                    ):  # geometries: [false]
                        self._validate_geometry(geom, f"{path}/geometries/{idx}")
        elif not self._is_invalid_property(geometry, "coordinates", "array", path):
            # All other geometry types
            if not self._is_incorrect_coordinates_depth(
                geometry["coordinates"], obj_type, f"{path}/coordinates"
            ):
                self._validate_position_array(
                    geometry["coordinates"], f"{path}/coordinates"
                )
                # validate_min/max positions #TODO

        bbox = geometry.get("bbox")
        if bbox:
            self._validate_bbox(bbox, f"{path}/bbox")

    def _is_invalid_datatype(
        self, obj: Union[dict, list, Any], required_data_type, path
    ):
        if not isinstance(obj, required_data_type):
            self._add_error(
                f"Object must be a '{required_data_type}', but is a {type(obj)} instead",
                path,
            )
            return True

    def _is_invalid_type_property(
        self, obj: Union[dict, Any], allowed_types: List[str], path: str
    ):
        """
        Checks if an object type member conforms to the requirements.

        Args:
            obj: The object to check the property of
            allowed_types: List of the allowed types to check against.
            path: The line_map path pointing to the type property in question.
        """
        if not isinstance(obj, dict):
            return True
        obj_type = obj.get("type")
        if obj_type is None:
            self._add_error("Missing 'type' member", path.split("/type")[0])
            return True
        if obj_type not in allowed_types:
            self._add_error(
                f"Invalid 'type' member, is '{obj_type}', must be one of {allowed_types}",
                path,
            )
            return True
        return False

    def _is_invalid_property(
        self, obj: Union[dict, Any], property_name: str, required_type: str, path: str
    ):
        """
        Checks if an object property conforms to the requirements.

        Args:
            obj: The object to check the property of
            required_type: The expected type as a string, one of "array" or "object"
            property_name: The property name
            path: The line_map path pointing to the property in question.
        """
        if property_name not in obj:
            self._add_error(
                f'"{property_name}" member required',
                path.split("/" + property_name)[0],
            )
            return True
        property_value = obj[property_name]
        property_type = type(property_value).__name__
        if required_type == "array" and not isinstance(property_value, list):
            self._add_error(
                f'"{property_name}" member must be an array, but is a {property_type} instead',
                path,
            )
            return True
        if required_type == "object":
            if property_name in ["geometry", "properties"] and property_value is None:
                return False
            if not isinstance(property_value, dict):
                self._add_error(
                    f'"{property_name}" member must be an object/dictionary, but is a {property_type} instead',
                    path,
                )
                return True
        return False

    def _is_incorrect_coordinates_depth(self, coords, obj_type, path):
        def _determine_array_depth(array, current_depth=0):
            """Recursively determine the depth of an array."""
            if not isinstance(array, list) or not array:
                return current_depth
            return _determine_array_depth(array[0], current_depth + 1)

        expected_depth = self.GEOMETRY_TYPES_DEPTHS[obj_type]["array_depth"]
        actual_depth = _determine_array_depth(coords)

        if actual_depth != expected_depth:
            message = "not deep enough" if actual_depth < expected_depth else "too much"
            self._add_error(
                f"Array is {message} nested, expected depth {expected_depth} for type '{obj_type}', "
                f"found depth {actual_depth}",
                path,
            )
            return True
        return False

    def _validate_position(self, coords: Union[list, Any], path: str):
        """Validate that the single coordinate position conforms to the requirements."""
        if len(coords) < 2:
            self._add_error(
                "Coordinate position must have at least 2 values (longitude, latitude)",
                path,
            )
        elif len(coords) > 3:
            self._add_error(
                "Coordinate position should not have more than 3 values (longitude, latitude and optional elevation).",
                path,
            )
        if not all(isinstance(coord, (int, float)) for coord in coords):
            self._add_error(
                "Each element in a coordinate position must be a number",
                path,
            )

    def _validate_position_array(self, coords: Union[list, Any], path: str):
        """Validate that the array of multiple coordinate positions conforms to the requirements."""
        # If the first element is a list, recurse further
        if len(coords) and isinstance(coords[0], list):  # avoid empty list index error
            for i, subarray in enumerate(coords):
                self._validate_position_array(subarray, f"{path}/{i}")
        else:
            self._validate_position(coords, path)

    def _validate_bbox(self, bbox: Union[list, Any], path):
        if not isinstance(bbox, list):
            self._add_error(
                "'bbox' member must be a one-dimensional array with bounding box coordinates",
                path,
            )
            return
        if not all(isinstance(p, (int, float)) for p in bbox):
            self._add_error(
                "'bbox' member array must contain only numbers",
                path,
            )
        if len(bbox) not in (4, 6):
            self._add_error(
                "'bbox' member array must consist of 4 or 6 coordinates",
                path,
            )
        # TODO: Check order.
