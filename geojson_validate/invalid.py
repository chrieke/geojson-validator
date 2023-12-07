from shapely.ops import orient


def check_exterior_ccw(df) -> bool:
    return all(
        row.geometry.exterior.is_ccw
        for _, row in df.iterrows()
        if row.geometry.geom_type == "Polygon"
    )


def fix_exterior_ccw(df):
    df.geometry = df.geometry.apply(
        lambda x: orient(x) if x.geom_type == "Polygon" else x
    )


def check_duplicate_nodes(df) -> bool:
    have_duplicates = []
    for _, row in df.iterrows():
        # Same first and last coordinate vertices is ignored.
        coords = list(row.geometry.exterior.coords)[1:-1]
        have_duplicates.append(len(coords) != len(set(coords)))
    if any(have_duplicates):
        return True


def fix_duplicate_nodes(df):
    df.geometry = df.geometry.simplify(0)
