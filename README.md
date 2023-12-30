<img src="./preview-images/header_img.jpeg">

**Validate and automatically fix invalid GeoJSON. 🌎 Webapp and 🐍 Python package.** 

The only tool that addresses all issues:
- Detects **invalid** geometries (GeoJSON **specification**): e.g. duplicate nodes, wrong winding order, ... 
- Detects **problematic** geometries (for some tools & APIs): e.g. self-intersection, crossing anti-meridian, ...
- Compares against the GeoJSON **schema** - if all required json elements exist
- Automatically **fixes** invalid geometry issues 


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

Input can be any type of GeoJSON, a filepath/url to a GeoJSON, or anything with a `__geo_interface__` (shapely, geopandas etc.).

```python
import geojson_validator

geojson_input = {'type': 'FeatureCollection',
                 'features': [{'type': 'Feature', 'geometry':
                     {'type': 'Polygon', 'coordinates': [[[-59.758285, 8.367035], ...]]}}]}

geojson_validator.validate(geojson_input)
```
The result gives the reason and positional indices of the invalid geometries e.g. `[0, 3]`. 
It also shows which of the sub-geometries within a MultiType geometry make it invalid e.g. `{2:[0, 5]}`.

```
{"invalid": 
      {"duplicate_nodes": [0, 3],
       "exterior_not_ccw":  [{2:[0, 5]}],  
 "problematic":
      {"crosses_antimeridian": [1]},
 "count_geometry_types": 
      {"Polygon": 3,
       "MultiPolygon": 1}}
```

### Fix GeoJSON

By default the `fix` function fixes 6 categories:

```python
geojson_validator.fix(geojson_input)
```

The other criteria can not be fixed in a similarly programmatic way, they require user input or case-by-case handling.

#### Parameters
It is possible to select only specific criteria for validation and fixing, by default all are checked. 
For detailed descriptions of the criteria, see the [geojson-invalid-geometry](https://github.com/chrieke/geojson-invalid-geometry) list.

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
- Add Schema validation as seperate func?
- bbox order and other criteria
- Multihtreading?
- add bbox option?
- Add geojson library simple validity checks https://github.com/jazzband/geojson/blob/c470a1f867579a39d25db2954aa8e909e79f3848/geojson/geometry.py#L79

No:
- Filsupport wkt etc. that would require more dependencies.