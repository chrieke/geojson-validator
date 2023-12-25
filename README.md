# geojsonvalidate

Validate and fix GeoJSON (Python). All possible invalid and problematic geometry issues.

Ever encountered an invalid geometry error when dealing with GeoJSON? Even if a GeoJSON conforms 
to the GeoJSON specification, some tools or APIs might have issues with it. This Python library shows you 
all possible invalid and problematic issues and fixes them automatically.

## Installation

```bash
pip install geojsonvalidate
```

## Usage

```python
import geojsonvalidate

geojson =  {'type': 'FeatureCollection',
    'features': [{'type': 'Feature', 'geometry': 
        {'type': 'Polygon', 'coordinates': [[[-59.758285, 8.367035],...]]}}]}
geojsonvalidate.validate(geojson)
```
```json
{"invalid": {"duplicate_nodes": [2]},
 "problematic": 
     {"self_intersection": [0, 2],
      "crosses_antimeridian": [1]},
 "count_geometry_types": {"Polygon": 2, "MultiPolygon": 1}}
```

The validation gives the reason & positional index of the invalid geometry. 
See [geojson-invalid-geometry](https://github.com/chrieke/geojson-invalid-geometry) for a comprehensive list of all issues.

Accepts a GeoJSON FeatureCollection, Feature, Polygon Geometry or MultiPolygon Geometry.


## Coming Soon:
- Automatically fixing geometries
- This library is still very early, expect breaking changes