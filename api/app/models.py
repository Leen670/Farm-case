"""The API contract. This file is the source of truth for every request and response.

The web app will mirror these shapes in TypeScript. Change a field here only
when the team agrees, then update web/src/types/api.ts to match.
"""

from typing import Literal

from pydantic import BaseModel

Soil = Literal["sandy", "clay", "silty", "loamy"]
WaterLevel = Literal["available", "moderate", "limited"]
WaterSource = Literal["rain", "ground", "surface", "treated", "desalinated"]
Priority = Literal["save_water", "increase_yield", "improve_soil", "lower_cost"]


class CaseRequest(BaseModel):
    """What the player sends after filling in the farmer form."""

    farmer_name: str
    lat: float
    lon: float
    soil: Soil | None = None  # None -> use a SoilGrids suggestion when that exists
    water_level: WaterLevel
    water_source: WaterSource
    previous_crops: list[str] = []
    priorities: list[Priority] = []
    priorities_text: str = ""


class Clue(BaseModel):
    """One piece of evidence shown on the farm map."""

    id: Literal["climate", "soil", "water", "crop"]
    title: str
    values: dict[str, float | str]
    summary: str
    source: str
    source_url: str
    image_url: str | None = None


class CluesResponse(BaseModel):
    """The four map cards for one farm."""

    clues: list[Clue]


class Plan(BaseModel):
    """A three-year rotation, its score, and the reasons behind both."""

    rotation: list[str]
    suitability: int
    reasons: list[str]
    risks: list[str]


class CaseResponse(BaseModel):
    """The full case the results screen renders."""

    case_id: str
    clues: list[Clue]
    recommended: Plan
    alternatives: list[Plan]
    explanation: str
    used_fallback: bool
