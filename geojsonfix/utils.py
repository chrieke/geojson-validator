VALIDATION_CRITERIA = {
    "invalid": [
        "unclosed",
        "duplicate_nodes",
        "less_three_unique_nodes",
        "exterior_not_ccw",
        "interior_not_cw",
        "inner_and_exterior_ring_intersect",
        "defined_crs",
    ],
    "problematic": [
        "holes",
        "self_intersection",
        "excessive_coordinate_precision",
        "more_than_2d_coordinates",
        "crosses_antimeridian",
    ],
}


def consolidate_criteria(validation_criteria):
    criteria = [
        elem for elem in validation_criteria if not "invalid" or not "problematic"
    ]
    if "invalid" in validation_criteria:
        criteria.extend(VALIDATION_CRITERIA["invalid"])
    if "problematic" in validation_criteria:
        criteria.extend(VALIDATION_CRITERIA["problematic"])

    # TODO append all others
    # [criteria.append(c) for c in validation_criteria not in ["invalid", "problematic"]]
    criteria = list(set(criteria))

    return criteria
