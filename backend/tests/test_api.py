import pytest
from fastapi.testclient import TestClient

import gemini_service
import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    main._hits.clear()
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


def chat(**body):
    body.setdefault("lang", "ta")
    r = client.post("/api/chat", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def test_health():
    r = client.get("/api/health").json()
    assert r["status"] == "ok" and r["schemes"] == 3 and r["gemini"] is False


def test_start_asks_the_situation_first():
    d = chat(start=True)
    assert d["step"]["id"] == "situation" and len(d["step"]["options"]) == 5
    assert "வணக்கம்" in d["reply"] and d["result"] is None


def test_full_tamil_voice_journey_deserted_woman():
    d = chat(message="என் கணவர் என்னை விட்டுப் பிரிந்துவிட்டார்", pending="marital_status")
    assert d["step"]["id"] == "age"
    d = chat(profile=d["profile"], message="முப்பத்தெட்டு", pending="age")
    assert d["profile"]["age"] == 38 and d["step"]["id"] == "years"
    d = chat(profile=d["profile"], message="6", pending="deserted_years")
    assert d["step"]["id"] == "assets"
    d = chat(profile=d["profile"], message="இல்லை", pending="assets_over_limit")
    assert d["step"]["id"] == "result" and d["result"]["status"] == "potential_match"
    assert d["result"]["scheme"]["id"] == "ddwps" and "1,200" in d["result"]["scheme"]["amount"]
    assert len(d["result"]["documents"]) == 8 and d["result"]["sources"]


def test_full_button_journey_widow_english():
    d = chat(lang="en", answer={"slot": "marital_status", "value": "widow"})
    d = chat(lang="en", profile=d["profile"], answer={"slot": "age", "value": 45})
    assert d["step"]["id"] == "assets"          # widows are never asked about years
    d = chat(lang="en", profile=d["profile"], answer={"slot": "assets_over_limit", "value": False})
    assert d["result"]["status"] == "potential_match" and d["result"]["scheme"]["id"] == "dwps"
    assert "Widow" in d["result"]["scheme"]["name"]


def test_too_young_stops_early_with_wait_time():
    d = chat(answer={"slot": "marital_status", "value": "unmarried"})
    d = chat(profile=d["profile"], answer={"slot": "age", "value": 46})
    assert d["result"]["status"] == "criteria_not_met" and "4" in d["result"]["message"]


def test_deserted_under_five_years_mentions_court_certificate():
    p = chat(answer={"slot": "marital_status", "value": "deserted"})["profile"]
    p = chat(profile=p, answer={"slot": "age", "value": 40})["profile"]
    d = chat(profile=p, answer={"slot": "deserted_years", "value": 3})
    assert d["result"]["status"] == "criteria_not_met" and "reasons" in d["result"] and d["result"]["reasons"] == ["years"]


def test_married_woman_gets_an_honest_out_of_scope_answer():
    d = chat(answer={"slot": "marital_status", "value": "married"})
    assert d["result"]["status"] == "not_applicable" and d["result"]["scheme"] is None


def test_not_understood_repeats_the_same_question():
    d = chat(message="blah blah", pending="age", profile={"marital_status": "widow"})
    assert d["not_understood"] and d["step"]["id"] == "age"
    assert "மன்னிக்கவும்" in d["reply"]


def test_tap_a_chip_to_change_an_answer():
    d = chat(profile={"marital_status": "widow", "age": 40, "assets_over_limit": False}, ask="age")
    assert d["step"]["id"] == "age" and "age" not in d["profile"]


def test_changing_status_drops_irrelevant_years():
    d = chat(profile={"marital_status": "deserted", "age": 40, "deserted_years": 6}, answer={"slot": "marital_status", "value": "widow"})
    assert "deserted_years" not in d["profile"]


def test_documents_mentioned_in_the_story_are_pre_ticked():
    d = chat(lang="en", message="my husband died, I am 40 years old, I have Aadhaar", pending="marital_status")
    d = chat(lang="en", profile=d["profile"], answer={"slot": "assets_over_limit", "value": False})
    ready = {x["key"] for x in d["result"]["documents"] if x["ready"]}
    assert ready == {"aadhaar"}


@pytest.mark.parametrize("body", [
    {"message": "x" * 501}, {"lang": "fr"}, {"answer": {"slot": "age", "value": [1]}}, {"unknown": 1},
    {"answer": {"slot": "nope", "value": 1}}, {"profile": {"age": "forty"}},
])
def test_bad_requests_are_rejected(body):
    assert client.post("/api/chat", json=body).status_code == 422


def test_hostile_profile_values_are_discarded_not_trusted():
    d = chat(profile={"marital_status": "<script>", "age": 999, "docs_ready": ["../../etc/passwd"]})
    assert d["profile"] == {} and d["step"]["id"] == "situation"


def test_rate_limit():
    codes = [client.post("/api/chat", json={"start": True}).status_code for _ in range(95)]
    assert codes.count(429) >= 1


def test_tts_disabled_without_key():
    assert client.post("/api/tts", json={"text": "வணக்கம்"}).status_code == 503


def test_tts_returns_wav_when_gemini_answers(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test")
    monkeypatch.setattr(gemini_service, "synthesize", lambda text: gemini_service.pcm_to_wav(b"\x00\x00" * 100))
    r = client.post("/api/tts", json={"text": "வணக்கம்"})
    assert r.status_code == 200 and r.content[:4] == b"RIFF" and r.headers["content-type"] == "audio/wav"
