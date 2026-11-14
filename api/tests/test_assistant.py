"""The assistant answers from the case, and stops after 20 questions a minute."""

from fastapi.testclient import TestClient

from app.assistant import reset_rate_limit
from app.main import app

CASE = {
    "title": "Ada's case",
    "clues": [
        {
            "name": "Climate",
            "line": "The average temperature is 9.6°C and the year brings 865 mm of rain.",
            "source": "NASA POWER (climatology, AG community)",
            "image_url": "https://gibs.example/climate.png",
        },
        {
            "name": "Soil",
            "line": "The farmer reports loamy soil.",
            "source": "Entered by the farmer",
        },
        {
            "name": "Water",
            "line": "The farmer reports limited water from rain.",
            "source": "NASA POWER GWETROOT",
        },
    ],
    "recommended": {
        "crops": ["maize", "faba bean", "maize"],
        "score": 100,
        "why": ["faba bean follows maize, nitrogen crop after a cereal, +10"],
        "risks": ["Year 1 maize is a heavy feeder and draws nitrogen down"],
    },
}

QUESTIONS = {
    "why": "Why this rotation?",
    "water": "How is the water?",
    "soil": "What soil does this farm have?",
    "climate": "What is the climate like?",
    "power": "What is NASA POWER?",
}


def _ask(client: TestClient, question: str, ip: str = "203.0.113.8"):
    return client.post(
        "/api/assistant",
        json={"case": CASE, "question": question},
        headers={"x-forwarded-for": ip},
    )


def test_five_keywords_use_the_case_when_gemini_is_down(monkeypatch):
    reset_rate_limit()
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = TestClient(app)

    answers = {name: _ask(client, question).json()["answer"] for name, question in QUESTIONS.items()}

    assert "maize, faba bean, maize" in answers["why"]
    assert "heavy feeder" in answers["why"]
    assert "limited water" in answers["water"]
    assert "loamy" in answers["soil"]
    assert "865 mm" in answers["climate"]
    assert "NASA POWER" in answers["power"]
    assert "865 mm" in answers["power"]
    assert all(isinstance(text, str) and text for text in answers.values())


def test_an_unrelated_question_stays_on_the_farm(monkeypatch):
    reset_rate_limit()
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = _ask(TestClient(app), "Who won the world cup?", ip="203.0.113.9")
    assert response.status_code == 200
    assert "rotation" in response.json()["answer"]


def test_a_gemini_reply_is_returned(monkeypatch):
    reset_rate_limit()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    async def fake(system, user, *, max_output_tokens, timeout):
        assert "Farm Case assistant" in system
        assert "image_url" not in user
        assert max_output_tokens == 300
        assert timeout == 10.0
        assert "Why this rotation?" in user
        return "The plan is maize, then faba bean, then maize."

    monkeypatch.setattr("app.assistant.gemini_reply", fake)
    response = _ask(TestClient(app), "Why this rotation?", ip="203.0.113.10")
    assert response.status_code == 200
    assert response.json()["answer"] == "The plan is maize, then faba bean, then maize."


def test_the_twenty_first_question_waits(monkeypatch):
    reset_rate_limit()
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = TestClient(app)
    for _ in range(20):
        assert _ask(client, "What is the soil?", ip="203.0.113.11").status_code == 200
    blocked = _ask(client, "What is the soil?", ip="203.0.113.11")
    assert blocked.status_code == 429
    assert _ask(client, "What is the soil?", ip="203.0.113.12").status_code == 200


def test_docs_list_the_assistant():
    schema = TestClient(app).get("/openapi.json").json()
    assert "post" in schema["paths"]["/api/assistant"]
