from typing import List, Union
import sys
from dataclasses import dataclass

from loguru import logger

from .invalid import *
from .problematic import *

logger.remove()
logger_format = "{time:YYYY-MM-DD_HH:mm:ss.SSS} | {message}"
logger.add(sink=sys.stderr, format=logger_format, level="INFO")


# pylint: disable=unused-argument, attribute-defined-outside-init
@dataclass
class Validation:
    """
    Handles the invalid geometry checks, data input and validation results.
    """

    df: GeoDataFrame = None

    any_invalid: bool = False
    unclosed: bool = False
    duplicate_nodes: bool = False
    less_three_unique_nodes: bool = False
    exterior_cw: bool = False
    interior_ccw: bool = False

    any_problematic: bool = False
    holes: bool = False
    selfintersection: bool = False

    def validate(self, validation_criteria: Union[List[str], None] = None) -> None:
        """
        Checks all validity conditions.
        """
        ### Invalid ###
        if "duplicate_nodes" in validation_criteria:
            self.duplicate_nodes = check_duplicate_nodes(self.df)

        if "exterior_ccw" in validation_criteria:
            self.exterior_ccw = check_exterior_ccw(self.df)

        if any([self.duplicate_nodes, self.exterior_ccw]):
            self.any_invalid = True

        ### Problematic ###
        if "no_holes" in validation_criteria:
            self.holes = check_holes(self.df)

        if "no_selfintersection" in validation_criteria:
            self.selfintersection = check_selfintersection(self.df)

        if any([self.holes, self.selfintersection]):
            self.any_problematic = True
