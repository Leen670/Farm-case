"""The rotation rules, pinned to numbers. No network, no NASA call."""

import json
from pathlib import Path
from typing import get_args

from app.crops import CROPS, get_crop
from app.models import Soil
from app.nasa_power import parse_climatology
from app.scoring import FarmConditions, rank_rotations, rotation_delta, score_rotation

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"
DEMO_FIXTURES = ("power_iowa.json", "power_punjab.json", "power_andalusia.json")

# A mild farm where water, heat, soil, and salt all fit the test crops.
# The gap between the two plans is then the rotation rules alone.
GENTLE = FarmConditions(
    rain_mm=700,
    max_temp_c=30,
    avg_temp_c=16,
    soil="loamy",
    water_level="available",
    water_source="rain",
)


def _points(rotation: tuple[str, str, str], **overrides: object) -> int:
    data = {
        "rain_mm": GENTLE.rain_mm,
        "max_temp_c": GENTLE.max_temp_c,
        "avg_temp_c": GENTLE.avg_temp_c,
        "soil": GENTLE.soil,
        "water_level": GENTLE.water_level,
        "water_source": GENTLE.water_source,
    }
    data.update(overrides)
    conditions = FarmConditions(**data)
    crops = tuple(get_crop(name) for name in rotation)
    return rotation_delta(crops, conditions).points


def _limited_from_fixture(filename: str, priorities: tuple[str, ...] = ()) -> FarmConditions:
    payload = json.loads((FIXTURE_DIR / filename).read_text(encoding="utf-8"))
    climate = parse_climatology(payload)
    return FarmConditions(
        rain_mm=climate.rain_mm_per_year,
        max_temp_c=climate.annual_max_temp_c,
        avg_temp_c=climate.avg_temp_c,
        soil="loamy",
        water_level="limited",
        water_source="rain",
        priorities=priorities,
    )


def test_crop_table_matches_the_contract():
    soils = set(get_args(Soil))
    names = {crop.name for crop in CROPS}
    assert len(CROPS) >= 12
    assert {"wheat", "chickpea", "alfalfa", "maize"} <= names
    assert get_crop("alfalfa").water_need_mm >= 800
    assert get_crop("corn").name == "maize"
    for crop in CROPS:
        assert set(crop.soil_pref) <= soils


def test_legume_after_cereal_beats_cereal_after_cereal():
    legume = score_rotation(("wheat", "chickpea", "barley"), GENTLE)
    cereals = score_rotation(("wheat", "barley", "sorghum"), GENTLE)

    assert _points(("wheat", "chickpea", "barley")) == 10
    assert _points(("wheat", "barley", "sorghum")) == -30
    assert legume.suitability > cereals.suitability
    assert legume.suitability - cereals.suitability >= 20
    assert any("nitrogen crop after a cereal, +10" in reason for reason in legume.reasons)
    assert any("same family (cereal), -15" in risk for risk in cereals.risks)


def test_rotation_rules_stack():
    # Wheat again is both the same family (−15) and a repeat of the previous crop (−10).
    # Barley after that wheat is another cereal pair (−15). Chickpea after barley is +10.
    assert _points(("wheat", "barley", "chickpea"), previous_crops=("wheat",)) == -30
    assert _points(("wheat", "chickpea", "barley"), priorities=("improve_soil",)) == 15
    # Improve soil also pays the deep-root crop. Sorghum is the structure row.
    assert _points(("wheat", "chickpea", "sorghum"), priorities=("improve_soil",)) == 20


def test_limited_water_never_ranks_alfalfa_first():
    priority_sets = (
        (),
        ("save_water",),
        ("increase_yield",),
        ("improve_soil",),
        ("lower_cost",),
    )
    for filename in DEMO_FIXTURES:
        for priorities in priority_sets:
            conditions = _limited_from_fixture(filename, priorities)
            result = rank_rotations(conditions)
            leader = result.recommended.rotation[0]
            assert leader != "alfalfa", (filename, priorities, result.recommended.rotation)


def test_scores_stay_between_0_and_100():
    brutal = FarmConditions(
        rain_mm=50,
        max_temp_c=50,
        avg_temp_c=5,
        soil="sandy",
        water_level="limited",
        water_source="treated",
        previous_crops=("alfalfa",),
        priorities=("save_water",),
    )
    result = rank_rotations(brutal)
    plans = (result.recommended, *result.alternatives)
    assert all(0 <= plan.suitability <= 100 for plan in plans)

    floored = score_rotation(("alfalfa", "alfalfa", "alfalfa"), brutal)
    assert floored.suitability == 0


def test_demo_climates_change_the_first_crop():
    # Same farmer choices, three POWER climates. Iowa's hottest month sits
    # near maize. Punjab's sits on the heat-5 crops, so millet leads.
    iowa = rank_rotations(_limited_from_fixture("power_iowa.json"))
    punjab = rank_rotations(_limited_from_fixture("power_punjab.json"))
    assert iowa.recommended.rotation[0] == "maize"
    assert punjab.recommended.rotation[0] == "millet"
    assert iowa.recommended.rotation != punjab.recommended.rotation


def test_same_input_same_output():
    conditions = _limited_from_fixture("power_iowa.json", ("save_water", "improve_soil"))
    assert rank_rotations(conditions) == rank_rotations(conditions)
    assert score_rotation(("wheat", "chickpea", "barley"), GENTLE) == score_rotation(
        ("wheat", "chickpea", "barley"),
        GENTLE,
    )
