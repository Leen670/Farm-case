"""Snapshot links for a fixed day. This test does not call NASA."""

from datetime import date
from urllib.parse import parse_qs, urlparse

from app.gibs import (
    NAMED_ONLY,
    POWER_WETNESS_LABEL,
    WORLD_HEIGHT,
    WORLD_WIDTH,
    pixel_to_lon_lat,
    snapshots,
    world_map_url,
)
from app.nasa_power import DEMO_FARMS

DAY = date(2026, 11, 14)

EXPECTED = {
    "SMAP_L3_Passive_Enhanced_Day_Soil_Moisture": {
        "date_used": "2026-11-11",
        "fallback_date": "2026-11-08",
        "source_label": "SMAP image (NASA GIBS)",
        "max_zoom": 6,
    },
    "MODIS_Terra_NDVI_8Day": {
        "date_used": "2026-10-29",
        "fallback_date": "2026-10-13",
        "source_label": "MODIS NDVI image (NASA GIBS)",
        "max_zoom": 9,
    },
    "IMERG_Precipitation_Rate": {
        "date_used": "2026-11-12",
        "fallback_date": "2026-11-10",
        "source_label": "GPM IMERG image (NASA GIBS)",
        "max_zoom": 6,
    },
}


def test_snapshots_for_demo_farms():
    assert POWER_WETNESS_LABEL == "NASA POWER GWETROOT"
    assert NAMED_ONLY == ("Landsat", "VIIRS")

    for lat, lon in DEMO_FARMS.values():
        shots = snapshots(lat, lon, DAY)
        assert [shot["layer_id"] for shot in shots] == list(EXPECTED)
        for shot in shots:
            expected = EXPECTED[shot["layer_id"]]
            assert shot["date_used"] == expected["date_used"]
            assert shot["fallback_date"] == expected["fallback_date"]
            assert shot["source_label"] == expected["source_label"]
            assert shot["max_zoom"] == expected["max_zoom"]
            assert shot["source_label"] != POWER_WETNESS_LABEL
            _assert_box_contains_pin(shot["url"], lat, lon)
            _assert_box_contains_pin(shot["fallback_url"], lat, lon)
            assert f"TIME={shot['date_used']}" in shot["url"]
            assert f"LAYERS={shot['layer_id']}" in shot["url"]
            assert f"TIME={shot['fallback_date']}" in shot["fallback_url"]


def test_world_map_is_a_north_up_globe():
    url = world_map_url()
    query = parse_qs(urlparse(url).query)
    assert query["BBOX"] == ["-90,-180,90,180"]
    assert query["WIDTH"] == [str(WORLD_WIDTH)]
    assert query["HEIGHT"] == [str(WORLD_HEIGHT)]
    assert query["LAYERS"] == ["BlueMarble_NextGeneration"]
    assert query["CRS"] == ["EPSG:4326"]
    assert query["FORMAT"] == ["image/jpeg"]
    assert "-180,-90,180,90" not in url

    assert pixel_to_lon_lat(0, 0, WORLD_WIDTH, WORLD_HEIGHT) == (-180.0, 90.0)
    assert pixel_to_lon_lat(WORLD_WIDTH, WORLD_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT) == (180.0, -90.0)
    assert pixel_to_lon_lat(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, WORLD_WIDTH, WORLD_HEIGHT) == (0.0, 0.0)


def _assert_box_contains_pin(url: str, lat: float, lon: float) -> None:
    query = parse_qs(urlparse(url).query)
    south, west, north, east = (float(part) for part in query["BBOX"][0].split(","))
    assert south <= lat <= north
    assert west <= lon <= east
    assert query["CRS"] == ["EPSG:4326"]
