# geojsonfix

**Validates and automatically fixes your invalid GeoJSON data**   

Ever encountered an invalid geometry error when dealing with GeoJSON? Even if it conforms 
to the GeoJSON specification, some tools or APIs might have issues with it. This Python library shows you 
all possible invalid and problematic issues with your GeoJSON and can fix them automatically.

## Installation

```bash
pip install geojsonfix
```

## Usage

Accepts a GeoJSON FeatureCollection, Feature, Polygon Geometry or MultiPolygon Geometry.

```python
import geojsonfix

geojson = {'type': 'FeatureCollection',
           'features': [{'type': 'Feature', 'geometry':
             {'type': 'Polygon', 'coordinates': [[[-59.758285, 8.367035], ...]]}}]}

geojsonfix.validate(geojson)
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

```python
# Invalid according to the GeoJSON specification
criteria_invalid = ["unclosed", "duplicate_nodes", "less_three_unique_nodes", "exterior_not_ccw", 
                    "interior_not_cw", "inner_and_exterior_ring_intersect", "crs_defined", 
                    "outside_lat_lon_boundaries"]
```
```python
# valid, but problematic with some tools or APIs
criteria_problematic = ["holes", "self_intersection", "excessive_coordinate_precision", 
                        "more_than_2d_coordinates", "crosses_antimeridian"]
```

## Webapp

Coming Soon...

- File Upload: GeoJSON, JSON, KML, WKT, Shapefile (Zipfile containing shp,dbf,prj,shx files)
- Copy-paste: GeoJSON FeatureCollection, Feature, Geometry, Coordinates, bbox

## TODO:
- Automatically fix geometries
- Accept all Geometry types, validate/fix depending on type
- Add shapely input support
- Add support for all file input types as in app
- Banner image with geometry, inspection glass, hammer
- Check for incorrect geometry data type in type vs. geometry pattern
- bbox order and other criteria
- 