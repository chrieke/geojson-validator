from geopandas import GeoDataFrame

from shapely import Polygon


def check_all_problematic(df, criteria):
    problematic_results = []
    if "holes" in criteria:
        if check_holes(df):
            problematic_results.append("holes")

    if "selfintersection" in criteria:
        if check_selfintersection(df):
            problematic_results.append("selfintersection")

    return problematic_results


# All invalid criteria. True returned if any geometry is invalid.
def check_selfintersection(df: GeoDataFrame) -> bool:
    return not all(df.geometry.apply(lambda x: x.is_valid).to_list())


def fix_selfintersection(df):
    df.geometry = df.geometry.buffer(0)


def check_holes(df: GeoDataFrame) -> bool:
    return any(
        row.geometry.geom_type == "Polygon" and row.geometry.interiors
        for _, row in df.iterrows()
    )


def fix_holes(df):
    def close_holes(poly: Polygon) -> Polygon:
        """
        Close polygon holes by limitation to the exterior ring.
        Args:
            poly: Input shapely Polygon
        Example:
            df.geometry.apply(lambda p: close_holes(p))
        """
        if poly.interiors:
            return Polygon(list(poly.exterior.coords))
        else:
            return poly

    df.geometry = df.geometry.apply(close_holes)
