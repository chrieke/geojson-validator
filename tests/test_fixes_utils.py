from .context import fixes_utils
from .fixtures import read_geojson


def test_process_fix():
    fc = read_geojson(
        "./tests/data/invalid_geometries/invalid_exterior_not_ccw.geojson",
    )
    geometry_validation_results = {
        "invalid": {"exterior_not_ccw": [0]},
        "problematic": {},
        "count_geometry_types": {"Polygon": 0},
    }
    criteria = [
        "unclosed",
        "exterior_not_ccw",
        "interior_not_cw",
        "duplicate_nodes",
    ]  # "excessive_coordinate_precision", TODO
    fixed_fc = fixes_utils.process_fix(fc, geometry_validation_results, criteria)
    assert fixed_fc != fc
    assert len(fixed_fc["features"]) == 1


def test_process_fix_multigeom():
    fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-124.10446826928252, 49.27193446446772],
                                [-124.11750419994368, 49.27994147270371],
                                [-124.12689606250484, 49.283874318593504],
                                [-124.13464711227414, 49.29214509115894],
                                [-124.14549408624137, 49.29522284280057],
                                [-124.15657343692958, 49.293878893523974],
                                [-124.16313668808009, 49.29676320209966],
                                [-124.17199342506395, 49.30457633545649],
                                [-124.17996561227646, 49.31036985552304],
                                [-124.18381829948783, 49.3129531477033],
                                [-124.18944008624155, 49.312941393652146],
                                [-124.15647733620148, 49.25601920231696],
                                [-124.18024031893718, 49.25915322927615],
                                [-124.18585875475434, 49.26687454471484],
                                [-124.170361150497, 49.26849575671696],
                                [-124.14770546066919, 49.26518657060704],
                                [-124.13417691120077, 49.2639502953848],
                                [-124.11547863325129, 49.26556859469935],
                                [-124.10599673705812, 49.26862188977475],
                                [-124.10446826928252, 49.27193446446772],
                            ]
                        ],
                        [
                            [
                                [-123.20366412400031, 49.123428495036165],
                                [-123.23996181835875, 49.13423483908312],
                                [-123.23313491268677, 49.1358284897417],
                                [-123.20556019858563, 49.13606464929612],
                                [-123.2012429010334, 49.13970424532238],
                                [-123.20454280875938, 49.16200739653192],
                                [-123.20784271649477, 49.17566758897465],
                                [-123.19662303022699, 49.177609155130796],
                                [-123.19288313479812, 49.172647293127454],
                                [-123.18849634152625, 49.124532468852834],
                                [-123.19244936628289, 49.12330158370361],
                                [-123.20366412400031, 49.123428495036165],
                            ]
                        ],
                        [
                            [
                                [-122.66743487789853, 49.1881614957822],
                                [-122.67170722482153, 49.19533040857388],
                                [-122.67182269366643, 49.20370541518429],
                                [-122.65507971242758, 49.21245616503853],
                                [-122.63417985311065, 49.216981787698415],
                                [-122.6176678095465, 49.217811444433494],
                                [-122.60485076875031, 49.2162275438871],
                                [-122.60115576599443, 49.20521426100066],
                                [-122.60716014547009, 49.19661316468526],
                                [-122.63706657400357, 49.189821758973096],
                                [-122.66743487789853, 49.1881614957822],
                            ]
                        ],
                    ],
                },
            }
        ],
    }

    geometry_validation_results = {
        "invalid": {"exterior_not_ccw": [{0: [1, 2]}]},
        "problematic": {"excessive_coordinate_precision": [{0: [0, 1, 2]}]},
        "count_geometry_types": {"MultiPolygon": 1},
        "skipped_validation": [],
    }
    criteria = [
        "unclosed",
        "exterior_not_ccw",
        "interior_not_cw",
        "duplicate_nodes",
    ]  # "excessive_coordinate_precision", TODO
    fixed_fc = fixes_utils.process_fix(fc, geometry_validation_results, criteria)
    assert fixed_fc != fc
    assert len(fixed_fc["features"]) == 1
    assert len(fixed_fc["features"][0]["geometry"]["coordinates"]) == 3


# def test_process_fix_multigeom_geometrycollection():
# TODO
