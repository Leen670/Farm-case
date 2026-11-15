"""Turn a farmer form into clues and a case.

The route handlers stay thin. This module is where the three services meet:
NASA POWER for the numbers, NASA GIBS for the pictures, and the ranker for
the rotation. The ranker never sees a URL, and GIBS never sees a crop score.
"""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime

import httpx

from app import gibs, nasa_power
from app.explain import explain_plan
from app.llm import polish_explanation
from app.models import CaseRequest, CaseResponse, Clue, Plan
from app.nasa_power import Climatology, PowerError
from app.scoring import FarmConditions, ScoredRotation, rank_rotations

# A pin this close to a saved demo farm may use that farm's fixture.
FIXTURE_MATCH_DEGREES = 0.02

NDVI_LAYER = "MODIS_Terra_NDVI_8Day"
SMAP_LAYER = "SMAP_L3_Passive_Enhanced_Day_Soil_Moisture"
IMERG_LAYER = "IMERG_Precipitation_Rate"


class ClimateUnavailable(RuntimeError):
    """POWER did not answer, and this pin has no saved fixture."""


async def load_climate(lat: float, lon: float) -> tuple[Climatology, bool]:
    """POWER for this pin. The bool is true only when POWER did not answer.

    The 0.5 degree cache is still NASA's download, including the copy the
    clue request just stored. It is not demo data. The bool is true only
    when POWER cannot be reached and a demo farm's saved fixture is used.
    """

    try:
        payload = await nasa_power.fetch_climatology(lat, lon)
        return nasa_power.parse_climatology(payload), False
    except (httpx.HTTPError, PowerError, KeyError, TypeError, ValueError):
        payload = _demo_fixture(lat, lon)
        if payload is None:
            raise ClimateUnavailable(
                "NASA POWER did not answer, and this pin has no saved fixture."
            ) from None
        return nasa_power.parse_climatology(payload), True


def _demo_fixture(lat: float, lon: float) -> dict | None:
    for name, (farm_lat, farm_lon) in nasa_power.DEMO_FARMS.items():
        if abs(lat - farm_lat) > FIXTURE_MATCH_DEGREES or abs(lon - farm_lon) > FIXTURE_MATCH_DEGREES:
            continue
        path = nasa_power.FIXTURE_DIR / f"power_{name}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


def assemble_clues(case: CaseRequest, climate: Climatology, day: date | datetime) -> list[Clue]:
    """Four cards, in map order: climate, soil, water, crop."""

    pictures = {shot["layer_id"]: shot for shot in gibs.snapshots(case.lat, case.lon, day)}
    return [
        _climate_clue(climate, pictures[IMERG_LAYER]),
        _soil_clue(case),
        _water_clue(case, climate, pictures[SMAP_LAYER]),
        _crop_clue(pictures[NDVI_LAYER]),
    ]


async def build_clues(
    case: CaseRequest,
    *,
    day: date | datetime | None = None,
) -> tuple[list[Clue], bool]:
    """Load POWER once and build the four cards."""

    climate, used_fallback = await load_climate(case.lat, case.lon)
    return assemble_clues(case, climate, day or date.today()), used_fallback


async def build_case(case: CaseRequest, *, day: date | datetime | None = None) -> CaseResponse:
    """The full results screen: the same four clues, then the ranked plans.

    POWER is loaded once. The ranker reads those numbers and the form.
    Gemini may restyle the paragraph. It does not choose the rotation.
    """

    climate, used_fallback = await load_climate(case.lat, case.lon)
    recommendation = rank_rotations(_conditions(case, climate))
    when = day or date.today()
    clues = assemble_clues(case, climate, when)
    explanation, evidence = explain_plan(
        case,
        recommendation.recommended,
        climate,
        used_fallback=used_fallback,
    )
    # The model sees this JSON and nothing else. The check after the reply
    # uses the same object, so a number has to be one the player can see.
    facts = _case_facts(case.farmer_name, recommendation, evidence, clues)
    explanation = await polish_explanation(
        explanation,
        case.farmer_name,
        recommendation.recommended.rotation,
        facts,
    )
    return CaseResponse(
        case_id=uuid.uuid4().hex,
        clues=clues,
        recommended=_plan(recommendation.recommended),
        alternatives=[_plan(item) for item in recommendation.alternatives],
        explanation=explanation,
        evidence=evidence,
        used_fallback=used_fallback,
    )


def _conditions(case: CaseRequest, climate: Climatology) -> FarmConditions:
    return FarmConditions(
        rain_mm=climate.rain_mm_per_year,
        max_temp_c=climate.annual_max_temp_c,
        avg_temp_c=climate.avg_temp_c,
        soil=case.soil,
        water_level=case.water_level,
        water_source=case.water_source,
        previous_crops=tuple(case.previous_crops),
        priorities=tuple(case.priorities),
    )


def _case_facts(farmer_name: str, recommendation, evidence, clues) -> dict:
    """The crops and numbers the results paragraph is allowed to repeat."""

    def plan(item) -> dict:
        return {
            "rotation": list(item.rotation),
            "suitability": item.suitability,
            "reasons": list(item.reasons),
            "risks": list(item.risks),
        }

    return {
        "farmer_name": farmer_name,
        "clues": [{"title": clue.title, "summary": clue.summary} for clue in clues],
        "recommended": plan(recommendation.recommended),
        "alternatives": [plan(item) for item in recommendation.alternatives],
        "evidence": [
            {"label": row.label, "value": row.value, "unit": row.unit} for row in evidence
        ],
    }


def _plan(scored: ScoredRotation) -> Plan:
    return Plan(
        rotation=list(scored.rotation),
        suitability=scored.suitability,
        reasons=list(scored.reasons),
        risks=list(scored.risks),
    )


def _climate_clue(climate: Climatology, imerg: dict) -> Clue:
    return Clue(
        id="climate",
        title="Climate",
        values={
            "avg_temp_c": climate.avg_temp_c,
            "annual_max_temp_c": climate.annual_max_temp_c,
            "annual_max_temp_month": climate.annual_max_temp_month,
            "rain_mm_per_day": climate.rain_mm_per_day,
            "rain_mm_per_year": climate.rain_mm_per_year,
            "sunlight_mj_per_m2_per_day": climate.sunlight_mj_per_m2_per_day,
            "humidity_percent": climate.humidity_percent,
        },
        summary=(
            f"The average temperature is {climate.avg_temp_c:.1f}°C. "
            f"The hottest month, {climate.annual_max_temp_month}, reaches "
            f"{climate.annual_max_temp_c:.1f}°C, and the year brings "
            f"{climate.rain_mm_per_year:.0f} mm of rain."
        ),
        source=nasa_power.SOURCE,
        source_url=nasa_power.SOURCE_URL,
        image_url=str(imerg["url"]),
    )


def _soil_clue(case: CaseRequest) -> Clue:
    if case.soil is None:
        summary = "The farmer has not chosen a soil type yet. The ranker treats the soil as unknown."
        soil_value = "unspecified"
    else:
        summary = f"The farmer reports {case.soil} soil."
        soil_value = case.soil
    return Clue(
        id="soil",
        title="Soil",
        values={"soil": soil_value},
        summary=summary,
        source="Entered by the farmer",
        source_url="",
    )


def _water_clue(case: CaseRequest, climate: Climatology, smap: dict) -> Clue:
    values: dict[str, float | str] = {
        "wetness_label": gibs.POWER_WETNESS_LABEL,
        "water_level": case.water_level,
        "water_source": case.water_source,
    }
    if climate.root_zone_wetness is None:
        summary = (
            "NASA POWER has no root-zone wetness for this pin, which usually "
            "means it is not on land. The farmer reports "
            f"{case.water_level} water from {case.water_source}."
        )
    else:
        values["root_zone_wetness"] = climate.root_zone_wetness
        summary = (
            f"Root-zone wetness is {climate.root_zone_wetness:.2f} "
            f"from {gibs.POWER_WETNESS_LABEL}. The farmer reports "
            f"{case.water_level} water from {case.water_source}."
        )
    return Clue(
        id="water",
        title="Water",
        values=values,
        summary=summary,
        source=f"{gibs.POWER_WETNESS_LABEL}; {smap['source_label']}",
        source_url=nasa_power.SOURCE_URL,
        image_url=str(smap["url"]),
    )


def _crop_clue(ndvi: dict) -> Clue:
    named = " and ".join(gibs.NAMED_ONLY)
    return Clue(
        id="crop",
        title="Crop",
        values={
            "image_date": str(ndvi["date_used"]),
            "layer_id": str(ndvi["layer_id"]),
        },
        summary=(
            f"MODIS NDVI picture for {ndvi['date_used']}. "
            f"{named} are named only and are not downloaded."
        ),
        source=str(ndvi["source_label"]),
        source_url=gibs.WMS_ENDPOINT,
        image_url=str(ndvi["url"]),
    )

