from typing import List, Union
import sys
from pathlib import Path
from dataclasses import dataclass

import geopandas as gpd
from geopandas import GeoDataFrame
from loguru import logger

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
    duplicate_nodes: bool = (False,)
    less_three_unique_nodes: bool = False
    exterior_cw: bool = False
    interior_ccw: bool = False
    holes: bool = False
    selfintersection: bool = False

    @classmethod
    def from_file(cls, fp=Union[str, Path]):
        validation = cls()
        validation.df = gpd.read_file(fp)
        return validation

    @classmethod
    def from_geojson_dict(cls, geojson_dict: dict):
        validation = cls()
        validation.df = gpd.GeoDataFrame.from_features(
            features=geojson_dict, crs="EPSG:4326"
        )
        return validation

    def validate(self, validation_criteria: Union[List[str], None] = None) -> None:
        """
        Checks all validity conditions.
        """
        if "duplicate_nodes" in validation_criteria:
            self.duplicate_nodes = check_duplicate_nodes(self.df)

        if "exterior_ccw" in validation_criteria:
            self.exterior_ccw = check_exterior_ccw(self.df)

        if "no_holes" in validation_criteria:
            self.holes = check_holes(self.df)

        if "no_selfintersection" in validation_criteria:
            self.selfintersection = check_selfintersection(self.df)

        if any(
            [self.duplicate_nodes, self.exterior_ccw, self.holes, self.selfintersection]
        ):
            self.any_invalid = True


# All invalid criteria. True returned if any geometry is invalid.
def check_selfintersection(df: GeoDataFrame) -> bool:
    return not all(df.geometry.apply(lambda x: x.is_valid).to_list())


def check_holes(df: GeoDataFrame) -> bool:
    return any(
        row.geometry.geom_type == "Polygon" and row.geometry.interiors
        for _, row in df.iterrows()
    )


def check_exterior_ccw(df) -> bool:
    return all(
        row.geometry.exterior.is_ccw
        for _, row in df.iterrows()
        if row.geometry.geom_type == "Polygon"
    )


def check_duplicate_nodes(df) -> bool:
    have_duplicates = []
    for _, row in df.iterrows():
        # Same first and last coordinate vertices is ignored.
        coords = list(row.geometry.exterior.coords)[1:-1]
        have_duplicates.append(len(coords) != len(set(coords)))
    if any(have_duplicates):
        return True
