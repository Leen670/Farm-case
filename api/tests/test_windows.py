"""The wider search scores a crop on the months it grows, not the hottest month."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.ecocrop import find_crop
from app.main import app
from app.nasa_power import MONTHS
from app.windows import MonthlyClimate, average_years, from_climatology, rank_windows

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "power_iowa.json"


def _climate() -> MonthlyClimate:
    # Six cold months, then six warm months. Rain rises with the heat.
    return MonthlyClimate(
        period="example",
        temp_c=(0, 2, 8, 14, 20, 28, 30, 29, 22, 14, 6, 1),
        rain_mm_per_day=(1, 1, 1, 2, 3, 4, 4, 3, 2, 2, 1, 1),
    )


def _window_temp(climate: MonthlyClimate, start: str, length: int) -> float:
    start_index = MONTHS.index(start)
    indexes = [(start_index + step) % 12 for step in range(length)]
    from app.nasa_power import DAYS_IN_MONTH

    chosen = [DAYS_IN_MONTH[MONTHS[index]] for index in indexes]
    return sum(climate.temp_c[index] * day for index, day in zip(indexes, chosen)) / sum(chosen)


def test_maize_takes_a_warmer_window_than_wheat():
    climate = _climate()
    fits = {item.scientific_name: item for item in rank_windows(climate, limit=3000)}
    # The parent row Zea mays has a blank category, so the farm search
    # uses the subspecies that EcoCrop marks as a cereal.
    maize = fits["Zea mays ssp. mays"]
    wheat = fits["Triticum aestivum"]

    assert _window_temp(climate, maize.start_month, maize.length_months) > _window_temp(
        climate, wheat.start_month, wheat.length_months
    )
    assert 0 <= maize.score <= 1
    assert find_crop("maize").cycle_min_days is not None


def test_iowa_maize_survives_the_july_mean():
    # The game scores maize on the 42°C extreme and it collapses.
    # July's mean is inside EcoCrop's optimum, so the window keeps it.
    climate = from_climatology(json.loads(FIXTURE.read_text(encoding="utf-8")))
    fits = {item.scientific_name: item for item in rank_windows(climate, limit=3000)}
    maize = fits["Zea mays ssp. mays"]

    assert maize.score > 0
    assert maize.start_month in {"APR", "MAY", "JUN", "JUL"}


def test_a_two_year_series_averages_each_month():
    payload = {
        "properties": {
            "parameter": {
                "T2M": {"200101": 0, "200201": 10, "200107": 20, "200207": 30},
                "PRECTOTCORR": {"200101": 1, "200201": 3, "200107": 4, "200207": 6},
            }
        }
    }
    # The other ten months need a value or average_years refuses them.
    for month in range(2, 7):
        for year in (2001, 2002):
            payload["properties"]["parameter"]["T2M"][f"{year}{month:02d}"] = 15
            payload["properties"]["parameter"]["PRECTOTCORR"][f"{year}{month:02d}"] = 2
    for month in range(8, 13):
        for year in (2001, 2002):
            payload["properties"]["parameter"]["T2M"][f"{year}{month:02d}"] = 15
            payload["properties"]["parameter"]["PRECTOTCORR"][f"{year}{month:02d}"] = 2

    climate = average_years(payload, "2001-2002")

    assert climate.temp_c[0] == 5
    assert climate.rain_mm_per_day[0] == 2
    assert climate.temp_c[6] == 25
    assert climate.period == "2001-2002"


def test_windows_route_returns_five_scores(monkeypatch):
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

    async def saved(*args, **kwargs):
        return payload

    monkeypatch.setattr("app.analysis.nasa_power.fetch_climatology", saved)
    response = TestClient(app).post("/api/windows", json={"lat": 42.03, "lon": -93.62})

    assert response.status_code == 200
    body = response.json()
    assert len(body["top"]) == 5
    assert all(0 <= row["score"] <= 100 for row in body["top"])
    assert body["top"][0]["scientific_name"] == "Phaseolus vulgaris"
    assert body["earlier_period"] == "2001-2020"
    assert body["earlier_top"][0]["scientific_name"] == "Phaseolus vulgaris"
    assert body["leader_changed"] is False
