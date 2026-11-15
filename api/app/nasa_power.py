"""NASA POWER climatology client.

Verified against the climatology point docs and a live AG-community request
on 14 Nov 2026. All six parameter names came back, with units in the body:

https://power.larc.nasa.gov/docs/services/api/temporal/climatology/

T2M and RH2M annual values are means. PRECTOTCORR is millimetres per day,
not per year. T2M_MAX keeps the extreme rather than the average daily high:
https://power.larc.nasa.gov/docs/methodology/data/processing/
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

import httpx

CLIMATOLOGY_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
COMMUNITY = "AG"
PARAMETERS = (
    "T2M",
    "T2M_MAX",
    "PRECTOTCORR",
    "ALLSKY_SFC_SW_DWN",
    "RH2M",
    "GWETROOT",
)
FILL_VALUE = -999.0
MONTHS = (
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
)
# A non-leap year. POWER's ANN rain value is a daily rate, so a yearly total
# has to be rebuilt from the monthly rates.
DAYS_IN_MONTH = {
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
SOURCE = "NASA POWER (climatology, AG community)"
SOURCE_URL = "https://power.larc.nasa.gov/"

# Three climates on three continents. West longitudes are negative.
DEMO_FARMS = {
    "iowa": (42.03, -93.62),
    "punjab": (30.90, 75.85),
    "andalusia": (37.88, -4.78),
}

API_DIR = Path(__file__).resolve().parents[1]
FIXTURE_DIR = API_DIR / "fixtures"
CACHE_DIR = API_DIR / ".power_cache"


class PowerError(RuntimeError):
    """POWER answered, but the body is not a climatology we can use."""


def cache_key(lat: float, lon: float) -> tuple[float, float]:
    """Round to the nearest 0.5 degree, which is POWER's regional grid size.

    42.03 becomes 42.0. -93.62 becomes -93.5. Exact halves stay put.
    """
    return (round(lat * 2) / 2, round(lon * 2) / 2)


def _cache_path(key: tuple[float, float]) -> Path:
    lat, lon = key
    return CACHE_DIR / f"{lat:+.1f}_{lon:+.1f}.json"


class PowerCache:
    """Remember one POWER response per 0.5 degree cell, in memory and on disk."""

    def __init__(self) -> None:
        self._memory: dict[tuple[float, float], dict] = {}

    def get(self, lat: float, lon: float) -> dict | None:
        key = cache_key(lat, lon)
        if key in self._memory:
            return self._memory[key]
        path = _cache_path(key)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        self._memory[key] = payload
        return payload

    def put(self, lat: float, lon: float, payload: dict) -> None:
        key = cache_key(lat, lon)
        self._memory[key] = payload
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _cache_path(key).write_text(json.dumps(payload), encoding="utf-8")


cache = PowerCache()


async def fetch_climatology(
    lat: float,
    lon: float,
    *,
    client: httpx.AsyncClient | None = None,
    store: PowerCache | None = None,
) -> dict:
    """Return the raw POWER climatology for this point, using the cache first.

    The request uses the pin the player chose. The cache key is the surrounding
    0.5 degree cell, so a second pin in that cell reuses the first response.
    """
    store = cache if store is None else store
    cached = store.get(lat, lon)
    if cached is not None and _usable(cached):
        return cached

    owns_client = client is None
    if client is None:
        client = httpx.AsyncClient(
            timeout=60,
            headers={"User-Agent": "farm-case/0.1 (NASA Space Apps; educational)"},
        )
    try:
        response = await client.get(
            CLIMATOLOGY_URL,
            params={
                "parameters": ",".join(PARAMETERS),
                "community": COMMUNITY,
                "latitude": lat,
                "longitude": lon,
                "format": "JSON",
            },
        )
        response.raise_for_status()
        payload = response.json()
    finally:
        if owns_client:
            await client.aclose()

    missing = [name for name in PARAMETERS if name not in payload.get("properties", {}).get("parameter", {})]
    if missing:
        raise PowerError(f"POWER response is missing {', '.join(missing)}")
    if not _usable(payload):
        raise PowerError("POWER has no climate values for this point")
    store.put(lat, lon, payload)
    return payload


@dataclass(frozen=True)
class Climatology:
    """The numbers the climate and water clues are allowed to show."""

    latitude: float
    longitude: float
    elevation_m: float
    period: str
    avg_temp_c: float
    annual_max_temp_c: float
    annual_max_temp_month: str
    rain_mm_per_day: float
    rain_mm_per_year: float
    sunlight_mj_per_m2_per_day: float
    humidity_percent: float
    root_zone_wetness: float | None

    def values(self) -> dict[str, float | str]:
        numbers: dict[str, float | str] = {
            "avg_temp_c": self.avg_temp_c,
            "annual_max_temp_c": self.annual_max_temp_c,
            "annual_max_temp_month": self.annual_max_temp_month,
            "rain_mm_per_day": self.rain_mm_per_day,
            "rain_mm_per_year": self.rain_mm_per_year,
            "sunlight_mj_per_m2_per_day": self.sunlight_mj_per_m2_per_day,
            "humidity_percent": self.humidity_percent,
        }
        if self.root_zone_wetness is not None:
            numbers["root_zone_wetness"] = self.root_zone_wetness
        return numbers


def _annual(payload: dict, name: str) -> float:
    value = _raw_annual(payload, name)
    if value == FILL_VALUE:
        raise PowerError(f"POWER has no {name} value for this point")
    return float(value)


def _optional_annual(payload: dict, name: str) -> float | None:
    """None when POWER's fill value is the only annual number.

    Root-zone wetness is empty over open water. Temperature and rain are not,
    so a missing wetness reading must not throw away the rest of the climate.
    """

    value = _raw_annual(payload, name)
    if value == FILL_VALUE:
        return None
    return float(value)


def _raw_annual(payload: dict, name: str) -> float:
    return float(payload["properties"]["parameter"][name]["ANN"])


def rain_mm_per_year(monthly_mm_per_day: dict[str, float]) -> float:
    """Turn twelve daily rates into a 365-day total."""
    total = sum(monthly_mm_per_day[month] * DAYS_IN_MONTH[month] for month in MONTHS)
    return round(total, 2)


def _usable(payload: dict) -> bool:
    """True when the body has real climate numbers, not POWER's fill value."""

    try:
        parse_climatology(payload)
    except (PowerError, KeyError, TypeError, ValueError):
        return False
    return True


def parse_climatology(payload: dict) -> Climatology:
    """Read a POWER climatology body. This does not call the network."""
    series = payload["properties"]["parameter"]
    maximums = series["T2M_MAX"]
    hottest = max(MONTHS, key=lambda month: maximums[month])
    lon, lat, elevation = payload["geometry"]["coordinates"]
    return Climatology(
        latitude=float(lat),
        longitude=float(lon),
        elevation_m=float(elevation),
        period=str(payload["header"]["range"]),
        avg_temp_c=_annual(payload, "T2M"),
        annual_max_temp_c=_annual(payload, "T2M_MAX"),
        annual_max_temp_month=hottest,
        rain_mm_per_day=_annual(payload, "PRECTOTCORR"),
        rain_mm_per_year=rain_mm_per_year(series["PRECTOTCORR"]),
        sunlight_mj_per_m2_per_day=_annual(payload, "ALLSKY_SFC_SW_DWN"),
        humidity_percent=_annual(payload, "RH2M"),
        root_zone_wetness=_optional_annual(payload, "GWETROOT"),
    )


async def save_demo_fixtures(directory: Path = FIXTURE_DIR) -> None:
    """Fetch the three demo farms and write the raw POWER bodies to disk."""
    directory.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(
        timeout=60,
        headers={"User-Agent": "farm-case/0.1 (NASA Space Apps; educational)"},
    ) as client:
        for name, (lat, lon) in DEMO_FARMS.items():
            payload = await fetch_climatology(lat, lon, client=client)
            path = directory / f"power_{name}.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(f"wrote {path.name}")


def main() -> None:
    asyncio.run(save_demo_fixtures())


if __name__ == "__main__":
    main()
