"""The 'Why this plan' paragraph and the evidence rows behind it.

Every sentence is filled from the ranker's notes and the numbers already
on the case. Nothing here calls a language model, and nothing here changes
the rotation.
"""

from __future__ import annotations

from app import gibs, nasa_power
from app.models import CaseRequest, Evidence
from app.nasa_power import Climatology
from app.scoring import ScoredRotation

_PRIORITY_WORDS = {
    "save_water": "save water",
    "increase_yield": "increase yield",
    "improve_soil": "improve soil",
    "lower_cost": "lower cost",
}


def explain_plan(
    case: CaseRequest,
    plan: ScoredRotation,
    climate: Climatology,
    *,
    used_fallback: bool,
) -> tuple[str, list[Evidence]]:
    """Return the results paragraph and the rows the evidence panel lists."""

    crops = ", ".join(plan.rotation)
    soil = case.soil if case.soil is not None else "unspecified"
    sentences = [
        (
            f"For {case.farmer_name}, the three-year rotation is {crops}, "
            f"with suitability {plan.suitability}."
        ),
        (
            f"Yearly rain at this pin is {climate.rain_mm_per_year:.0f} mm, "
            f"from NASA POWER. The farmer reports {case.water_level} water "
            f"from {case.water_source}."
        ),
        (
            f"Summer crops were checked against {climate.annual_max_temp_month}, "
            f"at {climate.annual_max_temp_c:.1f}°C. Winter crops were checked "
            f"against the average temperature, {climate.avg_temp_c:.1f}°C."
        ),
        f"The soil used in the score is {soil}.",
    ]

    bonus = next((reason for reason in plan.reasons if "+" in reason), None)
    if bonus is not None:
        sentences.append(bonus[0].upper() + bonus[1:] + ".")
    penalty = next((risk for risk in plan.risks if "-" in risk), None)
    if penalty is not None:
        sentences.append(penalty[0].upper() + penalty[1:] + ".")

    if case.water_level == "limited":
        sentences.append(
            "Limited water lowers crops that need 700 mm or more in a season."
        )

    if case.priorities:
        words = [_PRIORITY_WORDS[name] for name in case.priorities]
        sentences.append(f"The checked priorities are {', '.join(words)}.")
    if case.priorities_text.strip():
        sentences.append(f"The farmer added: {case.priorities_text.strip()}")

    sentences.append(
        "Root-zone wetness is shown beside the plan. "
        "The water score uses the yearly rain and the water the farmer reported."
    )
    if used_fallback:
        sentences.append("The climate numbers came from a saved POWER response.")

    return " ".join(sentences), evidence_rows(case, climate)


def evidence_rows(case: CaseRequest, climate: Climatology) -> list[Evidence]:
    """The values the ranker used, plus the wetness reading shown next to them."""

    power = nasa_power.SOURCE
    farmer = "Entered by the farmer"
    soil = case.soil if case.soil is not None else "unspecified"
    return [
        Evidence(
            label="Average temperature",
            value=f"{climate.avg_temp_c:.1f}",
            unit="°C",
            source=power,
        ),
        Evidence(
            label=f"Hottest month ({climate.annual_max_temp_month})",
            value=f"{climate.annual_max_temp_c:.1f}",
            unit="°C",
            source=power,
        ),
        Evidence(
            label="Yearly rain",
            value=f"{climate.rain_mm_per_year:.2f}",
            unit="mm/year",
            source=power,
        ),
        Evidence(
            label="Soil",
            value=soil,
            unit="",
            source=farmer,
        ),
        Evidence(
            label="Water level",
            value=case.water_level,
            unit="",
            source=farmer,
        ),
        Evidence(
            label="Water source",
            value=case.water_source,
            unit="",
            source=farmer,
        ),
        Evidence(
            label="Root-zone wetness",
            value=f"{climate.root_zone_wetness:.2f}",
            unit="0–1",
            source=gibs.POWER_WETNESS_LABEL,
        ),
    ]
