<img src="./preview-images/header_img.jpeg">

**Validate and automatically fixes invalid GeoJSON. 🌎 Webapp and 🐍 Python package.** 

The only tool that addresses all issues:
- **Invalid** GeoJSON according to specification: e.g. duplicate nodes, wrong winding order, unclosed 
- **Problematic** with some tools & APIs: e.g. self-intersection, holes, crossing anti-meridian


<h3 align="center">
    🎈 <a href="https://geojson-validator.streamlit.app/">Try it out: geojson-validator webapp 🎈 </a>
</h3>

<br>

## Python package

#### Installation
```bash
pip install geojson-validator
```

### Validate GeoJSON

Input can be any GeoJSON (dictionary, filepath, url), shapely geometry, or anything with a `__geo_interface__`.

```python
import geojson_validator

geojson_input = {'type': 'FeatureCollection',
                 'features': [{'type': 'Feature', 'geometry':
                     {'type': 'Polygon', 'coordinates': [[[-59.758285, 8.367035], ...]]}}]}

geojson_validator.validate(geojson_input)
```
The result gives the reason and positional index of the invalid geometry.
```json
{"invalid": 
      {"duplicate_nodes": [2]},
 "problematic": 
      {"self_intersection": [0, 2], 
        "crosses_antimeridian": [1]},
 "count_geometry_types": 
      {"Polygon": 2, 
        "MultiPolygon": 1}}
```

### Fix GeoJSON

**Coming Soon!**

<br>

#### Parameters
It is possible to select only specific criteria for validation and fixing. For comprehensive criteria descriptions,
see the [geojson-invalid-geometry](https://github.com/chrieke/geojson-invalid-geometry) list.

```python
# Invalid according to the GeoJSON specification
criteria_invalid = ["unclosed", "duplicate_nodes", "less_three_unique_nodes", "exterior_not_ccw", 
                    "interior_not_cw", "inner_and_exterior_ring_intersect", "crs_defined", 
                    "outside_lat_lon_boundaries"]

# Problematic with some tools & APIs
criteria_problematic = ["holes", "self_intersection", "excessive_coordinate_precision", 
                        "more_than_2d_coordinates", "crosses_antimeridian"]

geojson_validator.validate(geojson, criteria_invalid, criteria_problematic)
```

<br>
<br>

## TODO:
- Put on website projects
- Automatically fix geometries
- Release 0.1, delete 0.0.1
- Check for incorrect geometry data type in type vs. geometry pattern
- bbox order and other criteria
- Multihtreading?
- Add tests for invalid/prob for each geometry type (gpt)
- refactor main
- add bbox option?

No:
- Filsupport wkt etc. that would require more dependencies.