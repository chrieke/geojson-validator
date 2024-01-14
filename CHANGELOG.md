# Changelog

Update your installation to the latest version:

=== "pip"

    ```bash
    # pip show geojson-validator # check currently installed version
    pip install geojson-validator --upgrade
    ```

## 0.4.0
**January 04, 2024**

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
