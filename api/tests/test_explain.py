"""The results paragraph repeats the ranker's numbers. No network, no model."""

from app.explain import explain_plan
from app.models import CaseRequest
from app.nasa_power import Climatology
from app.scoring import FarmConditions, score_rotation

CLIMATE = Climatology(
    latitude=42.03,
    longitude=-93.62,
    elevation_m=310.0,
    period="2001-2025",
    avg_temp_c=9.59,
    annual_max_temp_c=42.12,
    annual_max_temp_month="JUL",
    rain_mm_per_day=2.37,
    rain_mm_per_year=400.25,
    sunlight_mj_per_m2_per_day=14.52,
    humidity_percent=74.97,
    root_zone_wetness=0.51,
)


def _case(**overrides: object) -> CaseRequest:
    data = {
        "farmer_name": "Ada",
        "lat": 42.03,
        "lon": -93.62,
        "soil": "loamy",
        "water_level": "limited",
        "water_source": "rain",
    }
    data.update(overrides)
    return CaseRequest(**data)


def _plan(case: CaseRequest):
    conditions = FarmConditions(
        rain_mm=CLIMATE.rain_mm_per_year,
        max_temp_c=CLIMATE.annual_max_temp_c,
        avg_temp_c=CLIMATE.avg_temp_c,
        soil=case.soil,
        water_level=case.water_level,
        water_source=case.water_source,
        previous_crops=tuple(case.previous_crops),
        priorities=tuple(case.priorities),
    )
    return score_rotation(("wheat", "chickpea", "barley"), conditions)


def test_paragraph_quotes_the_rain_and_the_rotation():
    case = _case()
    text, evidence = explain_plan(case, _plan(case), CLIMATE, used_fallback=False)

    assert text.startswith("For Ada, the three-year rotation is wheat, chickpea, barley")
    assert "400 mm" in text
    assert "42.1°C" in text
    assert "9.6°C" in text
    assert "loamy" in text
    assert "Limited water" in text
    rain = next(row for row in evidence if row.label == "Yearly rain")
    assert rain.value == "400.25"
    assert rain.unit == "mm/year"
    assert rain.source == "NASA POWER (climatology, AG community)"


def test_wetness_is_labeled_as_power_not_smap():
    case = _case()
    text, evidence = explain_plan(case, _plan(case), CLIMATE, used_fallback=True)
    wetness = next(row for row in evidence if row.label == "Root-zone wetness")

    assert wetness.value == "0.51"
    assert wetness.unit == "0–1"
    assert wetness.source == "NASA POWER GWETROOT"
    assert "SMAP" not in wetness.source
    assert "saved POWER response" in text
    assert "wetness is shown beside the plan" in text


def test_blank_soil_is_unspecified():
    case = _case(soil=None)
    _, evidence = explain_plan(case, _plan(case), CLIMATE, used_fallback=False)
    soil = next(row for row in evidence if row.label == "Soil")
    assert soil.value == "unspecified"
    assert soil.source == "Entered by the farmer"
