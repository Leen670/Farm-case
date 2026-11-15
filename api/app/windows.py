"""Score the EcoCrop table on each crop's own growing months.

The 15-crop game is a different search. This one reads every EcoCrop row
that has a temperature and a rain range. EcoCrop states those rain limits
for a full year, so a shorter crop is judged on a window of its cycle
length and the limits are scaled to that many days. The window slides
around the twelve months. The score is the worse of temperature and rain,
the limiting factor in the EcoCrop method. The best window is kept.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from app.ecocrop import EcoCrop, load_crops, trapezoid
from app.nasa_power import DAYS_IN_MONTH, DEMO_FARMS, FIXTURE_DIR, MONTHS

_YEAR_DAYS = 365
_TOP = 5
# A farm search. Forest, ornamentals, weeds, and medicinals stay in the
# file and out of this list. A row with no category is left out too.
CULTIVATED = frozenset(
    {
        "cereals & pseudocereals",
        "pulses (grain legumes)",
        "vegetables",
        "roots/tubers",
        "fruits & nuts",
        "forage/pasture",
        "materials",
    }
)


@dataclass(frozen=True)
class MonthlyClimate:
    """Twelve monthly normals. Temperature is °C. Rain is millimetres per day."""

    period: str
    temp_c: tuple[float, ...]
    rain_mm_per_day: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.temp_c) != 12 or len(self.rain_mm_per_day) != 12:
            raise ValueError("a year has 12 months")


@dataclass(frozen=True)
class WindowFit:
    """One species, the month its best window starts, and a 0–1 score.

    closeness is how far the window sits from the middle of the optimum.
    It only orders crops that already share a score.
    """

    scientific_name: str
    common_name: str
    score: float
    start_month: str
    length_months: int
    closeness: float


def from_climatology(payload: dict) -> MonthlyClimate:
    """Read the twelve monthly normals already inside a POWER climatology."""

    series = payload["properties"]["parameter"]
    return MonthlyClimate(
        period=str(payload["header"]["range"]),
        temp_c=tuple(float(series["T2M"][month]) for month in MONTHS),
        rain_mm_per_day=tuple(float(series["PRECTOTCORR"][month]) for month in MONTHS),
    )


def average_years(payload: dict, period: str) -> MonthlyClimate:
    """Collapse a POWER monthly time series into twelve means.

    Keys look like 200101. A fill value of -999 is left out of that month.
    """

    parameters = payload["properties"]["parameter"]
    temps: list[float] = []
    rains: list[float] = []
    for index, _month in enumerate(MONTHS, start=1):
        suffix = f"{index:02d}"
        temp_values = [
            float(value)
            for key, value in parameters["T2M"].items()
            if key.endswith(suffix) and float(value) != -999
        ]
        rain_values = [
            float(value)
            for key, value in parameters["PRECTOTCORR"].items()
            if key.endswith(suffix) and float(value) != -999
        ]
        if not temp_values or not rain_values:
            raise ValueError(f"no values for month {suffix}")
        temps.append(sum(temp_values) / len(temp_values))
        rains.append(sum(rain_values) / len(rain_values))
    return MonthlyClimate(period, tuple(temps), tuple(rains))


def cycle_months(crop: EcoCrop) -> int:
    """How many months the window covers. A blank cycle is the whole year."""

    if crop.cycle_min_days is None or crop.cycle_max_days is None:
        return 12
    days = (crop.cycle_min_days + crop.cycle_max_days) / 2
    if days <= 0:
        return 12
    months = round(days / (_YEAR_DAYS / 12))
    return min(12, max(1, months))


def rank_windows(climate: MonthlyClimate, limit: int = _TOP) -> tuple[WindowFit, ...]:
    """Cultivated species, highest score first, then closest to the optimum."""

    ranked = [_fit(crop, climate) for crop in load_crops() if _cultivated(crop)]
    ranked.sort(key=lambda item: (-round(item.score, 6), round(item.closeness, 6), item.scientific_name))
    return tuple(ranked[:limit])


def leader_changed(current: MonthlyClimate, earlier: MonthlyClimate) -> bool:
    """True when the single best species is not the same in both periods."""

    return rank_windows(current, 1)[0].scientific_name != rank_windows(earlier, 1)[0].scientific_name


def earlier_climate(lat: float, lon: float) -> MonthlyClimate | None:
    """The saved 2001–2020 normals for a demo pin, if this pin is one of them."""

    for name, (farm_lat, farm_lon) in DEMO_FARMS.items():
        if abs(lat - farm_lat) > 0.02 or abs(lon - farm_lon) > 0.02:
            continue
        path = FIXTURE_DIR / f"window_2001_2020_{name}.json"
        if not path.is_file():
            return None
        body = json.loads(path.read_text(encoding="utf-8"))
        return MonthlyClimate(
            period=str(body["period"]),
            temp_c=tuple(float(body["T2M"][month]) for month in MONTHS),
            rain_mm_per_day=tuple(float(body["PRECTOTCORR"][month]) for month in MONTHS),
        )
    return None


def _cultivated(crop: EcoCrop) -> bool:
    return bool(set(crop.categories) & CULTIVATED)


def _fit(crop: EcoCrop, climate: MonthlyClimate) -> WindowFit:
    length = cycle_months(crop)
    best: tuple[float, float, int] | None = None
    for start in range(12):
        score, closeness = _window_score(crop, climate, start, length)
        if best is None or score > best[0] or (score == best[0] and closeness < best[1]):
            best = (score, closeness, start)
    assert best is not None
    common = crop.common_names[0] if crop.common_names else crop.scientific_name
    return WindowFit(crop.scientific_name, common, best[0], MONTHS[best[2]], length, best[1])


def _window_score(crop: EcoCrop, climate: MonthlyClimate, start: int, length: int) -> tuple[float, float]:
    indexes = [(start + step) % 12 for step in range(length)]
    days = [DAYS_IN_MONTH[MONTHS[index]] for index in indexes]
    day_total = sum(days)
    temp = sum(climate.temp_c[index] * day for index, day in zip(indexes, days)) / day_total
    rain = sum(climate.rain_mm_per_day[index] * day for index, day in zip(indexes, days))
    scale = day_total / _YEAR_DAYS
    temperature = trapezoid(
        temp,
        crop.temp_min,
        crop.temp_opt_lo,
        crop.temp_opt_hi,
        crop.temp_max,
    )
    rainfall = trapezoid(
        rain,
        crop.rain_min * scale,
        crop.rain_opt_lo * scale,
        crop.rain_opt_hi * scale,
        crop.rain_max * scale,
    )
    closeness = _gap(temp, crop.temp_opt_lo, crop.temp_opt_hi) + _gap(
        rain,
        crop.rain_opt_lo * scale,
        crop.rain_opt_hi * scale,
    )
    return min(temperature, rainfall), closeness


def _gap(value: float, opt_lo: float, opt_hi: float) -> float:
    middle = (opt_lo + opt_hi) / 2
    half = (opt_hi - opt_lo) / 2
    if half == 0:
        return abs(value - middle)
    return abs(value - middle) / half
