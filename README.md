# WORK IN PROGRESS
# geojsonvalidate

Validate and fix GeoJSON (Python). All possible invalid and problematic geometry issues.

Ever encountered an invalid geometry error when dealing with GeoJSON? Even if a GeoJSON conforms 
to the GeoJSON specification, some tools or APIs might have issues with it. This Python library shows you 
all possible invalid and problematic issues and fixes them automatically. 

See [geojson-invalid-geometry](https://github.com/chrieke/geojson-invalid-geometry) for a comprehensive list of all issues.

## Installation

```bash
pip install geojsonvalidate
```

## Usage

```python
import geojsonvalidate

geojsonvalidate.validate(geojson)
```

Accepts a GeoJSON FeatureCollection, Feature, Polygon Geometry or MultiPolygon Geometry.
