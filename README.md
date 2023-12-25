# geojsonvalidate

**Validate and fix invalid GeoJSON**   

Ever encountered an invalid geometry error when dealing with GeoJSON? Even if a GeoJSON conforms 
to the GeoJSON specification, some tools or APIs might have issues with it. This Python library shows you 
all possible invalid and problematic issues with your GeoJSON and can fix them automatically.

## Installation

```bash
pip install geojsonvalidate
```

## Usage

Accepts a GeoJSON FeatureCollection, Feature, Polygon Geometry or MultiPolygon Geometry.

```python
import geojsonvalidate

geojson =  {'type': 'FeatureCollection',
    'features': [{'type': 'Feature', 'geometry': 
        {'type': 'Polygon', 'coordinates': [[[-59.758285, 8.367035],...]]}}]}

geojsonvalidate.validate(geojson)
```
The result gives the reason and positional index of the invalid geometry:

```json
{"invalid": {"duplicate_nodes": [2]},
 "problematic": {"self_intersection": [0, 2], "crosses_antimeridian": [1]},
 "count_geometry_types": {"Polygon": 2, "MultiPolygon": 1}}
```

## Parameters
To only evaluate specific validation criteria use the parameters `validate(geojson, criteria_invalid, criteria_problematic)`.
For details on all the invalid and problematic GeoJSON criteria see [geojson-invalid-geometry](https://github.com/chrieke/geojson-invalid-geometry).

```
# criteria_invalid
["unclosed", "duplicate_nodes", "less_three_unique_nodes", "exterior_not_ccw", "interior_not_cw", 
"inner_and_exterior_ring_intersect", "crs_defined", "outside_lat_lon_boundaries"]
```
```
# criteria_problematic
["holes", "self_intersection", "excessive_coordinate_precision", "more_than_2d_coordinates", 
"crosses_antimeridian"]
```

## Coming Soon:
- Automatically fixing geometries
- This library is still very early, expect breaking changes