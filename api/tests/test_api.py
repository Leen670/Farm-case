"""The clues and case endpoints, with POWER replaced by a fixture or a stub."""

import json
import re
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app import nasa_power
from app.main import BROWSER_ORIGIN_PATTERN, app, cors_settings
from app.nasa_power import parse_climatology

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "power_iowa.json"
IOWA = {
    "farmer_name": "Ada",
    "lat": 42.03,
    "lon": -93.62,
    "soil": "loamy",
    "water_level": "limited",
    "water_source": "rain",
}


def _offline(monkeypatch) -> TestClient:
    monkeypatch.setattr(nasa_power.cache, "get", lambda lat, lon: None)

    async def boom(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(nasa_power, "fetch_climatology", boom)
    return TestClient(app)


def test_open_cors_is_the_default(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    origins, pattern = cors_settings()
    assert origins == ["*"]
    assert pattern is None


def test_cors_keeps_local_dev_and_any_vercel_site(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://farm-case.vercel.app")
    origins, pattern = cors_settings()
    assert "https://farm-case.vercel.app" in origins
    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:5173" in origins
    assert "https://html-classic.itch.zone" in origins
    assert "https://html.itch.zone" in origins
    assert pattern == BROWSER_ORIGIN_PATTERN
    assert re.fullmatch(pattern, "https://kadi.itch.io")
    assert re.fullmatch(pattern, "https://farm-case.vercel.app")
    assert re.fullmatch(pattern, "https://evil.example") is None
    assert re.fullmatch(pattern, "https://evilitch.io") is None


def test_docs_list_both_posts():
    client = TestClient(app)
    docs = client.get("/docs")
    schema = client.get("/openapi.json")
    assert docs.status_code == 200
    assert schema.status_code == 200
    paths = schema.json()["paths"]
    assert "post" in paths["/api/clues"]
    assert "post" in paths["/api/case"]


def test_clues_use_the_fixture_and_the_farmers_soil(monkeypatch):
    client = _offline(monkeypatch)
    response = client.post("/api/clues", json=IOWA)
    assert response.status_code == 200
    clues = {clue["id"]: clue for clue in response.json()["clues"]}

    climate = parse_climatology(json.loads(FIXTURE.read_text(encoding="utf-8")))
    assert clues["climate"]["values"]["avg_temp_c"] == climate.avg_temp_c
    assert clues["climate"]["values"]["rain_mm_per_year"] == climate.rain_mm_per_year
    assert clues["climate"]["source"] == nasa_power.SOURCE
    assert "IMERG_Precipitation_Rate" in clues["climate"]["image_url"]

    assert clues["soil"]["values"]["soil"] == "loamy"
    assert clues["soil"]["source"] == "Entered by the farmer"
    assert clues["soil"]["image_url"] is None

    assert clues["water"]["values"]["root_zone_wetness"] == climate.root_zone_wetness
    assert clues["water"]["values"]["wetness_label"] == "NASA POWER GWETROOT"
    assert "SMAP_L3_Passive_Enhanced_Day_Soil_Moisture" in clues["water"]["image_url"]

    crop = clues["crop"]
    assert crop["source"] == "MODIS NDVI image (NASA GIBS)"
    assert "MODIS_Terra_NDVI_8Day" in crop["image_url"]
    assert "Landsat" in crop["summary"] and "VIIRS" in crop["summary"]


def test_blank_soil_stays_unspecified(monkeypatch):
    client = _offline(monkeypatch)
    body = dict(IOWA)
    body["soil"] = None
    response = client.post("/api/clues", json=body)
    assert response.status_code == 200
    soil = next(clue for clue in response.json()["clues"] if clue["id"] == "soil")
    assert soil["values"]["soil"] == "unspecified"


def test_case_ranks_from_the_fixture_and_flags_it(monkeypatch):
    client = _offline(monkeypatch)
    response = client.post("/api/case", json=IOWA)
    assert response.status_code == 200
    body = response.json()

    climate = parse_climatology(json.loads(FIXTURE.read_text(encoding="utf-8")))
    assert body["used_fallback"] is True
    assert body["recommended"]["rotation"][0] == "maize"
    assert len(body["recommended"]["rotation"]) == 3
    assert len(body["alternatives"]) == 2
    assert 0 <= body["recommended"]["suitability"] <= 100
    assert body["explanation"].startswith("For Ada,")
    assert "saved POWER response" in body["explanation"]
    assert "maize" in body["explanation"]
    rain = next(row for row in body["evidence"] if row["label"] == "Yearly rain")
    assert rain["value"] == f"{climate.rain_mm_per_year:.2f}"
    assert rain["unit"] == "mm/year"
    assert rain["source"] == "NASA POWER (climatology, AG community)"
    wetness = next(row for row in body["evidence"] if row["label"] == "Root-zone wetness")
    assert wetness["source"] == "NASA POWER GWETROOT"
    assert len(body["clues"]) == 4


def test_a_fresh_power_response_is_not_a_fallback(monkeypatch):
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    monkeypatch.setattr(nasa_power.cache, "get", lambda lat, lon: None)

    async def live(*args, **kwargs):
        return payload

    monkeypatch.setattr(nasa_power, "fetch_climatology", live)
    response = TestClient(app).post("/api/case", json=IOWA)
    assert response.status_code == 200
    assert response.json()["used_fallback"] is False


def _assert_jsonutility(value):
    """Unity's reader accepts objects, arrays, strings, numbers, and bools."""

    assert value is not None
    if isinstance(value, dict):
        for item in value.values():
            _assert_jsonutility(item)
    elif isinstance(value, list):
        for item in value:
            _assert_jsonutility(item)
    else:
        assert isinstance(value, (str, int, bool))


def test_simple_case_is_display_ready(monkeypatch):
    client = _offline(monkeypatch)
    response = client.post("/api/case/simple", json=IOWA)
    assert response.status_code == 200
    assert "null" not in response.text
    body = response.json()
    _assert_jsonutility(body)

    assert body["title"] == "Ada's case"
    assert body["demo_data"] is True
    assert [clue["name"] for clue in body["clues"]] == ["Climate", "Soil", "Water", "Crop"]
    assert all(isinstance(clue["image_url"], str) for clue in body["clues"])
    assert body["clues"][1]["image_url"] == ""
    assert "MODIS_Terra_NDVI_8Day" in body["clues"][3]["image_url"]

    recommended = body["recommended"]
    assert recommended["crops"] == ["maize", "faba bean", "maize"]
    assert isinstance(recommended["score"], int)
    assert recommended["why"] and recommended["risks"]
    assert len(body["alternatives"]) == 2
    assert all(len(plan["crops"]) == 3 for plan in body["alternatives"])


def test_docs_list_the_unity_route():
    schema = TestClient(app).get("/openapi.json").json()
    assert "post" in schema["paths"]["/api/case/simple"]
    assert "get" in schema["paths"]["/api/world-map"]
    assert "get" in schema["paths"]["/api/image"]


def test_a_fill_value_pin_is_unavailable_instead_of_crashing(monkeypatch):
    fill = {
        "properties": {"parameter": {}},
        "geometry": {"coordinates": [0, 0, 0]},
        "header": {"range": ""},
    }
    monkeypatch.setattr(nasa_power.cache, "get", lambda lat, lon: fill)

    async def boom(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(nasa_power, "fetch_climatology", boom)
    body = dict(IOWA)
    body["lat"] = 0
    body["lon"] = 0
    response = TestClient(app).post("/api/case/simple", json=body)
    assert response.status_code == 503


def test_an_unsaved_pin_is_unavailable_when_power_is_down(monkeypatch):
    client = _offline(monkeypatch)
    body = dict(IOWA)
    body["lat"] = 0
    body["lon"] = 0
    response = client.post("/api/case", json=body)
    assert response.status_code == 503
