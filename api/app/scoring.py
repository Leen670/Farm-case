"""Suitability of one crop, then a ranked 3-year rotation.

The formula is plain arithmetic so a test can pin every bonus. NASA data
enters as numbers the caller already has: yearly rain and temperatures from
POWER. This module does not call NASA, and it does not ask a model to pick
the crops.

One crop is scored 0–100 from four fits (water, heat, soil, salinity).
A rotation is the average of its three crops, plus the brief's bonuses and
penalties. The printed score is capped at 0–100. Sorting uses the total
before that cap, so a +10 still beats a tie that would otherwise print 100.
Equal totals then prefer three different crop names, then A to Z.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import get_args

from app.crops import CROPS, Crop, find_crop, get_crop
from app.ecocrop import trapezoid
from app.models import Priority, Soil, WaterLevel, WaterSource

# POWER's yearly rain, plus how much irrigation the farmer said they can add.
# The allowance is a game assumption. POWER does not report water rights.
IRRIGATION_ALLOWANCE_MM = {
    "available": 600,
    "moderate": 250,
    "limited": 0,
}

# Alfalfa is 1200 mm, cotton 1000, sunflower 800. Millet and the pulses sit
# under this line, so limited water hits the heavy users and leaves the rest.
HIGH_WATER_NEED_MM = 700
LIMITED_WATER_FACTOR = 0.25

# Winter crops are judged on the annual mean. They grow in the cool months.
# Summer crops are judged on T2M_MAX, which is the hottest month, not a
# daily average.
# A crop short of the heat this site needs loses 30 points per level.
# A crop tougher than the site needs loses 8 per extra level, so two crops
# that can both survive still sort by which one matches the temperature.
HEAT_SHORTFALL_STEP = 30
HEAT_OVERSHOOT_STEP = 8
SALT_STEP = 25

SOIL_MATCH = 100.0
SOIL_UNKNOWN = 70.0
SOIL_MISS = 45.0
PH_OUTSIDE_FACTOR = 0.75
WEAK_FIT = 70

# Weights are integers out of a starting 100, then a priority adds to one
# term and the four are divided by their new total. Save water and lower
# cost both raise water: lower cost stands in for the irrigation bill, which
# is the cost this table can actually see. Increase yield raises heat and
# soil. Improve soil raises the soil weight and, separately, the rotation bonus.
BASE_WEIGHTS = {"water": 40, "heat": 25, "soil": 20, "salinity": 15}

# How salty we treat each source, on the same 1–5 scale as the crop table.
# Desalinated water is fresh, so it only stresses a sensitive crop. Treated
# water is the salty end. Ground water often is too.
SALT_STRESS = {
    "rain": 1,
    "surface": 2,
    "desalinated": 2,
    "ground": 4,
    "treated": 5,
}

LEGUME_BONUS = 10
LEGUME_BONUS_IMPROVE_SOIL = 15
STRUCTURE_BONUS = 5
SAME_FAMILY_PENALTY = 15
REPEAT_PENALTY = 10

TERMS = ("water", "heat", "soil", "salinity")
WATER_LEVELS = get_args(WaterLevel)
WATER_SOURCES = get_args(WaterSource)
SOILS = get_args(Soil)
PRIORITIES = get_args(Priority)


@dataclass(frozen=True)
class FarmConditions:
    """The farm facts the ranker needs. Climate numbers come from POWER."""

    rain_mm: float
    max_temp_c: float
    avg_temp_c: float
    soil: str | None
    water_level: str
    water_source: str
    previous_crops: tuple[str, ...] = ()
    priorities: tuple[str, ...] = ()
    soil_ph: float | None = None

    def __post_init__(self) -> None:
        if self.water_level not in WATER_LEVELS:
            raise ValueError(f"water_level must be one of {WATER_LEVELS}")
        if self.water_source not in WATER_SOURCES:
            raise ValueError(f"water_source must be one of {WATER_SOURCES}")
        if self.soil is not None and self.soil not in SOILS:
            raise ValueError(f"soil must be one of {SOILS}")
        unknown = set(self.priorities) - set(PRIORITIES)
        if unknown:
            raise ValueError(f"unknown priorities: {sorted(unknown)}")
        object.__setattr__(self, "previous_crops", tuple(self.previous_crops))
        object.__setattr__(self, "priorities", tuple(self.priorities))


@dataclass(frozen=True)
class CropFit:
    """The four terms and their weighted total, each on a 0–100 scale."""

    water: float
    heat: float
    soil: float
    salinity: float
    total: float

    def as_terms(self) -> dict[str, float]:
        return {
            "water": self.water,
            "heat": self.heat,
            "soil": self.soil,
            "salinity": self.salinity,
        }


@dataclass(frozen=True)
class Note:
    points: int
    text: str


@dataclass(frozen=True)
class RotationDelta:
    points: int
    notes: tuple[Note, ...]


@dataclass(frozen=True)
class ScoredRotation:
    """One 3-year plan. suitability is the capped score the screen prints."""

    rotation: tuple[str, str, str]
    suitability: int
    reasons: tuple[str, ...]
    risks: tuple[str, ...]


@dataclass(frozen=True)
class Recommendation:
    """The winning plan and the two runners-up."""

    recommended: ScoredRotation
    alternatives: tuple[ScoredRotation, ScoredRotation]


def fit_weights(priorities: tuple[str, ...]) -> dict[str, float]:
    """Turn the checked priorities into four weights that add up to 1."""

    weights = dict(BASE_WEIGHTS)
    chosen = set(priorities)
    if "save_water" in chosen:
        weights["water"] += 20
    if "lower_cost" in chosen:
        weights["water"] += 10
    if "increase_yield" in chosen:
        weights["heat"] += 15
        weights["soil"] += 10
    if "improve_soil" in chosen:
        weights["soil"] += 10
    total = float(sum(weights.values()))
    return {name: value / total for name, value in weights.items()}


def _bound(value: float) -> float:
    return min(100.0, max(0.0, value))


def water_fit(crop: Crop, conditions: FarmConditions) -> float:
    """Seasonal need against yearly rain plus the irrigation allowance.

    Yearly rain is larger than the rain that falls inside one season. The
    brief compares the crop's seasonal need with POWER's rain total, so this
    version does that. A later pass can switch the rain to the growing months.
    """

    supply = conditions.rain_mm + IRRIGATION_ALLOWANCE_MM[conditions.water_level]
    fit = _bound(100.0 * supply / crop.water_need_mm)
    if conditions.water_level == "limited" and crop.water_need_mm >= HIGH_WATER_NEED_MM:
        fit *= LIMITED_WATER_FACTOR
    return fit


def _required_heat(temp_c: float) -> float:
    """Place a winter temperature on the same 1–5 scale as heat_tolerance.

    17°C is 1. Each further 8°C asks for one more level. Summer crops do
    not use this scale. Their heat comes from the EcoCrop trapezoid.
    """

    return min(5.0, max(1.0, (temp_c - 9) / 8))


def heat_fit(crop: Crop, conditions: FarmConditions) -> float:
    """Summer heat is the EcoCrop trapezoid on the hottest month.

    Winter crops stay on the 1–5 scale and the annual mean. A winter
    grain's EcoCrop maximum is the temperature that stops it in summer,
    so scoring it on the hottest month would zero it on a hot farm.
    """

    if crop.season == "summer":
        suitability = trapezoid(
            conditions.max_temp_c,
            crop.temp_min,
            crop.temp_opt_lo,
            crop.temp_opt_hi,
            crop.temp_max,
        )
        return _bound(100.0 * suitability)
    gap = crop.heat_tolerance - _required_heat(conditions.avg_temp_c)
    if gap >= 0:
        return _bound(100.0 - gap * HEAT_OVERSHOOT_STEP)
    return _bound(100.0 - (-gap) * HEAT_SHORTFALL_STEP)


def soil_fit(crop: Crop, conditions: FarmConditions) -> float:
    if conditions.soil is None:
        fit = SOIL_UNKNOWN
    elif conditions.soil in crop.soil_pref:
        fit = SOIL_MATCH
    else:
        fit = SOIL_MISS
    if conditions.soil_ph is not None and not (crop.ph_min <= conditions.soil_ph <= crop.ph_max):
        fit *= PH_OUTSIDE_FACTOR
    return fit


def salinity_fit(crop: Crop, conditions: FarmConditions) -> float:
    gap = SALT_STRESS[conditions.water_source] - crop.salt_tolerance
    if gap <= 0:
        return 100.0
    return _bound(100.0 - gap * SALT_STEP)


def crop_fit(crop: Crop, conditions: FarmConditions) -> CropFit:
    """Weighted sum of the four fits. The result stays on 0–100."""

    parts = {
        "water": water_fit(crop, conditions),
        "heat": heat_fit(crop, conditions),
        "soil": soil_fit(crop, conditions),
        "salinity": salinity_fit(crop, conditions),
    }
    weights = fit_weights(conditions.priorities)
    total = sum(parts[name] * weights[name] for name in TERMS)
    return CropFit(
        water=parts["water"],
        heat=parts["heat"],
        soil=parts["soil"],
        salinity=parts["salinity"],
        total=total,
    )


def fixes_nitrogen(crop: Crop) -> bool:
    """Pulses, and alfalfa, which is filed under forage but still fixes nitrogen."""

    return crop.family == "legume" or crop.soil_effect == "nitrogen"


def rotation_delta(crops: tuple[Crop, Crop, Crop], conditions: FarmConditions) -> RotationDelta:
    """Bonuses and penalties for a sequence, including the farmer's last crop.

    The last name in previous_crops is the year before year 1. An unknown
    name is skipped. Planting that same crop again in any of the three years
    is −10 each time, and an adjacent same-family pair is also −15.
    """

    previous = None
    if conditions.previous_crops:
        previous = find_crop(conditions.previous_crops[-1])
    improve_soil = "improve_soil" in conditions.priorities
    notes: list[Note] = []

    sequence: list[Crop | None] = [previous, crops[0], crops[1], crops[2]]
    for before, after in zip(sequence, sequence[1:]):
        if before is None:
            continue
        if before.family == "cereal" and fixes_nitrogen(after):
            bonus = LEGUME_BONUS_IMPROVE_SOIL if improve_soil else LEGUME_BONUS
            notes.append(
                Note(
                    bonus,
                    f"{after.name} follows {before.name}, nitrogen crop after a cereal, +{bonus}",
                )
            )
        if before.family == after.family:
            notes.append(
                Note(
                    -SAME_FAMILY_PENALTY,
                    f"{after.name} follows {before.name}, same family ({before.family}), -{SAME_FAMILY_PENALTY}",
                )
            )

    if previous is not None:
        for crop in crops:
            if crop.name == previous.name:
                notes.append(
                    Note(
                        -REPEAT_PENALTY,
                        f"{crop.name} repeats the farmer's previous crop, -{REPEAT_PENALTY}",
                    )
                )

    if improve_soil:
        for crop in crops:
            if crop.soil_effect == "structure":
                notes.append(
                    Note(
                        STRUCTURE_BONUS,
                        f"{crop.name} roots deeply and improves soil structure, +{STRUCTURE_BONUS}",
                    )
                )

    return RotationDelta(sum(note.points for note in notes), tuple(notes))


def clamp_score(raw: float) -> int:
    """The score the screen prints. Ranking happens before this cap."""

    capped = min(100.0, max(0.0, raw))
    return int(capped + 0.5)


def _explain(
    crops: tuple[Crop, Crop, Crop],
    fits: tuple[CropFit, CropFit, CropFit],
    delta: RotationDelta,
    conditions: FarmConditions,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    reasons = [note.text for note in delta.notes if note.points > 0]
    risks = [note.text for note in delta.notes if note.points < 0]

    for year, crop, fit in zip((1, 2, 3), crops, fits):
        terms = fit.as_terms()
        best = max(TERMS, key=lambda term: (terms[term], term))
        worst = min(TERMS, key=lambda term: (terms[term], term))
        reasons.append(f"Year {year} {crop.name}: {best} fit {round(terms[best])}/100")
        if terms[worst] < WEAK_FIT:
            risks.append(f"Year {year} {crop.name}: {worst} fit {round(terms[worst])}/100")
        if conditions.water_level == "limited" and crop.water_need_mm >= HIGH_WATER_NEED_MM:
            risks.append(
                f"Year {year} {crop.name} needs {crop.water_need_mm} mm this season and water is limited"
            )
        if crop.soil_effect == "depletes":
            risks.append(f"Year {year} {crop.name} is a heavy feeder and draws nitrogen down")

    if not reasons:
        reasons.append("Water, heat, soil, and salinity all sit in the middle of the range")
    if not risks:
        risks.append("No weak fit and no rotation penalty")
    return tuple(reasons), tuple(risks)


def score_rotation(rotation: tuple[str, ...] | list[str], conditions: FarmConditions) -> ScoredRotation:
    """Score one sequence of three crop names."""

    if len(rotation) != 3:
        raise ValueError("A rotation is three crops")
    crops = tuple(get_crop(name) for name in rotation)
    fits = tuple(crop_fit(crop, conditions) for crop in crops)
    delta = rotation_delta(crops, conditions)
    raw = sum(fit.total for fit in fits) / 3 + delta.points
    reasons, risks = _explain(crops, fits, delta, conditions)
    names = (crops[0].name, crops[1].name, crops[2].name)
    return ScoredRotation(names, clamp_score(raw), reasons, risks)


def rank_rotations(conditions: FarmConditions) -> Recommendation:
    """Try every 3-crop sequence and return the best plus two alternatives.

    Each crop is scored once. The 15³ sequences only combine those fifteen
    totals with the rotation rules, which is why this stays under a second.
    """

    fits = {crop.name: crop_fit(crop, conditions) for crop in CROPS}
    crops_by_name = {crop.name: crop for crop in CROPS}
    ranked: list[tuple[float, ScoredRotation]] = []

    for names in product(crops_by_name, repeat=3):
        crops = (crops_by_name[names[0]], crops_by_name[names[1]], crops_by_name[names[2]])
        used = (fits[names[0]], fits[names[1]], fits[names[2]])
        delta = rotation_delta(crops, conditions)
        raw = sum(fit.total for fit in used) / 3 + delta.points
        reasons, risks = _explain(crops, used, delta, conditions)
        plan = ScoredRotation(names, clamp_score(raw), reasons, risks)
        ranked.append((raw, plan))

    # Same total: prefer three different names, then A to Z. The name order
    # is only a tie-break, so the same input cannot flip between runs.
    ranked.sort(
        key=lambda item: (
            -round(item[0], 4),
            -len(set(item[1].rotation)),
            item[1].rotation,
        )
    )
    return Recommendation(
        recommended=ranked[0][1],
        alternatives=(ranked[1][1], ranked[2][1]),
    )
