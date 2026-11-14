"""The API contract. This file is the source of truth for every request and response.

The web app will mirror these shapes in TypeScript. Change a field here only
when the team agrees, then update web/src/types/api.ts to match.
"""

from typing import Any, Literal

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


class Evidence(BaseModel):
    """One row of the results screen's See the evidence panel."""

    label: str
    value: str
    unit: str
    source: str


class CaseResponse(BaseModel):
    """The full case the results screen renders."""

    case_id: str
    clues: list[Clue]
    recommended: Plan
    alternatives: list[Plan]
    explanation: str
    evidence: list[Evidence]
    used_fallback: bool


class SimpleClue(BaseModel):
    """One card, flattened for Unity's JsonUtility."""

    name: str
    line: str
    source: str
    image_url: str = ""


class SimplePlan(BaseModel):
    """A rotation Unity can show without nested dictionaries."""

    crops: list[str]
    score: int
    why: list[str]
    risks: list[str]


class SimpleCase(BaseModel):
    """The case as Kadi's Unity screens read it.

    JsonUtility needs public fields, JSON arrays, and no nulls. demo_data
    is true when the climate numbers came from a saved POWER response.
    """

    title: str
    clues: list[SimpleClue]
    recommended: SimplePlan
    alternatives: list[SimplePlan]
    demo_data: bool


class WorldMap(BaseModel):
    """A north-up world picture for the farm picker.

    image_url is the NASA GIBS picture. proxy_path is that same picture
    through this API, for a WebGL build that cannot read GIBS directly.
    A click is pixels from the left and from the top:
    lon = x / width * 360 - 180, lat = 90 - y / height * 180.
    """

    image_url: str
    width: int
    height: int
    proxy_path: str


class AssistantRequest(BaseModel):
    """The case already on screen, plus the player's question.

    case accepts either the full case or the flat Unity case. The assistant
    does not score the farm again.
    """

    case: dict[str, Any]
    question: str


class AssistantReply(BaseModel):
    """One short answer for the chat box."""

    answer: str
