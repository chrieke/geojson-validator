# Changelog

Update your installation to the latest version:

=== "pip"

    ```bash
    # pip show geojson-validator  # check currently installed version
    pip install geojson-validator --upgrade
    ```

## 0.7.0
**August 02, 2026**

- Requires Python >= 3.10
- Move `inner_and_exterior_ring_intersect` from the `invalid` to the `problematic` criteria, it no longer flags rings that touch in a single point
- All checks now cover every Polygon ring, before only the exterior ring was checked
- `excessive_coordinate_precision` also detects exponent notation (e.g. `1e-07`), it and `3d_coordinates` no longer miss issues after the first two coordinates
- `validate_geometries` no longer raises on geometries that shapely cannot parse or that are structurally broken, the feature index is reported in `skipped_validation` instead
- Fix `validate_geometries` modifying the input GeoJSON
- Fix `fix_geometries` not applying the fixes to the sub-geometries of MultiPolygons & GeometryCollections
- Fix the `duplicate_nodes` fix removing meaningful collinear vertices
- Fix `validate_structure` reporting a FeatureCollection-level `bbox` error under the last feature, and a reused `GeoJsonLint` instance repeating the errors of previous calls
- Fixed & completed type hints
- Speed improvements.

## 0.6.0
**November 29, 2024**

- Add `configure_logging` function to configure logging behavior
- `pyproject.toml` replaces setup.py & requirements.txt files

## 0.5.2
**March 27, 2024**

- Fix issue `fix_geometries` not applied to multigeometries

## 0.5.1
**February 16, 2024**

- Fix breaking issue unused imports

## 0.5.0
**January 19, 2024**

- Rename `main.validate_schema` to `main.validate_structure`.
- Change .validate_structure result from list to dictionary. Now adds feature position. Line position now points to exact subelement.
- Move "duplicate_nodes" & "outside_latlon_boundary" to problematic checks.
- Move "duplicate_nodes" to optional fix.
- Move crs check to .validate_sstructure, now optional.
- Enable Geometrycollection as valid type.
- Various improvements and fixes

## 0.3.0
**January 14, 2024**

- Change .validate_schema result from list to dictionary of error messages, with line and feature position of each error.
- Move crs check to .validate_schema, now optional.
- Enable Geometrycollection as valid type.
- Various improvements and fixes


## 0.3.0
**January 04, 2024**

- `.validate_schema()` now returns a list of errors (empty if valid) and adds line numbers to better locate the issue.
- adds check for excessive vertices (>999) as `problematic` criteria
- Various improvements and fixes (e.g. 3d coordinate handling)
- (Developer): Adds `make redownload-testfiles` to use https://github.com/chrieke/geojson-invalid-geometry as origin

## 0.2.0
**January 01, 2024**

- Adds `validate_schema`
- Renamed `validate` to `validate_geometries` and `fix` to `fix_geometries`
- Various improvements and fixes

## 0.1.0
**December 28, 2023**

- Initial Release
