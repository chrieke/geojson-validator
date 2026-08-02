# Changelog

Update your installation to the latest version:

=== "pip"

    ```bash
    # pip show geojson-validator  # check currently installed version
    pip install geojson-validator --upgrade
    ```

## Unreleased

- Ship a `py.typed` marker (PEP 561), so type checkers use the annotations instead of treating the
  package as untyped
- Fix incorrect type hints: `criteria_invalid`/`criteria_problematic` were annotated `List[str]` but
  defaulted to a dict (now the `INVALID_CRITERIA`/`PROBLEMATIC_CRITERIA` tuples of criteria names),
  `validate_geometries` documented the wrong return value, and `fix_geometries` and
  `configure_logging` were unannotated. The package now type checks cleanly (`make typecheck`)
- Passing a single criteria string instead of a list raises a clear error instead of validating
  against the individual characters
- Fix `fix_geometries` not applying fixes to the sub-geometries of MultiPolygons/GeometryCollections
  (results were written to a wrong key, leaving the coordinates unchanged)
- Fix `validate_geometries` mutating the input GeoJSON (Point/LineString coordinates were rewritten in place)
- Checks now cover all Polygon rings instead of only the exterior ring
  (`unclosed`, `less_three_unique_nodes`, `duplicate_nodes`, `excessive_coordinate_precision`,
  `3d_coordinates`, `outside_lat_lon_boundaries`, `crosses_antimeridian`)
- `excessive_vertices` now counts the vertices of all rings, not only the exterior ring
- `inner_and_exterior_ring_intersect` moved from the `invalid` to the `problematic` criteria
  (valid GeoJSON, but invalid by the OGC Simple Features standard), and no longer flags rings
  touching at a single point, matching [geojson-invalid-geometry](https://github.com/chrieke/geojson-invalid-geometry)
- `excessive_coordinate_precision` now also detects coordinates in exponent notation (e.g. `1e-07`)
- `fix_geometries` returns plain lists instead of tuples in the fixed coordinates
- Fix `fix_geometries` `duplicate_nodes` removing meaningful collinear vertices (use `shapely.remove_repeated_points` instead of `simplify(0)`)
- Fix `3d_coordinates` and `excessive_coordinate_precision` checks missing issues on vertices after the first two (now scan all coordinates)
- `validate_geometries` no longer crashes on geometries shapely cannot parse (e.g. mixed 2D/3D coordinates); raw-JSON checks still run, shapely-based checks are skipped
- Winding-order fixes now use `shapely.geometry.polygon.orient`
- `read_geojson_file_or_url` raises a clear HTTP error instead of silently falling through to a file open on non-200 responses
- Logging is configured in a single module instead of three (no longer wipes the global loguru logger multiple times on import)
- Require Python >= 3.10 (Python 3.9 is end-of-life; the current `requests` and `shapely` releases
  no longer support it), and bump the dependency floors to `loguru>=0.7.3`, `requests>=2.34.2`,
  `shapely>=2.1.2`
- Fix `validate_structure` reporting a FeatureCollection-level `bbox` error under the index of the
  last feature instead of no feature
- Fix a reused `GeoJsonLint` instance reporting the errors of previous `lint()` calls
- Fix `read_geojson_file_or_url` rejecting URLs with a query string (e.g. presigned URLs), because
  the query was read as part of the file suffix; the suffix check is now also case-insensitive
- Fix `fix_geometries(optional=["duplicate_nodes"])` crashing on a fully degenerate ring
  (`shapely` raises `GEOSException`, which is not a `ValueError`)

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
