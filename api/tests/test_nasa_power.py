"""Parse a saved POWER response. This test does not call NASA."""

import json
from pathlib import Path

from app.nasa_power import parse_climatology

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "power_iowa.json"
DAYS = {
    "JAN": 31,
    "FEB": 28,
    "MAR": 31,
    "APR": 30,
    "MAY": 31,
    "JUN": 30,
    "JUL": 31,
    "AUG": 31,
    "SEP": 30,
    "OCT": 31,
    "NOV": 30,
    "DEC": 31,
}


def test_parse_iowa_fixture():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    parsed = parse_climatology(payload)
    series = payload["properties"]["parameter"]

    assert parsed.avg_temp_c == series["T2M"]["ANN"]
    assert parsed.annual_max_temp_c == series["T2M_MAX"]["ANN"]
    assert parsed.rain_mm_per_day == series["PRECTOTCORR"]["ANN"]
    assert parsed.sunlight_mj_per_m2_per_day == series["ALLSKY_SFC_SW_DWN"]["ANN"]
    assert parsed.humidity_percent == series["RH2M"]["ANN"]
    assert parsed.root_zone_wetness == series["GWETROOT"]["ANN"]

    hottest = max(DAYS, key=lambda month: series["T2M_MAX"][month])
    assert parsed.annual_max_temp_month == hottest

    yearly = round(sum(series["PRECTOTCORR"][month] * days for month, days in DAYS.items()), 2)
    assert parsed.rain_mm_per_year == yearly
    assert payload["parameters"]["PRECTOTCORR"]["units"] == "mm/day"


def test_missing_root_zone_wetness_keeps_the_rest_of_the_climate():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["properties"]["parameter"]["GWETROOT"]["ANN"] = -999.0
    parsed = parse_climatology(payload)
    assert parsed.root_zone_wetness is None
    assert parsed.avg_temp_c == payload["properties"]["parameter"]["T2M"]["ANN"]
    assert "root_zone_wetness" not in parsed.values()
