"""The crop table the ranker reads. Nothing here calls NASA or scores a farm.

Seasonal water need is the midpoint of a published FAO range, in millimetres
for one growing season. The ranges are Table 5 of FAO Irrigation Water
Management, Training manual no. 3:

https://www.fao.org/4/s2022e/s2022e02.htm

Chickpea and lentil use that table's bean row (300–500). Faba bean uses the
pea row (350–500). Sesame is not a row of its own; it uses the oil-seed range
(300–600) in FAO Irrigation and Drainage Paper 24.

Salt tolerance is a 1–5 stand-in for the classes in FAO Irrigation and
Drainage Paper 29: 5 tolerant, 4 moderately tolerant, 2 moderately sensitive,
1 sensitive. Soil preference is ordinary agronomy, not a NASA product.

Temperature limits and soil pH are 'FAO EcoCrop (via openclim/ecocrop)'.
Summer crops are scored on those temperature limits. Winter crops still
use heat_tolerance, a 1–5 scale for the cool season, so a hot site does
not treat a winter grain as if it were growing through the hottest month.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.ecocrop import EcoCrop, species

Family = Literal["cereal", "legume", "oilseed", "forage", "vegetable", "fibre"]
Season = Literal["winter", "summer"]
SoilEffect = Literal["nitrogen", "structure", "depletes", "neutral"]

FAMILIES = ("cereal", "legume", "oilseed", "forage", "vegetable", "fibre")
SEASONS = ("winter", "summer")
SOIL_EFFECTS = ("nitrogen", "structure", "depletes", "neutral")
SOIL_TYPES = ("sandy", "clay", "silty", "loamy")


@dataclass(frozen=True)
class Crop:
    """One row of the crop table."""

    name: str
    family: Family
    season: Season
    water_need_mm: int
    # Read for winter crops only. Summer heat uses the EcoCrop range below.
    heat_tolerance: int
    salt_tolerance: int
    soil_pref: tuple[str, ...]
    soil_effect: SoilEffect
    # FAO EcoCrop (via openclim/ecocrop). Absolute temperature, degrees C.
    temp_min: float
    temp_opt_lo: float
    temp_opt_hi: float
    temp_max: float
    # FAO EcoCrop (via openclim/ecocrop). Used when a SoilGrids pH is passed in.
    ph_min: float
    ph_max: float

    def __post_init__(self) -> None:
        if self.family not in FAMILIES:
            raise ValueError(f"{self.name} has an unknown family")
        if self.season not in SEASONS:
            raise ValueError(f"{self.name} has an unknown season")
        if self.soil_effect not in SOIL_EFFECTS:
            raise ValueError(f"{self.name} has an unknown soil effect")
        if self.heat_tolerance not in range(1, 6):
            raise ValueError(f"{self.name} heat tolerance must be 1–5")
        if self.salt_tolerance not in range(1, 6):
            raise ValueError(f"{self.name} salt tolerance must be 1–5")
        unknown = set(self.soil_pref) - set(SOIL_TYPES)
        if unknown:
            raise ValueError(f"{self.name} has unknown soils: {sorted(unknown)}")
        if not (self.temp_min <= self.temp_opt_lo <= self.temp_opt_hi <= self.temp_max):
            raise ValueError(f"{self.name} has an unordered temperature range")
        if self.ph_min > self.ph_max:
            raise ValueError(f"{self.name} has an unordered pH range")


def _climate(scientific_name: str) -> dict[str, float]:
    """Temperature and pH from one EcoCrop row. Rain stays the FAO water table."""

    row: EcoCrop = species(scientific_name)
    if row.ph_min is None or row.ph_max is None:
        raise ValueError(f"{scientific_name} has no EcoCrop pH range")
    return {
        "temp_min": row.temp_min,
        "temp_opt_lo": row.temp_opt_lo,
        "temp_opt_hi": row.temp_opt_hi,
        "temp_max": row.temp_max,
        "ph_min": row.ph_min,
        "ph_max": row.ph_max,
    }


# Fifteen crops. 15³ is 3,375 rotations, which is the search the brief sized.
# Each **_climate(...) is one EcoCrop scientific name.
CROPS: tuple[Crop, ...] = (
    Crop(
        name="wheat",
        family="cereal",
        season="winter",
        water_need_mm=550,  # barley/wheat 450–650
        heat_tolerance=3,
        salt_tolerance=4,  # moderately tolerant
        soil_pref=("loamy", "clay", "silty"),
        soil_effect="neutral",
        **_climate("Triticum aestivum"),
    ),
    Crop(
        name="barley",
        family="cereal",
        season="winter",
        water_need_mm=550,  # barley/wheat 450–650
        heat_tolerance=3,
        salt_tolerance=5,  # tolerant
        soil_pref=("loamy", "sandy"),
        soil_effect="neutral",
        **_climate("Hordeum vulgare"),
    ),
    Crop(
        name="sorghum",
        family="cereal",
        season="summer",
        water_need_mm=550,  # sorghum/millet 450–650
        heat_tolerance=5,
        salt_tolerance=4,  # moderately tolerant
        soil_pref=("loamy", "sandy", "clay"),
        soil_effect="structure",
        **_climate("Sorghum bicolor"),
    ),
    Crop(
        name="millet",
        family="cereal",
        season="summer",
        water_need_mm=550,  # sorghum/millet 450–650
        heat_tolerance=5,
        # Paper 29 has no millet row. Millet shares sorghum's water row and
        # the same moderately tolerant class. The EcoCrop row is pearl millet.
        salt_tolerance=4,
        soil_pref=("sandy", "loamy"),
        soil_effect="neutral",
        **_climate("Pennisetum glaucum"),
    ),
    Crop(
        name="maize",
        family="cereal",
        season="summer",
        water_need_mm=650,  # maize 500–800
        heat_tolerance=4,
        salt_tolerance=2,  # moderately sensitive
        soil_pref=("loamy", "silty"),
        soil_effect="depletes",
        **_climate("Zea mays"),
    ),
    Crop(
        name="chickpea",
        family="legume",
        season="winter",
        water_need_mm=400,  # bean 300–500
        heat_tolerance=3,
        salt_tolerance=1,  # bean: sensitive
        soil_pref=("loamy", "sandy"),
        soil_effect="nitrogen",
        **_climate("Cicer arietinum"),
    ),
    Crop(
        name="faba bean",
        family="legume",
        season="winter",
        water_need_mm=425,  # pea 350–500
        heat_tolerance=2,
        salt_tolerance=1,  # bean: sensitive
        soil_pref=("loamy", "clay"),
        soil_effect="nitrogen",
        **_climate("Vicia faba"),
    ),
    Crop(
        name="lentil",
        family="legume",
        season="winter",
        water_need_mm=400,  # bean 300–500
        heat_tolerance=2,
        salt_tolerance=1,  # bean: sensitive
        soil_pref=("loamy", "sandy"),
        soil_effect="nitrogen",
        **_climate("Lens culinaris"),
    ),
    Crop(
        name="sesame",
        family="oilseed",
        season="summer",
        water_need_mm=450,  # oil seeds 300–600, Paper 24
        heat_tolerance=5,
        salt_tolerance=2,
        soil_pref=("sandy", "loamy"),
        soil_effect="neutral",
        **_climate("Sesamum indicum"),
    ),
    Crop(
        name="sunflower",
        family="oilseed",
        season="summer",
        water_need_mm=800,  # sunflower 600–1000
        heat_tolerance=4,
        salt_tolerance=2,  # moderately sensitive
        soil_pref=("loamy", "silty", "clay"),
        soil_effect="structure",
        **_climate("Helianthus annuus"),
    ),
    Crop(
        name="alfalfa",
        family="forage",
        season="summer",
        water_need_mm=1200,  # alfalfa 800–1600
        heat_tolerance=4,
        salt_tolerance=4,  # moderately tolerant
        soil_pref=("loamy", "silty"),
        # Alfalfa also roots deeply. One effect per crop: nitrogen is the
        # one the legume-after-cereal rule uses.
        soil_effect="nitrogen",
        **_climate("Medicago sativa"),
    ),
    Crop(
        name="tomato",
        family="vegetable",
        season="summer",
        water_need_mm=600,  # tomato 400–800
        heat_tolerance=3,
        salt_tolerance=2,  # moderately sensitive
        soil_pref=("loamy", "silty"),
        soil_effect="depletes",
        **_climate("Lycopersicon esculentum"),
    ),
    Crop(
        name="potato",
        family="vegetable",
        season="summer",
        water_need_mm=600,  # potato 500–700
        heat_tolerance=2,
        salt_tolerance=2,  # moderately sensitive
        soil_pref=("loamy", "sandy"),
        soil_effect="depletes",
        **_climate("Solanum tuberosum"),
    ),
    Crop(
        name="onion",
        family="vegetable",
        season="winter",
        water_need_mm=450,  # onion 350–550
        heat_tolerance=2,
        salt_tolerance=1,  # sensitive
        soil_pref=("loamy", "silty", "sandy"),
        soil_effect="neutral",
        **_climate("Allium cepa"),
    ),
    Crop(
        name="cotton",
        family="fibre",
        season="summer",
        water_need_mm=1000,  # cotton 700–1300
        heat_tolerance=5,
        salt_tolerance=5,  # tolerant
        soil_pref=("loamy", "clay"),
        soil_effect="depletes",
        **_climate("Gossypium hirsutum"),
    ),
)

# The form and the icons say corn. The table row is maize.
ALIASES = {"corn": "maize"}

BY_NAME = {crop.name: crop for crop in CROPS}


def get_crop(name: str) -> Crop:
    """Return the table row for a name the player typed."""

    key = ALIASES.get(name.strip().casefold(), name.strip().casefold())
    try:
        return BY_NAME[key]
    except KeyError:
        raise KeyError(f"Unknown crop: {name}") from None


def find_crop(name: str) -> Crop | None:
    """Like get_crop, but an unknown previous crop is ignored."""

    try:
        return get_crop(name)
    except KeyError:
        return None
