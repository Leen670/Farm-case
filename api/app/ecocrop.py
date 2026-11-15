"""EcoCrop climate ranges, scored with a trapezoid.

The table is the FAO EcoCrop snapshot published by OpenCLIM:

https://github.com/OpenCLIM/ecocrop/blob/main/EcoCrop_DB.csv

Common names in that file are not UTF-8, so it is read as latin-1.
This module does not call NASA and does not rank a rotation. It only
answers how well one temperature or one rainfall total fits one crop.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import cache
from pathlib import Path

# api/data, next to this package.
_DATA = Path(__file__).resolve().parents[1] / "data" / "EcoCrop_DB.csv"

# Absolute limits, then the optimum band. Rain is an annual total, in mm.
_TEMPERATURE = ("TMIN", "TOPMN", "TOPMX", "TMAX")
_RAIN = ("RMIN", "ROPMN", "ROPMX", "RMAX")
_RANGE = _TEMPERATURE + _RAIN


def trapezoid(
    x: float,
    minimum: float,
    opt_lo: float,
    opt_hi: float,
    maximum: float,
) -> float:
    """How well one reading fits a published range, from 0 to 1.

    Outside the absolute limits the score is 0. Between the two optima it
    is 1. On each shoulder it walks in a straight line from 0 at the limit
    to 1 at the optimum. Wheat's temperature is 5, 15, 23, 27, so 19°C
    scores 1 and 10°C, halfway up the cold shoulder, scores 0.5.
    """

    if x < minimum or x > maximum:
        return 0.0
    if opt_lo <= x <= opt_hi:
        return 1.0
    if x < opt_lo:
        span = opt_lo - minimum
        return 0.0 if span == 0 else (x - minimum) / span
    span = maximum - opt_hi
    return 0.0 if span == 0 else (maximum - x) / span


@dataclass(frozen=True)
class EcoCrop:
    """One species, after blank ranges are dropped and names are deduped."""

    scientific_name: str
    common_names: tuple[str, ...]
    temp_min: float
    temp_opt_lo: float
    temp_opt_hi: float
    temp_max: float
    rain_min: float
    rain_opt_lo: float
    rain_opt_hi: float
    rain_max: float
    # Absolute soil pH. None when that cell was blank. Not part of the
    # temperature or rain score.
    ph_min: float | None = None
    ph_max: float | None = None
    # Crop cycle, in days. None when the cell was blank. The monthly
    # search uses the midpoint as the length of the growing window.
    cycle_min_days: float | None = None
    cycle_max_days: float | None = None
    # EcoCrop use-categories, lower case, split on commas.
    categories: tuple[str, ...] = ()

    def temperature(self, celsius: float) -> float:
        """Suitability of one air temperature, in degrees Celsius."""

        return trapezoid(
            celsius,
            self.temp_min,
            self.temp_opt_lo,
            self.temp_opt_hi,
            self.temp_max,
        )

    def rain(self, millimetres: float) -> float:
        """Suitability of one annual rainfall total, in millimetres."""

        return trapezoid(
            millimetres,
            self.rain_min,
            self.rain_opt_lo,
            self.rain_opt_hi,
            self.rain_max,
        )


def _number(row: dict[str, str], column: str) -> float | None:
    raw = (row.get(column) or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _common_names(text: str) -> tuple[str, ...]:
    return tuple(part.strip().lower() for part in text.split(",") if part.strip())


def _categories(text: str) -> tuple[str, ...]:
    return tuple(part.strip().lower() for part in text.split(",") if part.strip())


@cache
def load_crops() -> tuple[EcoCrop, ...]:
    """One crop per scientific name, with a complete temperature and rain range.

    A later duplicate scientific name is skipped. A row missing any of the
    eight limits is skipped too. This snapshot has neither, and the rules
    stay so a newer file cannot put a blank range into a score.
    """

    with _DATA.open(encoding="latin-1", newline="") as handle:
        rows = csv.DictReader(handle)
        kept: dict[str, EcoCrop] = {}
        for row in rows:
            name = (row.get("ScientificName") or "").strip()
            if not name or name in kept:
                continue
            numbers = [_number(row, column) for column in _RANGE]
            if any(number is None for number in numbers):
                continue
            tmin, topmn, topmx, tmax, rmin, ropmn, ropmx, rmax = (
                float(number) for number in numbers
            )
            kept[name] = EcoCrop(
                scientific_name=name,
                common_names=_common_names(row.get("COMNAME") or ""),
                temp_min=tmin,
                temp_opt_lo=topmn,
                temp_opt_hi=topmx,
                temp_max=tmax,
                rain_min=rmin,
                rain_opt_lo=ropmn,
                rain_opt_hi=ropmx,
                rain_max=rmax,
                ph_min=_number(row, "PHMIN"),
                ph_max=_number(row, "PHMAX"),
                cycle_min_days=_number(row, "GMIN"),
                cycle_max_days=_number(row, "GMAX"),
                categories=_categories(row.get("CAT") or ""),
            )
    return tuple(kept.values())


def species(scientific_name: str) -> EcoCrop:
    """The row for one scientific name, after blanks are dropped."""

    for crop in load_crops():
        if crop.scientific_name == scientific_name:
            return crop
    raise KeyError(f"Unknown EcoCrop species: {scientific_name}")


def find_crop(common_name: str) -> EcoCrop:
    """The one species whose common-name list contains this name.

    Matching is the whole name between commas, so "okra" does not select
    a crop that only says "okura".
    """

    token = common_name.strip().lower()
    matches = [crop for crop in load_crops() if token in crop.common_names]
    if len(matches) != 1:
        raise LookupError(f"{common_name!r} matches {len(matches)} EcoCrop rows")
    return matches[0]
