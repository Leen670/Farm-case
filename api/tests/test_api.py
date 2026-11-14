"""The clues and case endpoints, with POWER replaced by a fixture or a stub."""

import json
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app import nasa_power
from app.main import app
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

    assert body["used_fallback"] is True
    assert body["recommended"]["rotation"][0] == "maize"
    assert len(body["recommended"]["rotation"]) == 3
    assert len(body["alternatives"]) == 2
    assert 0 <= body["recommended"]["suitability"] <= 100
    assert body["explanation"].startswith("For Ada,")
    assert "saved POWER response" in body["explanation"]
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


def test_an_unsaved_pin_is_unavailable_when_power_is_down(monkeypatch):
    client = _offline(monkeypatch)
    body = dict(IOWA)
    body["lat"] = 0
    body["lon"] = 0
    response = client.post("/api/case", json=body)
    assert response.status_code == 503
