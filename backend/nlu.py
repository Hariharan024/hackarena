"""Deterministic language understanding for Tamil (script + Tanglish) and English.

It is the first line: fast, free, works offline. Gemini is only asked when this finds nothing.
"""
import re
import unicodedata
from typing import Any, Dict, List, Optional

TAMIL_DIGITS = str.maketrans("௦௧௨௩௪௫௬௭௮௯", "0123456789")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "").translate(TAMIL_DIGITS)
    return re.sub(r"\s+", " ", text).strip().lower()


# ---------------------------------------------------------------- Tamil number words
BASIC = {
    "ஒன்று": 1, "ஒன்னு": 1, "ஒண்ணு": 1, "இரண்டு": 2, "ரெண்டு": 2, "மூன்று": 3, "மூணு": 3,
    "நான்கு": 4, "நாலு": 4, "ஐந்து": 5, "அஞ்சு": 5, "ஆறு": 6, "ஏழு": 7, "எட்டு": 8,
    "ஒன்பது": 9, "ஒம்பது": 9, "பத்து": 10, "பதினொன்று": 11, "பன்னிரண்டு": 12,
    "பதின்மூன்று": 13, "பதிமூன்று": 13, "பதினான்கு": 14, "பதினைந்து": 15, "பதினாறு": 16,
    "பதினேழு": 17, "பதினெட்டு": 18, "பத்தொன்பது": 19, "இருபது": 20, "முப்பது": 30,
    "நாற்பது": 40, "நாப்பது": 40, "ஐம்பது": 50, "அம்பது": 50, "அறுபது": 60, "எழுபது": 70,
    "எண்பது": 80, "தொண்ணூறு": 90, "நூறு": 100,
}
TENS_STEMS = {
    "இருபத்": 20, "முப்பத்": 30, "நாற்பத்": 40, "நாப்பத்": 40, "ஐம்பத்": 50, "அம்பத்": 50,
    "அறுபத்": 60, "எழுபத்": 70, "எண்பத்": 80, "தொண்ணூற்": 90,
}
UNIT_PATTERNS = [  # order matters: 9 before 1 (ஒன்பது vs ஒன்று)
    (r"ஒன்பது|தொன்பது", 9), (r"ஒன்று|தொன்று|ஒன்னு|ஒண்ணு", 1), (r"இரண்டு|திரண்டு|ரெண்டு", 2),
    (r"மூன்று|மூணு", 3), (r"நான்கு|நாலு", 4), (r"ஐந்து|தைந்து|அஞ்சு", 5), (r"ஆறு|தாறு", 6),
    (r"ஏழு|தேழு", 7), (r"எட்டு|தெட்டு", 8),
]
CONNECTORS = {"தி", "து", "த்து", "த்தி", ""}


def _unit(fragment: str) -> Optional[int]:
    for pattern, value in UNIT_PATTERNS:
        if re.search(pattern, fragment):
            return value
    return None


def tamil_number_words(text: str) -> Optional[int]:
    """'முப்பத்தெட்டு' -> 38, 'நாற்பத்தி ஐந்து' -> 45, 'ஆறு' -> 6. None if no number word."""
    tokens = text.split()
    for i, tok in enumerate(tokens):
        if tok in BASIC:
            return BASIC[tok]
        for stem, tens in TENS_STEMS.items():
            if tok.startswith(stem):
                rest = tok[len(stem):]
                if rest in CONNECTORS:
                    nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
                    unit = _unit(nxt) if nxt in BASIC or _unit(nxt) else None
                    return tens + (unit or 0)
                unit = _unit(rest)
                return tens + (unit or 0)
    return None


# ---------------------------------------------------------------- yes / no
NO_WORDS = ["இல்லை", "இல்ல", "இல்லீங்க", "இல்லைங்க", "கிடையாது", "இல்லாமல்", "illa", "illai", "illa", "kidayathu",
            "no ", "no.", "nope", "don't", "dont", "do not", "not ", "none", "without"]
YES_WORDS = ["ஆம்", "ஆமா", "ஆமாம்", "ஆமாங்க", "உண்டு", "இருக்கு", "இருக்கிறது", "இருக்குங்க", "உள்ளது",
             "aama", "aamam", "irukku", "undu", "yes", "yeah", "yep", "have", "i do"]


def parse_yes_no(t: str) -> Optional[bool]:
    padded = f" {t} "
    if any(w in padded for w in NO_WORDS) or t in {"no", "இல்லை"}:
        return False
    if any(w in padded for w in YES_WORDS):
        return True
    return None


# ---------------------------------------------------------------- facts
MARITAL_RULES = [  # order matters
    ("unmarried", ["திருமணம் ஆகவில்லை", "திருமணமாகவில்லை", "திருமணம் செய்யவில்லை", "கல்யாணம் ஆகவில்லை", "கல்யாணம் ஆகல",
                   "திருமணமாகாத", "கன்னி", "unmarried", "never married", "not married", "single woman", "i am single",
                   "thirumanam aagala", "kalyanam aagala", "thirumanam aagavillai"]),
    ("widow", ["விதவை", "கணவர் இறந்", "கணவன் இறந்", "கணவர் காலமான", "கணவர் மறைந்", "கணவனை இழந்", "கணவரை இழந்",
               "புருஷன் செத்", "வீட்டுக்காரர் இறந்", "widow", "husband died", "husband passed", "husband is dead",
               "lost my husband", "kanavar iranthu", "kanavar irandhu", "kanavar seththu", "vidhavai", "vithavai"]),
    ("divorced", ["விவாகரத்து", "நீதிமன்ற", "கோர்ட்", "divorce", "court separation", "legally separated", "court order",
                  "vivagarathu", "vivaharathu"]),
    ("deserted", ["விட்டுப் பிரிந்", "விட்டு பிரிந்", "விட்டுப் போய", "விட்டு போய", "விட்டுச் சென்", "விட்டு சென்", "கைவிட்ட",
                  "என்னை விட்டு", "பிரிந்து வாழ", "பிரிந்து", "ஓடிவிட்டார்", "கணவர் இல்லாமல்", "deserted", "abandoned",
                  "husband left", "left me", "separated", "not living with me", "ran away", "walked out",
                  "vittutu poitaru", "vittu poitaru", "pirinju", "pirinthu"]),
    ("married", ["கணவருடன் வாழ", "கணவரோட வாழ", "திருமணமாகி", "கணவர் இருக்கிறார்", "living with my husband",
                 "with my husband", "i am married", "married and"]),
]


def parse_marital(t: str) -> Optional[str]:
    for status, keywords in MARITAL_RULES:
        if any(k in t for k in keywords):
            return status
    return None


AGE_PATTERNS = [
    r"(\d{1,3})\s*(?:வயது|வயசு|வயதாகிறது|vayasu|vayas|years?\s*old|yrs?\s*old|yo\b)",
    r"(?:வயது|வயசு|age)\s*(?:is|:)?\s*(\d{1,3})",
    r"\b(?:i am|i'm|im)\s*(\d{1,3})\b(?!\s*(?:years?|yrs?)\s*(?:ago|since))",
    r"(?:enakku|enaku|naan)\s*(\d{1,3})",
]


def parse_age(t: str, pending: bool) -> Optional[int]:
    candidates: List[int] = []
    for pattern in AGE_PATTERNS:
        m = re.search(pattern, t)
        if m:
            candidates.append(int(m.group(1)))
            break
    if not candidates and re.search(r"வயது|வயசு|\bage\b|years old|vayasu", t):
        word = tamil_number_words(t)
        if word is not None:
            candidates.append(word)
    if not candidates and pending:
        m = re.search(r"\b(\d{1,3})\b", t)
        if m:
            candidates.append(int(m.group(1)))
        else:
            word = tamil_number_words(t)
            if word is not None:
                candidates.append(word)
    for age in candidates:
        if 10 <= age <= 110:
            return age
    return None


def parse_years(t: str, allowed: bool, pending: bool) -> Optional[int]:
    if not (allowed or pending):
        return None
    m = re.search(r"(\d{1,2})\s*(?:வருடம்|வருடமா|வருஷம்|வருசம்|ஆண்டு|வருட|(?:years?|yrs?)\b)(?!\s*old)", t)
    if m:
        value = int(m.group(1))
    elif pending and (m := re.search(r"\b(\d{1,2})\b", t)):
        value = int(m.group(1))
    elif pending or re.search(r"வருடம்|வருஷம்|ஆண்டு|years?", t):
        value = tamil_number_words(t)
    else:
        value = None
    return value if value is not None and 0 <= value <= 60 else None


DOC_KEYWORDS = {
    "aadhaar": ["ஆதார்", "aadhaar", "aadhar"],
    "bank_passbook": ["பாஸ்புக்", "வங்கி", "passbook", "bank book"],
    "address_proof": ["ரேஷன்", "குடும்ப அட்டை", "ration", "smart card", "address proof"],
    "death_certificate": ["இறப்புச் சான்று", "இறப்பு சான்று", "death certificate"],
    "court_order": ["நீதிமன்ற உத்தரவு", "court order"],
    "photo": ["புகைப்படம்", "photo"],
}
HAVE_MARKERS = ["இருக்கு", "இருக்கிறது", "உள்ளது", "உண்டு", "வைத்திருக்கிறேன்", "irukku", "vechiruken", "i have", "have my", "have a", "have the"]


def parse_documents(t: str) -> List[str]:
    found: List[str] = []
    for clause in re.split(r"[,.;]|\bbut\b|ஆனால்|ஆனா", t):
        if not any(h in clause for h in HAVE_MARKERS) or any(n in f" {clause} " for n in NO_WORDS):
            continue
        for key, words in DOC_KEYWORDS.items():
            if any(w in clause for w in words) and key not in found:
                found.append(key)
    return found


def extract(message: str, pending: Optional[str] = None, profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return only facts that were actually stated. `pending` is the slot Sakhi just asked about."""
    t = normalize(message)
    profile = profile or {}
    out: Dict[str, Any] = {}
    if not t:
        return out

    status = parse_marital(t)
    if status:
        out["marital_status"] = status

    age = parse_age(t, pending == "age")
    if age is not None:
        out["age"] = age

    status_now = out.get("marital_status") or profile.get("marital_status")
    years = parse_years(t, status_now == "deserted", pending == "deserted_years")
    if years is not None and years != out.get("age"):
        out["deserted_years"] = years
    elif years is not None and pending == "deserted_years":
        out["deserted_years"] = years

    if pending == "assets_over_limit":
        yn = parse_yes_no(t)
        if yn is not None:
            out["assets_over_limit"] = yn
    elif re.search(r"சொத்து|நிலம்|property|\bland\b", t):
        yn = parse_yes_no(t)
        if yn is False:  # only trust a clear "I have none" outside the direct question
            out["assets_over_limit"] = False

    docs = parse_documents(t)
    if docs:
        out["docs_ready"] = docs
    return out
