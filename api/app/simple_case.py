"""A second view of the same case, shaped for Unity's JsonUtility.

JsonUtility reads public fields on a class. It skips dictionaries, refuses
null, and does not understand a value that can be two types. This module
only renames and flattens. It does not score the farm again.
"""

from __future__ import annotations

from app.models import CaseResponse, Plan, SimpleCase, SimpleClue, SimplePlan


def as_simple_case(case: CaseResponse, farmer_name: str) -> SimpleCase:
    """Turn the full case into the flat JSON the Unity screens display."""

    return SimpleCase(
        title=f"{farmer_name}'s case",
        clues=[_clue(clue.title, clue.summary, clue.source, clue.image_url) for clue in case.clues],
        recommended=_plan(case.recommended),
        alternatives=[_plan(plan) for plan in case.alternatives],
        demo_data=case.used_fallback,
        confidence=case.confidence,
    )


def _clue(name: str, line: str, source: str, image_url: str | None) -> SimpleClue:
    return SimpleClue(
        name=name,
        line=line,
        source=source,
        image_url=image_url or "",
    )


def _plan(plan: Plan) -> SimplePlan:
    return SimplePlan(
        crops=list(plan.rotation),
        score=plan.suitability,
        why=list(plan.reasons),
        risks=list(plan.risks),
    )
