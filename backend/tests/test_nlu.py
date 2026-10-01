import pytest
from nlu import extract, parse_yes_no, tamil_number_words


@pytest.mark.parametrize("text,value", [
    ("முப்பத்தெட்டு", 38), ("நாற்பத்தி ஐந்து", 45), ("ஐம்பத்து மூன்று", 53), ("முப்பத்தொன்பது", 39),
    ("இருபத்திரண்டு", 22), ("அறுபத்தாறு", 66), ("முப்பது", 30), ("ஆறு", 6), ("பதினெட்டு", 18),
])
def test_tamil_number_words(text, value):
    assert tamil_number_words(text) == value


def test_tamil_script_story():
    r = extract("எனக்கு 38 வயது. என் கணவர் 6 வருடமாக என்னை விட்டுப் போய்ட்டார். ஆதார் இருக்கு")
    assert (r["marital_status"], r["age"], r["deserted_years"]) == ("deserted", 38, 6)
    assert r["docs_ready"] == ["aadhaar"]


def test_english_story_age_not_confused_with_years():
    r = extract("I am a woman, 38 years old. My husband left me 6 years ago. I have Aadhaar and bank passbook.")
    assert (r["age"], r["deserted_years"]) == (38, 6)
    assert set(r["docs_ready"]) == {"aadhaar", "bank_passbook"}


@pytest.mark.parametrize("text,status", [
    ("என் கணவர் இறந்துவிட்டார்", "widow"), ("my husband died last year", "widow"), ("kanavar iranthutar", "widow"),
    ("எனக்கு திருமணம் ஆகவில்லை", "unmarried"), ("I am unmarried", "unmarried"),
    ("விவாகரத்து ஆகிவிட்டது", "divorced"), ("I have a court separation order", "divorced"),
    ("கணவர் என்னை விட்டுப் பிரிந்துவிட்டார்", "deserted"), ("my husband left me", "deserted"),
])
def test_marital_status(text, status):
    assert extract(text)["marital_status"] == status


def test_unmarried_not_mistaken_for_married():
    assert extract("I am not married")["marital_status"] == "unmarried"


def test_bare_answers_use_the_pending_question():
    assert extract("38", pending="age")["age"] == 38
    assert extract("முப்பத்தெட்டு", pending="age")["age"] == 38
    assert extract("6", pending="deserted_years")["deserted_years"] == 6
    assert extract("ஆறு", pending="deserted_years")["deserted_years"] == 6
    assert extract("ஆம்", pending="assets_over_limit")["assets_over_limit"] is True
    assert extract("இல்லை", pending="assets_over_limit")["assets_over_limit"] is False
    assert extract("no", pending="assets_over_limit")["assets_over_limit"] is False


def test_bare_number_ignored_without_pending_question():
    assert extract("38") == {}


def test_negated_document_is_not_ticked():
    assert "aadhaar" not in extract("I don't have Aadhaar").get("docs_ready", [])


def test_no_property_statement_without_pending():
    assert extract("எனக்கு சொத்து எதுவும் இல்லை")["assets_over_limit"] is False


def test_tamil_digits():
    assert extract("எனக்கு ௪௦ வயது")["age"] == 40


def test_yes_no_none():
    assert parse_yes_no("maybe") is None
