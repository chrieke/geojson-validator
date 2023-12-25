import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Import the required classes and functions
# pylint: disable=unused-import,wrong-import-position
from geojson_validate import checks_invalid
from geojson_validate import checks_problematic
from geojson_validate.main import validate
