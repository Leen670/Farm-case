"""The AI Assistant button. It talks about the case already on screen.

The ranker is not called again. Gemini sees a short copy of the case, with
the picture links removed. If that call fails, a keyword picks one of five
prepared answers built from the same case.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict, deque

from app.llm import gemini_reply, grounded_in_case

LIMIT = 20
WINDOW_SECONDS = 60.0
MAX_OUTPUT_TOKENS = 300
TIMEOUT_SECONDS = 10.0
MAX_QUESTION_CHARS = 500

SYSTEM_PROMPT = (
    "You are the Farm Case assistant. "
    "Answer in 2 or 3 short sentences. "
    "Use only the case JSON and general farming knowledge. "
    "Do not invent measurements, dates, or crops, and do not change the rotation. "
    "If the case does not say it, say you do not know. "
    "If the question is not about this farm, politely refuse. "
    "History is this conversation. Use it for follow-up questions. "
    "Farm facts still come only from the case."
)

_HITS: dict[str, deque[float]] = defaultdict(deque)
_DROP = {"image_url", "source_url", "url", "proxy_path", "fallback_url"}


def reset_rate_limit() -> None:
    """Forget recent questions. Tests use this so they do not share a bucket."""

    _HITS.clear()


def allow_question(ip: str, now: float | None = None) -> bool:
    """True when this address is still inside 20 questions per minute."""

    moment = time.monotonic() if now is None else now
    hits = _HITS[ip]
    while hits and moment - hits[0] >= WINDOW_SECONDS:
        hits.popleft()
    if len(hits) >= LIMIT:
        return False
    hits.append(moment)
    return True


async def answer_question(case: dict, question: str, history: list | None = None) -> str:
    """Answer from Gemini, or from the five prepared replies.

    history is the earlier chat, newest last. It does not replace the case.
    """

    asked = " ".join(question.split())[:MAX_QUESTION_CHARS]
    if not asked:
        return _OFF_TOPIC
    try:
        reply = await gemini_reply(
            SYSTEM_PROMPT,
            json.dumps(
                {"case": _slim(case), "history": _history(history), "question": asked},
                ensure_ascii=False,
            ),
            max_output_tokens=MAX_OUTPUT_TOKENS,
            timeout=TIMEOUT_SECONDS,
        )
    except Exception:
        return canned_answer(case, asked)
    cleaned = reply.strip()[:1200]
    # The same rule as the results paragraph: a crop or a number that is not
    # in the case is replaced by the prepared answer.
    if not cleaned or not grounded_in_case(cleaned, _slim(case)):
        return canned_answer(case, asked)
    return cleaned


def canned_answer(case: dict, question: str) -> str:
    """One of five replies, chosen from the words in the question."""

    facts = _facts(case)
    topic = _topic(question)
    if topic == "power":
        climate = facts["climate"]
        extra = f" The climate card says: {climate}" if climate else ""
        return (
            "NASA POWER is the climate record this case used for temperature and rain. "
            "The assistant does not replace those numbers."
            f"{extra}"
        )
    if topic == "rotation":
        crops = ", ".join(facts["crops"]) if facts["crops"] else "not listed in this case"
        sentences = [f"The recommended rotation is {crops}."]
        if facts["why"]:
            sentences.append(_sentence(facts["why"][0]))
        if facts["risks"]:
            sentences.append(_sentence(facts["risks"][0]))
        return " ".join(sentences)
    if topic == "water":
        return _card("water", facts["water"])
    if topic == "soil":
        return _card("soil", facts["soil"])
    if topic == "climate":
        return _card("climate", facts["climate"])
    return _OFF_TOPIC


_OFF_TOPIC = (
    "I can only help with this farm's rotation, water, soil, climate, "
    "and the NASA POWER source."
)


def _topic(question: str) -> str:
    text = question.casefold()
    if "power" in text:
        return "power"
    if any(word in text for word in ("rotation", "why this", "plan", "crop")):
        return "rotation"
    if any(word in text for word in ("water", "rain", "wet")):
        return "water"
    if "soil" in text:
        return "soil"
    if any(word in text for word in ("climate", "temperature", "heat", "weather")):
        return "climate"
    return ""


def _facts(case: dict) -> dict[str, str | list[str]]:
    recommended = case.get("recommended") if isinstance(case.get("recommended"), dict) else {}
    crops = recommended.get("crops") or recommended.get("rotation") or []
    why = recommended.get("why") or recommended.get("reasons") or []
    risks = recommended.get("risks") or []
    return {
        "crops": [str(item) for item in crops],
        "why": [str(item) for item in why],
        "risks": [str(item) for item in risks],
        "climate": _clue(case, "climate"),
        "soil": _clue(case, "soil"),
        "water": _clue(case, "water"),
    }


def _clue(case: dict, name: str) -> str:
    clues = case.get("clues")
    if not isinstance(clues, list):
        return ""
    for clue in clues:
        if not isinstance(clue, dict):
            continue
        label = str(clue.get("name") or clue.get("title") or clue.get("id") or "")
        if label.casefold() != name:
            continue
        return str(clue.get("line") or clue.get("summary") or "").strip()
    return ""


def _card(label: str, line: str) -> str:
    if not line:
        return f"This case does not include a {label} reading, so I cannot add one."
    return _sentence(line)


def _sentence(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return cleaned
    cleaned = cleaned[0].upper() + cleaned[1:]
    if cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


def _history(turns: list | None) -> list[dict[str, str]]:
    """Keep the last few lines. Drop anything that is not a short chat turn."""

    if not turns:
        return []
    kept: list[dict[str, str]] = []
    for turn in turns[-8:]:
        if isinstance(turn, dict):
            role = turn.get("role")
            raw = turn.get("text", "")
        else:
            role = getattr(turn, "role", None)
            raw = getattr(turn, "text", "")
        text = " ".join(str(raw).split())[:MAX_QUESTION_CHARS]
        if role not in ("user", "assistant") or not text:
            continue
        kept.append({"role": role, "text": text})
    return kept


def _slim(value):
    """Drop picture links so the chat call is not spent on long URLs."""

    if isinstance(value, dict):
        return {key: _slim(item) for key, item in value.items() if key not in _DROP}
    if isinstance(value, list):
        return [_slim(item) for item in value]
    return value
