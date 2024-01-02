<img src="./preview-images/header_img.jpeg">

**Validate and automatically fix invalid GeoJSON. 🌎 Webapp and 🐍 Python package.** 

The only tool that reliably addresses all issues:
- Detects **invalid** geometries (GeoJSON specification): *duplicate nodes, wrong winding order, ...* 
- Detects **problematic** geometries (for some tools & APIs): *self-intersection, crossing anti-meridian, ...*
- Checks against **GeoJSON schema** if all required JSON elements exist 
- Automatically **fixes** invalid geometry issues 


<h3 align="center">
    🎈 <a href="https://geojson-validator.streamlit.app/">Try it out: geojson-validator webapp 🎈 </a>
</h3>

<br>

### Quickstart

```bash
# Installation
pip install geojson-validator
```

See the three main functions below. Data input can be any type of GeoJSON, a filepath/url to a GeoJSON, or anything with a `__geo_interface__` (shapely, geopandas etc.).

```python
import geojson_validator

geojson_input = {'type': 'FeatureCollection',
                 'features': [{'type': 'Feature', 'geometry':
                     {'type': 'Polygon', 'coordinates': [[[-59.758285, 8.367035], ...]]}}]}

geojson_validator.validate_schema(geojson_input)

geojson_validator.validate_geometries(geojson_input)

geojson_validator.fix_geometries(geojson_input)
```

### 1. Validate GeoJSON schema 📚

Checks the structure of the GeoJSON dictionary, if all required elements are there and formatted correctly.

```python
result, reason = geojson_validator.validate_schema(geojson_input)
```

The result is `(True, None)` if the input conforms to the GeoJSON schema, otherwise gives a reason why it is invalid
e.g. `(False, "key 'Feature' is missing")`.


### 2. Validate geometries 🟥

Checks the GeoJSON geometry objects for inconsistencies and geometric issues. See 
[geojson-invalid-geometry](https://github.com/chrieke/geojson-invalid-geometry) for a detailed description of all 
invalid and problematic criteria.

```python
result = geojson_validator.validate_geometries(geojson_input)
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

You can choose to validate only selected criteria, by default all are checked.
```python
# Invalid according to the GeoJSON specification
criteria_invalid = ["unclosed", "duplicate_nodes", "less_three_unique_nodes", "exterior_not_ccw",
                    "interior_not_cw", "inner_and_exterior_ring_intersect", "crs_defined",
                    "outside_lat_lon_boundaries"]

# Problematic with some tools & APIs
criteria_problematic = ["holes", "self_intersection", "excessive_coordinate_precision",
                        "more_than_2d_coordinates", "crosses_antimeridian"]

geojson_validator.validate_geometries(geojson, criteria_invalid, criteria_problematic)
```



### 3. Fix GeoJSON geometries 🟩

Fixes 6 of the most common categories of invalid geometries.
All other criteria can not be fixed in a programmatic way, they require user decisions 
(e.g. which part of a self-intersecting geometry should be dropped). More helper-functions for this coming soon!

```python
# Fixes "unclosed", "duplicate_nodes", "exterior_not_ccw", "interior_not_cw"
fixed_fc = geojson_validator.fix_geometries(geojson_input)
```

The result is a FeatureCollection with the fixed geometries.

<br>
<br>

## TODO:

- antimeridian example triggers outside latitude longtiude
- bug 3d coordinates
- shapely.to_geojson(a.buffer(3))
- jsondecodeerror when e.g. extra comma
- many vertices error? excessive_nodes   e.g. > 999    Can just be a very complex geometry, or e.g. when creating buffer geometries
- self intersections: polygons whose edges cross each other
- Reason not clear
- App: What was fixed & validate after again.
- test https://github.com/mapbox/geojsonhint/tree/master/test/data/bad & https://github.com/mapbox/geojsonhint/tree/master/test/data/good
- search chats & inet for problematic geojson/geometry for tests
- bbox order and other criteria
- Multihtreading?
- Post on SO, reddit etc. sites link to app
- fastapi as connector, not hosted just in package for others to run.
- add bbox option?
- Add geojson library simple validity checks https://github.com/jazzband/geojson/blob/c470a1f867579a39d25db2954aa8e909e79f3848/geojson/geometry.py#L79
- cli (webapp replaces it)?
- in app dataframe view with red/green. on click show in map.

No:
- Filsupport wkt etc. that would require more dependencies.

Notes:

old-style crs member is not recommended, this object is equivalent to the default and should be removed