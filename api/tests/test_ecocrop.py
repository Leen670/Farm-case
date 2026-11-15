"""EcoCrop ranges for three familiar crops, plus a reading outside the table.

The numbers are the OpenCLIM snapshot of FAO EcoCrop, not values we chose.
No network, and no call into the rotation ranker.
"""

from app.ecocrop import find_crop


def test_wheat_scores_one_inside_its_temperature_optimum():
    wheat = find_crop("wheat")

    assert wheat.scientific_name == "Triticum aestivum"
    assert (wheat.temp_min, wheat.temp_opt_lo, wheat.temp_opt_hi, wheat.temp_max) == (
        5,
        15,
        23,
        27,
    )
    # 19°C sits between the two optima, 15 and 23.
    assert wheat.temperature(19) == 1


def test_maize_climbs_linearly_between_its_minimum_and_its_optimum():
    maize = find_crop("maize")

    assert maize.scientific_name == "Zea mays"
    # Absolute minimum 10°C, optimal minimum 18°C. 14°C is halfway up.
    assert maize.temperature(14) == 0.5


def test_okra_scores_one_inside_its_rainfall_optimum():
    okra = find_crop("okra")

    assert okra.scientific_name == "Abelmoschus esculentus"
    # Optimal rain is 600–1200 mm. 900 mm is inside that band.
    assert okra.rain(900) == 1


def test_wheat_scores_zero_outside_its_temperature_limits():
    wheat = find_crop("wheat")

    # Absolute limits are 5°C and 27°C. Both of these are outside.
    assert wheat.temperature(0) == 0
    assert wheat.temperature(40) == 0
