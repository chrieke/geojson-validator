import geopandas as gpd


def read_geometry_input(geometry):
    """

    Args:
        geometry: geojson dict, shapely geometry or anything with __geo_interface__ e.g. Geopandas Geodataframes etc.

    Returns:
        geopandas geodataframe
    """
    df = gpd.GeoDataFrame.from_features(features=geometry, crs="EPSG:4326")
    # TODO: ADD OTHER TYPES
    return df


# GEOJSON_OBJECTS = {
#     "point": "Point",
#     "multipoint": "MultiPoint",
#     "linestring": "LineString",
#     "multilinestring": "MultiLineString",
#     "polygon": "Polygon",
#     "multipolygon": "MultiPolygon",
# }


# def check_is_single_feature(self) -> None:
#     self.is_single_feature = self.df.shape[0] == 1
#
#
# def check_is_polygon(self) -> None:
#     self.is_polygon = all((t == "Polygon" for t in self.df.geometry.geom_type.unique()))
#
#
# def check_is_single_ring(self) -> None:
#     self.is_single_ring = (
#         len(self.df.iloc[0].geometry.__geo_interface__["coordinates"]) == 1
#     )
#
#
# def check_is_4326(self) -> None:
#     self.is_4326 = self.df.crs == "EPSG:4326"
