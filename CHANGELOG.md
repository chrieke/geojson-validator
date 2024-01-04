# Changelog

Update your installation to the latest version:

=== "pip"

    ```bash
    pip install up42-py --upgrade
    ```

Check which version is currently installed:

=== "pip"

    ```bash
    pip show up42-py
    ```


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
