"""Gemini may restyle the paragraph. It may not change the case."""

import asyncio

import httpx

from app.llm import grounded_in_case, polish_explanation, rewrite_is_faithful

TEMPLATE = (
    "For Ada, the three-year rotation is maize, faba bean, maize, "
    "with suitability 100. Yearly rain at this pin is 865 mm, from NASA POWER."
)
ROTATION = ("maize", "faba bean", "maize")
FAITHFUL = (
    "Ada's three-year plan is maize, then faba bean, then maize. "
    "The suitability is 100, and NASA POWER puts the yearly rain at 865 mm."
)


def _payload(text: str) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


class _Response:
    def __init__(self, payload: dict, status: int = 200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("gemini failed", request=None, response=None)


def _client(monkeypatch, payload: dict, captured: list, status: int = 200):
    class Client:
        def __init__(self, *args, **kwargs):
            captured.append({"timeout": kwargs.get("timeout")})

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, headers, json):
            captured.append({"url": url, "headers": headers, "json": json})
            return _Response(payload, status)

    monkeypatch.setattr(httpx, "AsyncClient", Client)


CASE = {
    "farmer_name": "Ada",
    "recommended": {
        "rotation": ["maize", "faba bean", "maize"],
        "suitability": 100,
    },
    "clues": [{"title": "Climate", "summary": "The year brings 865 mm of rain."}],
    "evidence": [{"label": "Yearly rain", "value": "865.33", "unit": "mm/year"}],
}


def _polish(template: str, farmer: str, rotation: tuple[str, ...], case: dict | None = None) -> str:
    return asyncio.run(polish_explanation(template, farmer, rotation, case))


def test_a_missing_key_keeps_the_template(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    def explode(*args, **kwargs):
        raise AssertionError("Gemini was called without a key")

    monkeypatch.setattr(httpx, "AsyncClient", explode)
    assert _polish(TEMPLATE, "Ada", ROTATION) == TEMPLATE


def test_a_faithful_reply_replaces_the_template(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    captured = []
    _client(monkeypatch, _payload(FAITHFUL), captured)

    assert _polish(TEMPLATE, "Ada", ROTATION) == FAITHFUL
    sent = captured[-1]
    assert sent["json"]["generationConfig"]["temperature"] == 0
    assert "gemini-3.5-flash-lite:generateContent" in sent["url"]
    assert "test-key" not in sent["url"]
    assert sent["headers"]["x-goog-api-key"] == "test-key"
    assert captured[0]["timeout"] == 8.0
    assert len(captured) == 2


def test_an_error_keeps_the_template(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    class Client:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, *args, **kwargs):
            raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "AsyncClient", Client)
    assert _polish(TEMPLATE, "Ada", ROTATION) == TEMPLATE


def test_a_new_crop_or_number_is_rejected():
    assert rewrite_is_faithful(FAITHFUL, TEMPLATE, ROTATION, "Ada")
    alfalfa = FAITHFUL.replace("faba bean", "alfalfa")
    assert rewrite_is_faithful(alfalfa, TEMPLATE, ROTATION, "Ada") is False
    invented = FAITHFUL.replace("865", "900")
    assert rewrite_is_faithful(invented, TEMPLATE, ROTATION, "Ada") is False


def test_corn_is_still_maize():
    corn = FAITHFUL.replace("maize", "corn")
    assert rewrite_is_faithful(corn, TEMPLATE, ROTATION, "Ada")


def test_a_number_or_crop_missing_from_the_case_is_rejected():
    assert grounded_in_case(FAITHFUL, CASE)
    # 865.33 is on the evidence row. The template only wrote 865.
    precise = FAITHFUL.replace("865", "865.33")
    assert rewrite_is_faithful(precise, TEMPLATE, ROTATION, "Ada", CASE)
    assert rewrite_is_faithful(precise, TEMPLATE, ROTATION, "Ada") is False
    invented = FAITHFUL.replace("865", "900")
    assert grounded_in_case(invented, CASE) is False
    assert rewrite_is_faithful(invented, TEMPLATE, ROTATION, "Ada", CASE) is False
    alfalfa = FAITHFUL.replace("faba bean", "alfalfa")
    assert grounded_in_case(alfalfa, CASE) is False


def test_a_number_that_is_not_in_the_case_keeps_the_template(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    template = TEMPLATE + " Limited water lowers crops that need 700 mm or more."
    copied = FAITHFUL + " Limited water lowers crops that need 700 mm or more."
    _client(monkeypatch, _payload(copied), [])

    assert _polish(template, "Ada", ROTATION, CASE) == template
