import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Import the required classes and functions
# pylint: disable=unused-import,wrong-import-position
from geojsonvalidate import checks_invalid
from geojsonvalidate import checks_problematic
