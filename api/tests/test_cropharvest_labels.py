"""CropHarvest labels near the demo farms. No satellite arrays."""

import json
from pathlib import Path

import pytest

from app.cropharvest_labels import accept_download, cropland_count, named_crop_is_here

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "cropharvest_near_demos.json"


def test_a_satellite_archive_is_refused():
    accept_download("labels.geojson", 85_689_847)
    with pytest.raises(ValueError):
        accept_download("eo_data.tar.gz", 26_700_000_000)
    with pytest.raises(ValueError):
        accept_download("labels.geojson", 200_000_000)


def test_nearby_points_are_cropland_and_unnamed():
    body = json.loads(FIXTURE.read_text(encoding="utf-8"))
    expected = {"Iowa": (4, 4), "Punjab": (4, 4), "Andalusia": (6, 8)}

    for name, (crops, total) in expected.items():
        farm = body["farms"][name]
        assert cropland_count(farm["within_50km"]) == (crops, total)
        assert all(point["label"] is None for point in farm["within_50km"])
        assert named_crop_is_here(farm["nearest_named"]["km"]) is False
