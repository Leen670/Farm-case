"""Restyle the finished explanation. This module cannot score a farm.

The ranker has already chosen the crops and the numbers. Gemini may only
rephrase that paragraph. A missing key, a network error, or a reply that
names a crop or a number the case JSON does not contain all return the
original paragraph.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import httpx

from app.crops import ALIASES, CROPS

MODEL = "gemini-3.5-flash-lite"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
TIMEOUT_SECONDS = 8.0

_RULES = (
    "Rewrite the paragraph in plain sentences for a farm game. "
    "The crops and the numbers are already decided. "
    "Every crop name and every number in your reply must appear in the case JSON. "
    "Drop a sentence rather than keep a number that is not in the case. "
    "Do not add a crop, a measurement, a place, or a reason. "
    "Reply with the paragraph only."
)
_NUMBER = re.compile(r"[+\-]?\d+(?:\.\d+)?")
_LABELS = sorted(
    [(crop.name, crop.name) for crop in CROPS] + list(ALIASES.items()),
    key=lambda item: len(item[0]),
    reverse=True,
)


def load_local_env() -> None:
    """Read the repo .env without replacing variables the host already set."""

    path = Path(__file__).resolve().parents[2] / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


async def polish_explanation(
    template: str,
    farmer_name: str,
    rotation: tuple[str, ...],
    case: dict | None = None,
) -> str:
    """Return a rewritten paragraph, or the template when that is not safe."""

    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        return template
    try:
        reply = await _call_gemini(key, template, case)
        cleaned = _plain_paragraph(reply)
        if rewrite_is_faithful(cleaned, template, rotation, farmer_name, case):
            return cleaned
    except Exception:
        return template
    return template


def grounded_in_case(text: str, case: object) -> bool:
    """True when every crop name and every number in the text is in the case.

    Picture links are not part of the case text. A link is full of coordinates,
    and those are not measurements the assistant is allowed to invent from.
    """

    blob = case if isinstance(case, str) else json.dumps(case, ensure_ascii=False, default=str)
    if _number_values(text) - _number_values(blob):
        return False
    if _mentioned_crops(text) - _mentioned_crops(blob):
        return False
    return True


def rewrite_is_faithful(
    rewrite: str,
    template: str,
    rotation: tuple[str, ...],
    farmer_name: str,
    case: dict | None = None,
) -> bool:
    """True when the reply keeps this farmer, these crops, and these numbers.

    With a case, the allowed crops and numbers are the ones written in that
    JSON. Without one, they are the ones written in the template.
    """

    if not rewrite or len(rewrite) > 2000 or "http" in rewrite.casefold():
        return False
    name = farmer_name.strip()
    if len(name) >= 2 and name.casefold() not in rewrite.casefold():
        return False
    mentioned = _mentioned_crops(rewrite)
    planned = {crop.casefold() for crop in rotation}
    if case is None:
        if _number_values(rewrite) - _number_values(template):
            return False
        allowed = _mentioned_crops(template)
    else:
        if not grounded_in_case(rewrite, case):
            return False
        allowed = _mentioned_crops(json.dumps(case, ensure_ascii=False, default=str))
    if mentioned - allowed or not planned <= mentioned:
        return False
    return True


async def gemini_reply(
    system: str,
    user: str,
    *,
    max_output_tokens: int,
    timeout: float,
) -> str:
    """One Gemini reply. Raises when the key is missing or the call fails."""

    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            ENDPOINT,
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json={
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": {
                    "temperature": 0,
                    "maxOutputTokens": max_output_tokens,
                },
            },
        )
    response.raise_for_status()
    return _reply_text(response.json())


async def _call_gemini(key: str, template: str, case: dict | None = None) -> str:
    case_block = ""
    if case is not None:
        case_block = (
            "Case JSON:\n"
            + json.dumps(case, ensure_ascii=False, default=str)
            + "\n\n"
        )
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        response = await client.post(
            ENDPOINT,
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{_RULES}\n\n{case_block}Paragraph:\n{template}"}
                        ],
                    }
                ],
                "generationConfig": {"temperature": 0, "maxOutputTokens": 512},
            },
        )
    response.raise_for_status()
    return _reply_text(response.json())


def _reply_text(payload: dict) -> str:
    parts = payload["candidates"][0]["content"]["parts"]
    texts = [part.get("text", "") for part in parts if not part.get("thought") and part.get("text")]
    return "\n".join(texts).strip()


def _plain_paragraph(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    return cleaned.strip().strip('"')


def _number_values(text: str) -> set[str]:
    normalized = text.replace("\u2212", "-")
    values = set()
    for raw in _NUMBER.findall(normalized):
        rendered = format(float(raw), "f").rstrip("0").rstrip(".")
        values.add(rendered or "0")
    return values


def _mentioned_crops(text: str) -> set[str]:
    folded = text.casefold()
    found: set[str] = set()
    for label, canonical in _LABELS:
        if re.search(rf"\b{re.escape(label.casefold())}\b", folded):
            found.add(canonical.casefold())
    return found
